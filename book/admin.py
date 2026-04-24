from django.contrib import admin
from book.models import Destination, Bus, Book, Booking, Seat, Payment

# Register your models here.
admin.site.register(Destination)
admin.site.register(Bus)
admin.site.register(Book)
admin.site.register(Payment)

admin.site.register(Booking)
admin.site.register(Seat)

