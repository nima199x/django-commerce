from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ProfileUpdateForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


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
    messages.success(request, "شما با موفقیت خارج شدید.")
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