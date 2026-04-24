from django.db import models

from user.models import CompanyProfile, StaffProfile
from book.constants import COMPANY_STATUS


class Place(models.Model):
    place = models.CharField('Place', max_length=100)
    long = models.CharField('Longitude', max_length=50)
    lat = models.CharField('Latitude', max_length=50)

    def __str__(self):
        return self.place


class Company(models.Model):
    code = models.CharField(max_length=4,  unique=True)
    userid = models.OneToOneField(CompanyProfile, on_delete=models.CASCADE, null=True)
    company = models.CharField(max_length=100)
    company_initials = models.CharField(max_length=3, unique=True)
    address = models.CharField(max_length=250)
    email = models.EmailField()
    seat_selection = models.CharField(max_length=9, choices=COMPANY_STATUS, default='Random')
    contact_1 = models.CharField('Contact 1', max_length=20)
    contact_2 = models.CharField('Contact 2', max_length=20, blank=True)
    contact_3 = models.CharField('Contact 3', max_length=20, blank=True)
    contact_4 = models.CharField('Contact 4', max_length=20, blank=True)

    def __str__(self):
        return self.company


class Driver(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    first_name = models.CharField('First Name', max_length=50)
    last_name = models.CharField('Last Name', max_length=50)
    address = models.CharField(max_length=100)
    phone_1 = models.CharField('Phone 1', max_length=20)
    phone_2 = models.CharField('Phone 2', max_length=20, blank=True, null=True)

    userid = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


