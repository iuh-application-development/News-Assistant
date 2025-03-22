from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages

def home_view(request):
    return render(request, 'home/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, "Successfully logged in!")
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
