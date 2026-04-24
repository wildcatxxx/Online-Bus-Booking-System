import secrets
from datetime import date, time
from io import BytesIO

import qrcode
from PIL import ImageDraw, Image
from django.core.files import File
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from company.models import Company, Place, Driver
from user.models import ClientProfile
from .paystack import PayStack
from .constants import TIME_SESSIONS, BOOKING_STATUS, PAYMENT_TYPES


# Create your models here.
class Destination(models.Model):
    D_from = models.ForeignKey(Place, verbose_name='Destination From', on_delete=models.CASCADE, related_name='From')
    D_to = models.ForeignKey(Place, verbose_name='Destination To', on_delete=models.CASCADE, related_name='To')

    def __str__(self):
        return f"{self.D_from} To {self.D_to}"


class Bus(models.Model):
    company = models.ForeignKey(Company, verbose_name='Company', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.CharField('Bus Brand', max_length=25)
    model = models.CharField('Bus Model', max_length=15)
    plate_No = models.CharField('Plate No.', max_length=15, unique=True)
    capacity = models.PositiveIntegerField('Capacity')
    description = models.CharField('Description', max_length=250)
    image = models.ImageField(blank=False, upload_to='images/')

    available = models.BooleanField(default=True)
    seats_Sold = models.PositiveIntegerField(default=0)
    available_Seat = models.PositiveIntegerField(default=0)

    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, blank=True, null=True)
    price = models.FloatField(default=0)

    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, blank=True, null=True)
    departure_Date = models.DateField(blank=True, default=timezone.now)
    departure_Time = models.TimeField(blank=True, default='00:00:00')
    time_Session = models.CharField(choices=TIME_SESSIONS, max_length=10, default='Morning')

    def __str__(self):
        return self.plate_No


class Seat(models.Model):

    class Meta:
        verbose_name_plural = "Seat"
    number = models.PositiveIntegerField()

    def __str__(self):
        return str(self.number)


class Book(models.Model):
    book_Date = models.DateField(auto_now_add=True)
    book_Time = models.TimeField(auto_now_add=True)

    client = models.ForeignKey(ClientProfile, verbose_name='Client', on_delete=models.CASCADE)
    ticket_user = models.CharField(max_length=50, default='')

    company = models.ForeignKey(Company, verbose_name='Company', on_delete=models.CASCADE)
    seat = models.CharField(max_length=120)
    driver = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    amount = models.FloatField()
    destination = models.CharField(max_length=50)
    departure_Date = models.DateField()
    time_Session = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.client} {self.client}"


class Booking(models.Model):
    book_Date = models.DateField(auto_now_add=True)
    book_Time = models.TimeField(auto_now_add=True)

    client = models.ForeignKey(ClientProfile, verbose_name='Client', on_delete=models.CASCADE)
    ticket_user = models.CharField(max_length=50, default='')

    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    seat = models.CharField(max_length=120)
    driver = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True)
    amount = models.FloatField()
    destination = models.CharField(max_length=100)
    departure_Date = models.DateField()
    time_Session = models.CharField(max_length=10)
    qr_code = models.ImageField(upload_to='images/qr_codes/', blank=True)
    book_code = models.CharField(max_length=10, unique=True)

    status = models.CharField(max_length=15, choices=BOOKING_STATUS, default='Active')

    def __str__(self):
        return self.ticket_user

    def save(self, *args, **kwargs):
        qr_code_img = qrcode.make(self.book_code)
        canvas = Image.new('RGB', (290, 290), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qr_code_img)
        fname = f'qr_code-{self.book_code}.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)


class Payment(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.SET_NULL, null=True)
    book_Date = models.DateTimeField(auto_now_add=True)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True)

    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=200)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    payment_type = models.CharField(max_length=8, choices=PAYMENT_TYPES, default='MoMo')

    def __str__(self):
        return f'{self.bus.company}     Payment:{self.amount}'

    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            with_similar_ref = Payment.objects.filter(ref=ref)
            if not with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self) -> int:
        return self.amount * 100

    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
            self.save()
            if self.verified:
                return True
        return False


class Cancelled(models.Model):
    book_Date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    TP_cash = models.FloatField(default=0.00)

