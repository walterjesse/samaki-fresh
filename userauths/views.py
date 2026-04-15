from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit

from userauths import models as userauths_models
from userauths import forms as userauths_forms
from vendor import models as vendor_models


def register_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"You are already logged in")
        return redirect('/')

    form = userauths_forms.UserRegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = None
            try:
                user = form.save(commit=False)
                user.email = form.cleaned_data.get('email')
                user.username = form.cleaned_data.get('email').split('@')[0]
                user.set_password(form.cleaned_data.get('password1'))
                user.save()

                full_name = form.cleaned_data.get('full_name')
                mobile = form.cleaned_data.get('mobile')
                user_type = form.cleaned_data.get('user_type')

                profile = userauths_models.Profile.objects.create(
                    full_name=full_name,
                    mobile=mobile,
                    user=user,
                    user_type=user_type
                )

                user_authenticate = authenticate(request, email=user.email, password=form.cleaned_data.get('password1'))
                login(request, user_authenticate)

                messages.success(request, f"Account was created successfully.")
                next_url = request.GET.get("next", 'store:index')
                return redirect(next_url)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                if user:
                    user.delete()
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    context = {
        'form': form
    }
    return render(request, 'userauths/sign-up.html', context)

@ratelimit(key='ip', rate='5/h', method='POST')
def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('store:index')
    
    if request.method == 'POST':
        form = userauths_forms.LoginForm(request.POST)  
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user_instance = userauths_models.User.objects.get(email=email, is_active=True)
                user_authenticate = authenticate(request, email=email, password=password)

                if user_authenticate is not None:
                    login(request, user_authenticate)
                    messages.success(request, "You are Logged In")
                    next_url = request.GET.get("next", 'store:index')

                    print("next_url ========", next_url)
                    if next_url == '/undefined/':
                        return redirect('store:index')

                    if next_url == 'undefined':
                        return redirect('store:index')

                    if next_url is None or not next_url.startswith('/'):
                        return redirect('store:index')

                    return redirect(next_url)

                else:
                    messages.error(request, 'Invalid email or password')
            except userauths_models.User.DoesNotExist:
                messages.error(request, 'User does not exist')

    else:
        form = userauths_forms.LoginForm()  

    return render(request, "userauths/sign-in.html", {'form': form})

def logout_view(request):
    if "cart_id" in request.session:
        cart_id = request.session['cart_id']
    else:
        cart_id = None
    logout(request)
    request.session['cart_id'] = cart_id
    messages.success(request, 'You have been logged out.')
    return redirect("userauths:sign-in")

def handler404(request, exception, *args, **kwargs):
    context = {}
    response = render(request, 'userauths/404.html', context)
    response.status_code = 404
    return response

def handler500(request, *args, **kwargs):
    context = {}
    response = render(request, 'userauths/500.html', context)
    response.status_code = 500
    return response


def shop_owner_login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('vendor:dashboard')

    if request.method == 'POST':
        form = userauths_forms.LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user_instance = userauths_models.User.objects.get(email=email, is_active=True)
                user_authenticate = authenticate(request, email=email, password=password)
                if user_authenticate is not None:
                    # Allow superuser or Shop Owner to login
                    if user_authenticate.is_superuser or user_authenticate.profile.user_type == "Shop Owner":
                        login(request, user_authenticate)
                        messages.success(request, f"Welcome back, {user_authenticate.profile.full_name}!")
                        return redirect('vendor:dashboard')
                    else:
                        messages.error(request, "This account is not a Shop Owner account. Please use the regular login.")
                else:
                    messages.error(request, "Invalid email or password")
            except userauths_models.User.DoesNotExist:
                messages.error(request, "User does not exist")
    else:
        form = userauths_forms.LoginForm()

    context = {
        'form': form
    }
    return render(request, 'userauths/shop-owner-sign-in.html', context)
