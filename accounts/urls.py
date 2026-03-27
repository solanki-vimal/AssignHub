"""
URL configuration for the accounts app.

Handles authentication (login, register, logout), post-login dashboard routing,
and the full password reset flow using Django's built-in auth views.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # --- Authentication ---
    path('login/', views.login_view, name='login'),                     # POST: authenticate & redirect
    path('register/', views.register_view, name='register'),            # GET: form | POST: create user
    path('logout/', views.logout_view, name='logout'),                  # Logs out and redirects to home

    # --- Post-login routing ---
    path('dashboard-redirect/', views.dashboard_redirect, name='dashboard_redirect'),  # Routes to role-based dashboard

    # --- Password Reset Flow (Django built-in views with custom templates) ---
    # Step 1: User enters email
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset_form.html',
        email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt',
        success_url='/accounts/password-reset/done/'
    ), name='password_reset'),

    # Step 2: Confirmation that email was sent
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),

    # Step 3: User clicks the email link and sets new password
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        success_url='/accounts/password-reset-complete/'
    ), name='password_reset_confirm'),

    # Step 4: Success page after password is changed
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
]
