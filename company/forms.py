from django import forms
from django.forms import TextInput, FileInput, Select

from company.models import Company, Driver, Place


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = (
        'company', 'company_initials', 'address', 'email', 'seat_selection', 'contact_1', 'contact_2', 'contact_3',
        'contact_4')

        widgets = {
            'company': TextInput(
                attrs={'class': 'input', 'placeholder': 'company name', 'pattern': '[A-Z a-z]+',
                       'title': 'Enter Letters', }),
            'company_initials': TextInput(
                attrs={'class': 'input', 'placeholder': 'company initials', 'maxlength': '3', 'minlength': '3',
                                      'pattern': '[A-Za-z.-]+', 'title': 'Enter Letters', }),
            'address': TextInput(
                attrs={'class': 'input', 'placeholder': 'address', 'pattern': '[0-9A-Z a-z-]*$',
                                        'title': 'Enter Letters with -', }),
            'seat_selection': Select(attrs={'class': 'input'}),

            'contact_1': TextInput(
                attrs={'class': 'input', 'placeholder': 'phone', 'maxlength': '10', 'minlength': '10',
                       'pattern': '[0-9]+', 'title': 'Enter Phone Number', }),
            'contact_2': TextInput(
                attrs={'class': 'input', 'placeholder': 'phone', 'maxlength': '10', 'minlength': '10',
                       'pattern': '[0-9]+', 'title': 'Enter Phone Number', }),
            'contact_3': TextInput(
                attrs={'class': 'input', 'placeholder': 'phone', 'maxlength': '10', 'minlength': '10',
                       'pattern': '[0-9]+', 'title': 'Enter Phone Number', }),
            'contact_4': TextInput(
                attrs={'class': 'input', 'placeholder': 'phone', 'maxlength': '10', 'minlength': '10',
                       'pattern': '[0-9]+', 'title': 'Enter Phone Number', }),

        }


class DriverForm(forms.ModelForm):

    class Meta:
        model = Driver
        fields = ('first_name', 'last_name', 'address', 'phone_1', 'phone_2')
        widgets = {
            'first_name': TextInput(
                attrs={'class': 'input', 'placeholder': 'first name', 'pattern': '[A-Za-z]+',
                       'title': 'Enter Letters', }),
            'last_name': TextInput(
                attrs={'class': 'input', 'placeholder': 'last name', 'pattern': '[A-Za-z]+',
                       'title': 'Enter Letters', }),
            'address': TextInput(attrs={'class': 'input', 'placeholder': 'address', 'pattern': '[0-9A-Z a-z-]*$',
                                        'title': 'Enter Letters with -', }),
            'image': FileInput(attrs={'class': 'input', 'placeholder': 'image', }),

            'phone_1': TextInput(
                attrs={'class': 'input', 'placeholder': 'phone', 'maxlength': '10', 'minlength': '10',
                       'pattern': '[0-9]+', 'title': 'Enter Phone Number', }),
            'phone_2': TextInput(
                attrs={'class': 'input', 'placeholder': 'phone', 'maxlength': '10', 'minlength': '10',
                       'pattern': '[0-9]+', 'title': 'Enter Phone Number', }),
        }


class PlaceForm(forms.ModelForm):

    class Meta:
        model = Place
        fields = ('place',)
        widgets = {
            'place': TextInput(
                attrs={'class': 'input', 'placeholder': 'place', 'pattern': '[A-Za-z]+',
                       'title': 'Enter Letters', }),
        }

