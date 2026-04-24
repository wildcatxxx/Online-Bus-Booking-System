import secrets

from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    userid = models.CharField(max_length=10)
    image = models.ImageField(blank=True, upload_to=f'images/users/', default='images/users/user.png')
    user_type = models.CharField(max_length=25)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs) -> None:
        while not self.userid:
            get_four = get_random_string(10).upper()
            with_similar = CompanyProfile.objects.filter(userid=get_four)
            if not with_similar:
                self.userid = get_four
        self.user_type = 'CompanyAdmin'
        super().save(*args, **kwargs)


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to='images/users/')
    userid = models.CharField(max_length=10)
    user_type = models.CharField(max_length=25)

    def __str__(self):
        return self.user.username


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    userid = models.CharField(max_length=10)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(blank=True, max_length=150)
    city = models.CharField(blank=True, max_length=20)
    image = models.ImageField(blank=True, upload_to='images/users/')

    emergency_contact_name = models.CharField(max_length=50, null=True)
    emergency_contact_phone = models.CharField(max_length=20)

    user_type = models.CharField(max_length=25, )

    def save(self, *args, **kwargs) -> None:
        while not self.userid:
            get_four = get_random_string(10).upper()
            with_similar = ClientProfile.objects.filter(userid=get_four)
            if not with_similar:
                self.userid = get_four
        self.user_type = 'Customer'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def image_tag(self):
        return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))

    image_tag.short_description = 'Images'
