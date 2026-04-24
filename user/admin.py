from django.contrib import admin
from user.models import CompanyProfile,ClientProfile, StaffProfile


# Register your models here.
admin.site.register(CompanyProfile)
admin.site.register(StaffProfile)
admin.site.register(ClientProfile)
