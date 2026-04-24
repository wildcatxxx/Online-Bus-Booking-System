from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.utils.crypto import get_random_string
from book.forms import DestinationForm
from book.models import Bus, Booking, Destination
from book.templatetags.myapptags import url, get_company_user, get_company
from company.forms import CompanyForm, DriverForm, PlaceForm
from company.models import Company, Driver, Place
from user.models import CompanyProfile


@login_required(login_url='/login')  # Check login
def panel(request):
    user = request.user

    if user.is_superuser is True:
        return render(request, 'company/panel.html')
    else:

        get_user_id = get_company_user(request)
        getCompany = get_company(request)
        print(f'user_id {get_user_id}')
        company = Company.objects.filter(userid_id=get_user_id.id)
        buses = Bus.objects.filter(company=getCompany.id)
        drivers = Driver.objects.filter(company=getCompany.id)
        bookings = Booking.objects.filter(company=getCompany.id)

        print(f'company {company}')
        # res = Reservation.objects.filter(bookDate__lte=date.today())
        #print(f"{user}: access granted")
        return render(request, 'company/panel.html', {
                        'buses': buses,
                        'drivers': drivers,
                        'companies': company,
                        'User': get_user_id.user_id,
                        'res': bookings,
                    })


@login_required(login_url='/login')  # Check login
def add_company(request):
    if request.method == "POST":
        company_form = CompanyForm(request.POST, request.FILES)
        if company_form.is_valid():
            new_company = company_form.save(commit=False)  # create new company
            while new_company.code == "":
                get_four = get_random_string(4).upper()
                check_code = Company.objects.filter(code__icontains=get_four)
                if not check_code:
                    new_company.code = f'{new_company.company_initials}-{get_four}'
            new_company.save()  # create new company

            return render(request, 'company/company_details.html', {
                'company': new_company
            })
        else:
            messages.warning(request, company_form.errors)
            return HttpResponseRedirect(url(request))
    else:
        company_form = CompanyForm()
    return render(request, 'company/add_company.html', {
        'company_form': company_form
    })


@login_required(login_url='/login')
def company_details(request, id):
    company = get_object_or_404(Company, id=id)
    return render(request, 'company/company_details.html', {
        'company': company
    })


@login_required(login_url='/login')
def companies_view(request):
    companies = Company.objects.all()

    context = {'companies': companies,
               }
    return render(request, 'company/companies.html', context)


@login_required(login_url='/login')
def update_company(request, id):
    company = get_object_or_404(Company, id=id)
    if request.method == "POST":
        company_form = CompanyForm(request.POST, instance=company)
        if company_form.is_valid():
            company_update = company_form.save(commit=False)
            while company_update.code == "":
                get_four = get_random_string(4).upper()
                with_similar = Company.objects.filter(code__icontains=get_four)
                if not with_similar:
                    company_update.code = f'{company_update.company_initials}-{get_four}'
            company_update.save()
            return HttpResponseRedirect('/company')
        else:
            messages.warning(request, company_form.errors)
            return HttpResponseRedirect(url(request))
    else:
        company_form = CompanyForm(instance=company)
    return render(request, 'company/add_company.html', {
        'company_form': company_form
    })


# Buses of Company
@login_required(login_url='/login')
def buses_view(request):
    getCompany = get_company(request)
    buses = Bus.objects.filter(company=getCompany.id)
    context = {
        'buses': buses,
               }
    return render(request, 'company/bus/buses.html', context)


# Driver Functions Driver details, add driver, etc
@login_required(login_url='/login')
def drivers_view(request):
    getCompany = get_company(request)
    drivers = Driver.objects.filter(company=getCompany.id)
    context = {
        'drivers': drivers,
               }
    return render(request, 'company/driver/drivers.html', context)


@login_required(login_url='/login')
def driver_details(request, id):
    driver = get_object_or_404(Driver, id=id)
    return render(request, 'company/driver/driver_details.html', {
        'driver': driver
    })


@login_required(login_url='/login')
def add_driver(request):
    if request.method == "POST":
        form_var = DriverForm(request.POST, request.FILES)
        if form_var.is_valid():
            new_driver = form_var.save(commit=False)  # create nawBus
            user = request.user
            geti = CompanyProfile.objects.get(user=user)
            company = Company.objects.get(userid_id=geti.id)
            new_driver.company_id = company.id
            new_driver.save()  # create nawBus
            return HttpResponseRedirect('/company/panel/drivers')
        else:
            messages.warning(request, form_var.errors)
            return HttpResponseRedirect(url(request))
    else:
        form_var = DriverForm()
    return render(request, 'company/driver/add_driver.html', {
        'formdriver': form_var
    })


@login_required(login_url='/login')
def edit_driver(request, id):
    driver = get_object_or_404(Driver, id=id)
    if request.method == "POST":
        form_var = DriverForm(request.POST, instance=driver)
        if form_var.is_valid():
            update_driver = form_var.save(commit=False)
            update_driver.save()
            return HttpResponseRedirect('/company/pane/drivers')
        else:
            messages.warning(request, form_var.errors)
            return HttpResponseRedirect(url(request))
    else:
        form_var = DriverForm(instance=driver)
    return render(request, 'company/driver/add_driver.html', {'formdriver': form_var, 'edit': driver})


@login_required(login_url='/login')
def delete_driver(request, id):
    driver = get_object_or_404(Driver, id=id)
    driver.delete(request.FILES)
    return HttpResponseRedirect("/company/panel/drivers")


@login_required(login_url='/login')
# Place Functions Place details, add Place, etc
def add_place(request):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        form_var = PlaceForm(request.POST, request.FILES)
        if form_var.is_valid():
            new_place = form_var.save(commit=False)  # create nawBus
            place = Place.objects.filter(place=new_place.place)
            print(f' new place:{new_place} place: place')
            if place:
                messages.error(request, "Place Already Exits")
                return HttpResponseRedirect(url)
            else:
                new_place.save()  # create nawBus
                return HttpResponseRedirect('/company/panel/places')
        else:
            messages.warning(request, form_var.errors)
            return HttpResponseRedirect(url(request))
    else:
        form_var = PlaceForm()
    return render(request, 'company/place/add_place.html', {
        'formplace': form_var
    })


@login_required(login_url='/login')
def edit_place(request,id):
    place = get_object_or_404(Place, id=id)
    if request.method == "POST":
        form_var = PlaceForm(request.POST, instance=place)
        if form_var.is_valid():
            update_place = form_var.save(commit=False)
            place_up = Place.objects.filter(place=update_place.place)
            if place_up.count >= 2:
                messages.error(request, "Place Already Exits")
                return HttpResponseRedirect(url(request))
            else:
                update_place.save()
                return render(request, 'company/place/places.html', {
                    'places': update_place
                })
        else:
            messages.warning(request, form_var.errors)
            return HttpResponseRedirect(url(request))
    else:
        form_var = PlaceForm(instance=place)
    return render(request, 'company/place/add_place.html', {'formplace': form_var, 'edit': place})


@login_required(login_url='/login')
def places_view(request):
    places = Place.objects.all()
    context = {'y': places,
               }
    return render(request, 'company/place/places.html', context)


# Destinations Functions Place details, add Place, etc
@login_required(login_url='/login')
def destination_view(request):
    destinations = Destination.objects.all()
    context = {
        'destinations': destinations,
               }
    return render(request, 'company/destination/destinations.html', context)


@login_required(login_url='/login')
def add_destination(request):
    if request.method == "POST":
        form_destination = DestinationForm(request.POST, request.FILES)
        if form_destination.is_valid():
            new_destination = form_destination.save(commit=False)  # create nawBus
            newdestination1 = new_destination.D_from
            newdestination2 = new_destination.D_to

            get_chk = Destination.objects.filter(D_from_id=newdestination1, D_to_id=newdestination2)
            print(f" all {get_chk} ")

            if newdestination1 == newdestination2:
                messages.error(request, "Travel Destinations are same")
                HttpResponseRedirect(url(request))
            elif get_chk:
                messages.error(request, "Travel Destinations Already Exist")
                HttpResponseRedirect(url(request))
            else:
                new_destination.save()  # create nawBus
                return HttpResponseRedirect("/company/panel/destinations")
        else:
            messages.warning(request, form_destination.errors)
            return HttpResponseRedirect(url(request))
    else:
        form_destination = DestinationForm()
    return render(request, 'company/destination/add_destination.html', {
        'formjourney': form_destination
    })


@login_required(login_url='/login')
def edit_destination(request, id):
    destination = get_object_or_404(Destination, id=id)

    if request.method == "POST":
        form_destination = DestinationForm(request.POST, instance=destination)
        if form_destination.is_valid():
            update_destination = form_destination.save(commit=False)
            update_destination.save()
            return HttpResponseRedirect("/company/panel/destinations")
        else:
            messages.warning(request, form_destination.errors)
            return HttpResponseRedirect(url(request))
    else:
        form_destination = DestinationForm(instance=destination)
    return render(request, 'company/destination/add_destination.html', {'formjourney': form_destination, 'edit': destination})

