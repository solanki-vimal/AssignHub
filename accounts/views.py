from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid credentials")
            
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'student')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
        else:
            user = User.objects.create_user(username=email, email=email, password=password, role=role)
            user.first_name = full_name
            user.save()
            login(request, user)
            return redirect('accounts:dashboard_redirect')
            
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    role = request.user.role
    if role == 'admin':
        return redirect('dashboard:admin_dashboard')
    elif role == 'faculty':
        return redirect('dashboard:faculty_dashboard')
    else:
        return redirect('dashboard:student_dashboard')

def home_view(request):
    return render(request, 'home.html')
