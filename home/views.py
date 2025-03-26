from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_staff

def home_view(request):
    return render(request, 'home/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        admin_login = request.POST.get('admin_login', False)
        
        user = authenticate(username=username, password=password)
        if user:
            if admin_login and not user.is_staff:
                messages.error(request, "This account is not an administrator account!")
                return render(request, 'home/login.html')
            auth_login(request, user)
            messages.success(request, "Successfully logged in!")
            if admin_login and user.is_staff:
                return redirect('/admin/')
            return redirect('home')
        messages.error(request, "Invalid credentials!")
    return render(request, 'home/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        confirm_password = request.POST['password2']

        if password != confirm_password:
            messages.error(request, "Passwords don't match!")
            return render(request, 'home/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'home/register.html')

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.save()
        messages.success(request, "Registration successful! Please login.")
        return redirect('login')
    return render(request, 'home/register.html')

def logout_view(request):
    auth_logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect('home')
