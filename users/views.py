from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ProfileUpdateForm
from eshop_online.rate_limit import rate_limit
from eshop_online.captcha import generate_captcha, verify_captcha


@rate_limit('register', limit=3, period=3600, redirect_to='register')
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        captcha_answer = request.POST.get('captcha_answer', '')

        if not verify_captcha(request, captcha_answer):
            messages.error(request, 'Incorrect answer to the verification question. Please try again.')
            captcha_question = generate_captcha(request)
            return render(request, 'users/register.html', {'form': form, 'captcha_question': captcha_question})

        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RegisterForm()

    captcha_question = generate_captcha(request)
    return render(request, 'users/register.html', {'form': form, 'captcha_question': captcha_question})


def merge_guest_cart(request, user):
    from products.models import Cart, CartItem

    session_key = request.session.session_key
    if not session_key:
        return

    guest_cart = Cart.objects.filter(session_key=session_key, user=None).first()
    if not guest_cart:
        return

    user_cart, created = Cart.objects.get_or_create(user=user)

    for item in guest_cart.items.all():
        existing_item = CartItem.objects.filter(cart=user_cart, product=item.product).first()
        if existing_item:
            existing_item.quantity += item.quantity
            existing_item.save()
        else:
            item.cart = user_cart
            item.save()

    guest_cart.delete()


@rate_limit('login', limit=5, period=300, redirect_to='login')
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                merge_guest_cart(request, user)
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})