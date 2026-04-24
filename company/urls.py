from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from book import views
from . import views
urlpatterns = [
    path('', views.panel, name='panel'),
    path('panel/', views.panel, name='panel'),
    path('panel/place/add', views.add_place, name='add_place'),
    path('panel/places', views.places_view, name='places_view'),
    path('panel/places/454<int:id>dffdf', views.edit_place, name='place_edit'),

    path('add', views.add_company, name='add_company'),
    path('view', views.companies_view, name='company_view'),
    path('edit/<int:id>', views.update_company, name='edit_company'),

    path('panel/busesdetails/<int:id>', views.company_details, name='company_details'),
    path('panel/buses', views.buses_view, name='buses_view'),

    path('panel/destinations/new', views.add_destination, name='add_destination'),
    path('panel/destinations/edit/<int:id>', views.edit_destination, name='edit_destinations'),
    path('panel/destinations/', views.destination_view, name='destinations_view'),

    path('panel/driver/add', views.add_driver, name='driver'),
    path('panel/driver/edit/<int:id>', views.edit_driver, name='edit_driver'),
    path('panel/driver/delete/<int:id>', views.delete_driver, name='delete_driver'),
    path('panel/driver/<int:id>', views.driver_details, name='driver_details'),
    path('panel/drivers', views.drivers_view, name='drivers_view'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
