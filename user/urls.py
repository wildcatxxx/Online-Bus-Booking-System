from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.log_in, name='login'),
    path('logout/', views.logout_func, name='logout'),
    path('add', views.company_signup, name='companysignup'),
    path('signup/', views.signup, name='sign-up'),
    path('password/', views.user_password, name='user_password'),
    path('reset password/', views.forgot_password, name='reset_password'),
    path('userdatainfo/', views.client_account, name='client_info'),
    path('change info/', views.client_update, name='client_info_update'),

    #path('companylogin/', views.company_login, name='companylogin'),
    #path('company_control/', views.company_control, name='company_control'),
    #path('add_terminal/', views.add_terminal, name='add_terminal'),
    #path('terminal_control/', views.terminal_control, name='terminal_control'),
    #path('terminallogin/', views.terminal_login, name='terminallogin'),

]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)