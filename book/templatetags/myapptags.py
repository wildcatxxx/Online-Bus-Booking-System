from datetime import date, datetime, timedelta

from django import template
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse

from book.models import Cancelled, Booking
from company.models import Company
from user.models import CompanyProfile, ClientProfile

register = template.Library()


@register.simple_tag
def general_user(request):
    user = request.user
    return user


@register.simple_tag
def get_company(request):
    getuser = CompanyProfile.objects.get(user=general_user(request))
    company = Company.objects.get(userid_id=getuser.id)
    print(f'User name: {getuser} - Company id-{company}')
    return company


@register.simple_tag
def get_company_user(request):
    user = request.user
    if not user.is_anonymous and CompanyProfile.objects.filter(user=request.user):
        profile = CompanyProfile.objects.get(user=general_user(request))
        return profile


@register.simple_tag
def get_client_user(request):
    user = request.user
    if not user.is_anonymous and ClientProfile.objects.filter(user=request.user):
        profile = ClientProfile.objects.get(user=general_user(request))
        return profile


@register.simple_tag
def bookings_validation(request):
    expiry = timedelta(days=2)
    today = date.today()
    todays = today.strftime("%d/%m/%Y")
    print(f'today is {todays}')
    use = timedelta(days=1)
    bookings = Booking.objects.filter(status="Active")
    for book in bookings:
        expired = book.departure_Date + expiry
        in_use = book.departure_Date + use
        if todays == book.departure_Date or todays == in_use:
            book.status = "In-use"
            book.save()
        elif todays == expired:
            book.status = "Expired"
            book.save()
    return 0


@register.simple_tag
def user_iid(user):
    count = CompanyProfile.objects.filter(user=user)
    if count:
        counts = CompanyProfile.objects.get(user=user)
        count = counts.id
    print(count)
    return count


@register.simple_tag
def tp_cash(request):
    if ClientProfile.objects.filter(user=request.user):
        user = ClientProfile.objects.get(user=request.user)
        user_cash = Cancelled.objects.filter(client=user)

        if user_cash:
            tp_cash = Cancelled.objects.get(client=user)
            cash = tp_cash.TP_cash
            return cash
        else:
            cash = 0.00
            return cash


@register.simple_tag
def update_company(request):
    if CompanyProfile.objects.filter(user=request.user):
        company = get_company(request) and get_company(request).code == ""
        return company


@register.simple_tag
def filter_company(request):
    filter_com = Company.objects.filter(userid_id=get_company_user(request).id)
    return filter_com


@register.simple_tag
def todays_date(request):
    Ddate = date.today()
    return Ddate


@register.simple_tag
def todays_time(request):
    Btime = datetime.now().time()
    return Btime


@register.simple_tag
def account(request):
    profile = CompanyProfile.objects.filter(user=general_user(request))
    if profile:
        user_ = CompanyProfile.objects.get(user=general_user(request))
        ini = Company.objects.get(userid_id=user_.id)

        return ini.company_initials


@register.simple_tag
def url(request):
    url = request.META.get('HTTP_REFERER')
    return url
