from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.crypto import get_random_string
from twilio.rest import Client

from book.templatetags.myapptags import url, get_company, update_company
from company.models import Company
from online_booking.settings import ACCOUNT_SID, AUTH_TOKEN
from user.forms import SignUpForm, ClientsUpdateForm
from user.models import CompanyProfile, ClientProfile  # StaffProfile


def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        alt = CompanyProfile.objects.filter(user=user)
        print(f'alt User: {alt}')

        if user is not None:
            login(request, user)
            print(f'User: {user}')
            if user.is_superuser is True:
                return HttpResponseRedirect('/company/')
            else:
                profile = CompanyProfile.objects.filter(user=user)
                profile1 = ClientProfile.objects.filter(user=user)
                print(f'company {profile}, Client {profile1}')

                if profile:
                    company = get_company(request)
                    print(f'company {company}')

                    current_user = request.user
                    userprofile = CompanyProfile.objects.get(user_id=current_user.id)
                    request.session['userimage'] = userprofile.image.url
                    if update_company(request):
                        id = company.id
                        return HttpResponseRedirect(f'/company/edit/{id}')
                    else:
                        return HttpResponseRedirect('/company/')
                else:
                    current_user = request.user
                    userprofile = ClientProfile.objects.get(user_id=current_user.id)
                    request.session['userimage'] = userprofile.image.url
                    return HttpResponseRedirect('/')

        else:
            messages.warning(request,"Login Error !! Username or Password is incorrect")
            return HttpResponseRedirect('/login')
    # Return an 'invalid login' error message.

    #category = Category.objects.all()
    context = {#'category': category
     }
    return render(request, 'login_form.html',context)


@login_required(login_url='/login') # Check login
def company_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save() #completed sign up
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            # Create data in profile table for user
            logedin_user = request.user
            id_users = get_random_string(9).upper()
            data = CompanyProfile()
            data.user_id = user.id
            data.userid = id_users
            data.save()
            get=data.user_id
            print(f'prof id = {get}')

            mark = Company()
            mark.userid_id = data.id
            mark.save()

            messages.success(request, 'Your account has been created!')
            return HttpResponseRedirect('/company')
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect('add')

    com_form = SignUpForm()
    #category = Category.objects.all()
    context = {#'category': category,
               'com_form': com_form,
               }
    return render(request, 'company_signup_form.html', context)


def signup(request):
    if request.method == 'POST':
        client_form = SignUpForm(request.POST)
        client_update = ClientsUpdateForm(request.POST, request.FILES)

        if client_form.is_valid() and client_update.is_valid():
            client_form.save() #completed sign up
            data = client_update.save(commit=False)

            username = client_form.cleaned_data.get('username')
            password = client_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            # Create data in profile table for ClientProfile

            data.user_id = user.id
            while not data.image.url:
                data.image = 'images/users/user.png'
            data.email = client_form.cleaned_data.get('email')
            data = client_update
            data.save()

            messages.success(request, 'Your account has been created!')
            return HttpResponseRedirect('/')
        else:
            messages.warning(request, client_form.errors)
            messages.warning(request, client_update.errors)
            return HttpResponseRedirect(url(request))

    client_form = SignUpForm()
    client_update = ClientsUpdateForm()

    context = {
               'com_form': client_form,
                'up_form': client_update
               }
    return render(request, 'signup_form.html', context)


def logout_func(request):
    logout(request)
    return HttpResponseRedirect('/login')


@login_required(login_url='/login')  # Check login
def client_account(request):
    user = request.user
    data = ClientProfile.objects.get(user=user)
    return render(request, 'client_info.html', {'client': user, 'info': data})


@login_required(login_url='/login')  # Check login
def client_update(request):
    client = get_object_or_404(ClientProfile, user=request.user)
    if request.method == "POST":
        client_update = ClientsUpdateForm(request.POST,request.FILES, instance=client)
        if client_update.is_valid():
            company_update = client_update.save(commit=False)
            print(company_update)
            company_update.save()
            print(company_update.image.url)
            return HttpResponseRedirect('/user/userdatainfo')
        else:
            return HttpResponseRedirect(url(request))
    else:
        client_update = ClientsUpdateForm(instance=client)
        return render(request, 'client_update_form.html', {
            'up_form': client_update
        })


@login_required(login_url='/login')  # Check login
def user_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect('/user')
        else:
            messages.error(request, 'Please correct the error below.<br>'+ str(form.errors))
            return HttpResponseRedirect('/user/password')
    else:
        #category = Category.objects.all()
        form = PasswordChangeForm(request.user)
        return render(request, 'user_password.html', {'form': form, #'category': category
                       })


def forgot_password(request):
    initiated = True
    if request.method == 'POST':
        email = request.POST['email']

        user = User.objects.filter(email=email)
        if user:
            u = User.objects.get(email=email)
            new_password = get_random_string(8)
            u.set_password(new_password)
            u.save()

            #Password Reset
            username = u.username
            user_phone = ClientProfile.objects.get(user_id=u.id)

            client = Client(ACCOUNT_SID, AUTH_TOKEN)

            client.messages.create(
                body=f'Your request to reset your password was successful, You can Login with you Username: {username} and Your New Password: {new_password}, Thank You',
                from_='+12015786004',
                to= f'+233{user_phone.phone}',
            )
            return render(request, "forgot_password.html", {'initiated':initiated,})

    return render(request, "forgot_password.html")

'''
@login_required(login_url='superlogin') # Check login
def company_accounts(request):
    all_company = CompanyProfile.objects.all()

    context = {'all_company':all_company
    }
    return render(request, 'company_admin.html', context)


@login_required(login_url='/superlogin') # Check login
def add_company(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save() #completed sign up
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            # Create data in profile table for user
            logedin_user = request.user
            data = CompanyProfile()
            data.user_id = user.id
            data.image = "images/users/user.png"
            data.user_type = 'CompanyAdmin'
            data.save()
            messages.success(request, 'Your account has been created!')
            return HttpResponseRedirect('/company')
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect('/companysignup')


    form = SignUpForm()
    #category = Category.objects.all()
    context = {#'category': category,
               'form': form,
               }
    return render(request, 'company_signup_form.html', context)


@login_required(login_url='/companylogin') # Check login
def company_control(request):
    user = request.user
    print(f'user: {user}')

    userdata = get_object_or_404(CompanyProfile, user=user)
    if userdata.company_code is None or userdata.company_code == '':

        if request.method == 'POST':
            company_profile_form = CompanyProfileUpdateForm(request.POST, request.FILES,
                                                            instance=userdata)
            if company_profile_form.is_valid():
                userdata.company_code = get_random_string(5).upper()
                print(f'code = {userdata.company_code}')
                userdata.save()
                company_profile_form.save()
                messages.success(request, 'Your account has been updated!')
                return HttpResponseRedirect('/company_control')
        else:
            company_profile_form = CompanyProfileUpdateForm(
                instance=userdata)  # "userprofile" model -> OneToOneField relatinon with user

        context = {
            'company_profile_form': company_profile_form
        }
        return render(request, 'company_update_form.html', context)
    else:

        terminals = TerminalProfile.objects.filter()


        context = {'terminals': terminals
        }
        return render(request, 'terminal_company.html', context)


def company_login(request):
    if request.method == 'POST':
        fall = request.user
        print(f"session = {fall}")

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(f"user: {user}")
        print(f"username: {username}")

        if user is not None:
            login(request, user)
            userdata = get_object_or_404(CompanyProfile, user=user)
            print(f'user type : {userdata.user_type}')
            print(f'user type2 : {userdata.user}')

            if userdata.user_type == 'CompanyAdmin':
                print(f'code : {userdata.company_code}')
                return render(request,'terminal_company.html')
            else:
                messages.warning(request, "You are NOT authorised to access this page")
                return HttpResponseRedirect('/')
        else:
            messages.warning(request, "Login Error !! Username or Password is incorrect")
            return HttpResponseRedirect('/companylogin')
    # Return an 'invalid login' error message.

    #category = Category.objects.all()
    context = {#'category': category
     }
    return render(request, 'company_login_form.html', context)


@login_required(login_url='/companylogin') # Check login
def add_terminal(request):
    company_data = get_object_or_404(CompanyProfile, user=request.user)
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save() #completed sign up
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            print(f'user is {user}')
            # Create data in profile table for user
            data = TerminalProfile()
            data.user_id = user.id
            data.image = "images/users/user.png"
            data.company = company_data.company
            data.company_code = company_data.company_code
            data.user_type = 'TerminalAdmin'
            data.save()
            messages.success(request, 'Your account has been created!')
            return HttpResponseRedirect('/company_control')
        else:
            messages.warning(request,form.errors)
            return HttpResponseRedirect('/add_terminal')


    form = SignUpForm()
    #category = Category.objects.all()
    context = {#'category': category,
               'form': form,
               }
    return render(request, 'add_terminal_form.html', context)


def terminal_login(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(f"user: {user}")
        print(f"username: {username}")

        if user is not None:

            login(request, user)
            userdata = get_object_or_404(TerminalProfile, user=user)

            if userdata.user_type == 'TerminalAdmin':
                print(f'code : {userdata.company_code}')
                return render(request, 'terminal_control.html')
            else:
                messages.warning(request, "You are NOT authorised to access this page")
                return HttpResponseRedirect('/')

        else:
            messages.warning(request, "Login Error !! Username or Password is incorrect")
            return HttpResponseRedirect('/terminallogin')
    # Return an 'invalid login' error message.

    #category = Category.objects.all()
    context = {#'category': category
     }
    return render(request, 'terminal_login_form.html', context)


@login_required(login_url='terminallogin') # Check login
def terminal_control(request):
    user = request.user
    print(f'user: {user}')

    userdata = get_object_or_404(TerminalProfile, user=user)
    print(f'T Code: {userdata.terminal_code}')
    if userdata.terminal_code is None or userdata.terminal_code == '':

        if request.method == 'POST':
            terminal_profile_form = TerminalProfileUpdateForm(request.POST, request.FILES,
                                                            instance=userdata)
            if terminal_profile_form.is_valid():
                userdata.terminal_code = get_random_string(5).upper()
                print(f'code = {userdata.company_code}')
                userdata.save()
                terminal_profile_form.save()
                messages.success(request, 'Your account has been updated!')
                return HttpResponseRedirect('/terminal_control')
        else:
            terminal_profile_form = TerminalProfileUpdateForm(
                instance=userdata)  # "userprofile" model -> OneToOneField relatinon with user

        context = {
            'terminal_profile_form': terminal_profile_form
        }
        return render(request, 'terminal_update_form.html', context)
    else:

        staff = TerminalStaffProfile.objects.filter()

        context = {'staff': staff
                   }
        return render(request, 'terminal_control.html', context)


def logout_func(request):
    logout(request)
    return HttpResponseRedirect('/')

'''