"""
Views for the accounts app.

Handles login, registration, logout, role-based dashboard routing,
and the public home page.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from .models import User
from .forms import UserRegistrationForm


def login_view(request):
    """
    Authenticates a user with email and password.
    Also verifies that the selected role matches the user's actual role
    to prevent accessing the wrong dashboard.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            # Verify the role selected on the login form matches the DB role
            role = request.POST.get('role')
            if user.role != role:
                messages.error(request, f"Please select the correct role. You are registered as a {user.get_role_display()}.")
            else:
                login(request, user)
                return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'auth/login.html')


def register_view(request):
    """
    Handles new user registration for Students and Faculty.
    On success, sends a welcome email and redirects to the login page.
    """
    # Redirect already logged-in users to their dashboard
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                # Send welcome email (fails silently so registration isn't blocked)
                try:
                    send_mail(
                        'Welcome to AssignHub!',
                        f'Hello {user.first_name},\n\n'
                        f'Welcome to AssignHub! Your account as a {user.get_role_display()} '
                        f'has been created successfully.\n\n'
                        f'You can now sign in to your dashboard to get started.\n\n'
                        f'Best Regards,\nAssignHub Team',
                        None,  # Uses DEFAULT_FROM_EMAIL / EMAIL_HOST_USER from settings
                        [user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass  # Email failure should never block registration

                messages.success(request, f"Account created successfully! Please sign in as {user.role.capitalize()}.")
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            # Surface form validation errors as user-friendly messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = UserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    """Logs out the user and redirects to the home page."""
    logout(request)
    return redirect('home')


def dashboard_redirect(request):
    """
    Central routing hub after login.
    Redirects users to their role-specific dashboard:
      - admin   -> /dashboard/admin/
      - faculty -> /dashboard/faculty/
      - student -> /dashboard/student/
    """
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
    """Renders the public landing page."""
    return render(request, 'home.html')
