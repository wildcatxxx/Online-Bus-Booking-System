from django.contrib import admin

from company.models import Company, Place, Driver

# Register your models here.
admin.site.register(Company)
admin.site.register(Place)
admin.site.register(Driver)
