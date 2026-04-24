from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms import TextInput, FileInput, EmailInput, Select

from company.models import Place
from user.models import CompanyProfile, ClientProfile


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30, label='Username :', widget=forms.TextInput(
        attrs={'class': 'input', 'placeholder': 'username', 'pattern': '[0-9A-Za-z-_]+',
               'title': 'Enter Alphanumeric - _'}), )
    email = forms.EmailField(max_length=200, label='Email :', widget=forms.TextInput(
        attrs={'class': 'input', 'placeholder': 'email', }), )
    first_name = forms.CharField(max_length=50, label='First Name :', widget=forms.TextInput(
        attrs={'class': 'input', 'placeholder': 'first name', 'pattern': '[A-Za-z]+',
               'title': 'Enter Letters '}), )
    last_name = forms.CharField(max_length=50, label='Last Name :', widget=forms.TextInput(
        attrs={'class': 'input', 'placeholder': 'last name', 'pattern': '[A-Za-z]+', 'title': 'Enter Letters'}), )

    class Meta:
        model = User
        fields = ('username','first_name','last_name', 'email', 'password1', 'password2', )
        widgets = {
            'password1': TextInput(attrs={'class': 'input', 'placeholder': 'password', }),
            'password2': TextInput(attrs={'class': 'input', 'placeholder': 'confirm password', }),
        }


class AdminUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', 'email')
        widgets = {
            'first_name': TextInput(attrs={'class': 'input', 'placeholder': 'first name', 'pattern': '[A-Za-z]+',
                                      'title': 'Enter Letters', }),
            'last_name': TextInput(attrs={'class': 'input', 'placeholder': 'last name', 'pattern': '[A-Za-z]+',
                                      'title': 'Enter Letters', }),
            'email'     : EmailInput(attrs={'class': 'input','placeholder':'email'}),
        }


class CompanyProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ('image',)


place = Place.objects.all()
places = place.values_list('place')
CITY = []
for seat in places:
    put = seat + seat
    CITY.append(put)


class ClientsUpdateForm(forms.ModelForm):

    class Meta:
        model = ClientProfile
        fields = ('phone', 'address', 'city','image', 'emergency_contact_name', 'emergency_contact_phone')
        widgets = {
            'phone': TextInput(attrs={'class': 'input', 'placeholder': 'phone', 'maxlength': '10', 'minlength': '10',
                                      'pattern': '[0-9]+', 'title': 'Enter Phone Number', }),
            'address': TextInput(attrs={'class': 'input', 'placeholder': 'address', 'pattern': '[0-9A-Z a-z-]*$',
                                        'title': 'Enter Letters with -', }),
            'city': Select(attrs={'class': 'input', 'placeholder': 'city'}, choices=CITY),
            'image': FileInput(attrs={'class': 'input', 'placeholder': 'image', }),
            'emergency_contact_name': TextInput(
                attrs={'class': 'input', 'placeholder': 'Emergency Contact Name', 'pattern': '[A-Z a-z]+',
                       'title': 'Enter Letters', }),
            'emergency_contact_phone': TextInput(
                attrs={'class': 'input', 'placeholder': 'Emergency Contact Phone', 'maxlength': '10', 'minlength': '10',
                       'pattern': '[0-9]+', 'title': 'Enter Phone Number', }),

        }