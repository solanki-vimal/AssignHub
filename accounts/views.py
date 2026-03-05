from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User
from dashboard.models import ActivityLog

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            role = request.POST.get('role')
            if user.role != role:
                messages.error(request, f"Please select the correct role. You are registered as a {user.get_role_display()}.")
            else:
                login(request, user)
                ActivityLog.objects.create(
                    user=user,
                    action='auth',
                    action_name='User Login',
                    details=f'Logged in from IP: {request.META.get("REMOTE_ADDR")}'
                )
                return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid credentials")
            
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'student')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=email).exists():
            messages.error(request, "A user with this email already exists")
        else:
            user = User.objects.create_user(username=email, email=email, password=password, role=role)
            user.first_name = full_name
            
            if role == 'student':
                user.enrollment_no = request.POST.get('enrollment_no')
                user.batch = request.POST.get('batch')
            
            # Grant admin portal access if role is admin
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
                
            user.save()
            ActivityLog.objects.create(
                user=user,
                action='auth',
                action_name='User Registered',
                details=f'New {role} account created.'
            )
            messages.success(request, f"Account created successfully! Please sign in as {role.capitalize()}.")
            return redirect('accounts:login')
            
    return render(request, 'register.html')

def logout_view(request):
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action='auth',
            action_name='User Logout',
            details='Logged out successfully.'
        )
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
