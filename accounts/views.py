from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User
from .models import User

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
                return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid credentials")
            
    return render(request, 'auth/login.html')

from django.core.mail import send_mail
from .forms import UserRegistrationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Send Welcome Email via Gmail SMTP
                try:
                    send_mail(
                        'Welcome to AssignHub!',
                        f'Hello {user.first_name},\n\nWelcome to AssignHub! Your account as a {user.get_role_display()} has been created successfully.\n\nYou can now sign in to your dashboard to get started.\n\nBest Regards,\nAssignHub Team',
                        None, # Uses EMAIL_HOST_USER
                        [user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
                
                messages.success(request, f"Account created successfully! Please sign in as {user.role.capitalize()}.")
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = UserRegistrationForm()
            
    return render(request, 'auth/register.html', {'form': form})

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
