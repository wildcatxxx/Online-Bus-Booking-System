from django import forms
from django.forms import TextInput, FileInput

from company.models import Driver
from .models import Bus, Destination, Book, Booking


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class DestinationForm(forms.ModelForm):

    class Meta:
        model = Destination
        fields = ('D_from', 'D_to')
        widgets = {
            'D_from': TextInput(attrs={'class': 'input', 'placeholder': 'from', 'pattern': '[A-Z a-z-]*$',
                                      'title': 'Enter Letters', }),
            'D_to': TextInput(attrs={'class': 'input', 'placeholder': 'to', 'pattern': '[A-Z a-z-]*$',
                                      'title': 'Enter Letters', }),
        }


class BusForm(forms.ModelForm):

    class Meta:
        model = Bus
        fields = ('brand', 'model', 'plate_No', 'capacity', 'description', 'image',
                  )
        widgets = {
            'brand': TextInput(attrs={'class': 'input', 'placeholder': 'phone', 'pattern': '[0-9A-Z a-z-]*$',
                                      'title': 'Enter Only Letters with -', }),
            'model': TextInput(attrs={'class': 'input', 'placeholder': 'phone', 'pattern': '[0-9A-Z a-z-]*$',
                                      'title': 'Enter Only Letters with -', }),
            'plate_No': TextInput(attrs={'class': 'input', 'placeholder': 'bus number', 'pattern': '[0-9A-Z a-z-]*$',
                                         'title': 'Enter Only Letters with -', }),
            'capacity': TextInput(
                attrs={'class': 'input', 'placeholder': 'capacity', 'maxlength': '2', 'pattern': '[0-9]+',
                       'title': 'Enter Only Numbers', }),
            'description': TextInput(attrs={'class': 'input', 'placeholder': 'phone', 'pattern': '[0-9A-Z ()a-z-]*$',
                                            'title': 'Enter Only Letters with -', }),
            'image': FileInput(attrs={'class': 'input', 'placeholder': 'image', }),
        }


class DepartureForm(forms.ModelForm):
    def __init__(self, company, *args, **kwargs):
        super(DepartureForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['driver'].queryset = Driver.objects.filter(company=company)

    class Meta:
        model = Bus
        fields = ('destination', 'price', 'driver', 'departure_Date', 'departure_Time', 'time_Session', )

        widgets = {
            'departure_Date': DateInput(),
            'departure_Time': TimeInput()
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = (
            'company', 'seat', 'driver', 'bus', 'destination', 'departure_Date', 'time_Session'
        )

