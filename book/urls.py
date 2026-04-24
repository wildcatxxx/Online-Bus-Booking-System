from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about us', views.about_us, name='about_us'),
    path('contact us', views.contact_us, name='contact_us'),

    path('addbus', views.add_bus, name='addbus'),
    path('edit_bus/<int:id>', views.edit_bus, name='edit_bus'),
    path('delete/<int:id>', views.delete_bus, name='delete_bus'),
    path('details/<int:id>', views.bus_details, name='bus_details'),
    path('change_departure/178<int:id>54', views.change_departure, name='change_departure'),
    path('search/', views.search, name='search'),

    path('new_destination/<int:id>/<str:ref>/', views.book_details, name='book_details_view'),
    path('Book Now/9685<int:id>85', views.book, name='book_now'),
    path('cancel ticket/<int:id>', views.cancel, name='cancellation'),
    path('userbookings', views.user_booking, name='user_books'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
