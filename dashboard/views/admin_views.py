"""
Admin Dashboard & User Management views.

Handles the admin home dashboard (stats overview) and the user management page
(create, edit, delete, toggle status, send password reset emails).
"""

import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from academic.models import Course, Batch, Department
from dashboard.notifications import create_notification
from assignments.models import Submission

User = get_user_model()


# =============================================================================
# Admin Dashboard (Home)
# =============================================================================

@login_required
def admin_dashboard(request):
    """
    Admin home page with platform-wide stats:
    user counts by role, active courses, batches, and total submissions.
    """
    if request.user.role != 'admin':
        return redirect('home')

    total_users = User.objects.filter(is_active=True).count()
    student_count = User.objects.filter(is_active=True, role='student').count()
    faculty_count = User.objects.filter(is_active=True, role='faculty').count()
    admin_count = User.objects.filter(is_active=True, role='admin').count()

    # Calculate percentage distribution for the dashboard chart
    student_percent = round((student_count / total_users * 100)) if total_users > 0 else 0
    faculty_percent = round((faculty_count / total_users * 100)) if total_users > 0 else 0
    admin_percent = round((admin_count / total_users * 100)) if total_users > 0 else 0

    context = {
        'total_users': total_users,
        'student_count': student_count,
        'faculty_count': faculty_count,
        'admin_count': admin_count,
        'student_percent': student_percent,
        'faculty_percent': faculty_percent,
        'admin_percent': admin_percent,
        'active_courses': Course.objects.filter(is_archived=False).count(),
        'total_batches': Batch.objects.filter(is_archived=False).count(),
        'total_submissions': Submission.objects.count(),
    }
    return render(request, 'dashboard/admin/dashboard.html', context)


# =============================================================================
# User Management
# =============================================================================

@login_required
def admin_users(request):
    """
    GET:  Lists all users with batch and department data.
    POST: Handles multiple actions via the 'action' param:
      - toggle_status: Activate/deactivate a user (cannot deactivate self)
      - create: Create a new user (student/faculty/admin) with optional batch/department
      - edit: Update user details (name, role, batch, department)
      - delete: Permanently delete a user (cannot delete self)
      - send_reset_email: Send password reset instructions to a user
    """
    if request.user.role != 'admin':
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')

        # --- Toggle Active/Inactive ---
        if action == 'toggle_status':
            user_id = request.POST.get('user_id')
            target_user = get_object_or_404(User, pk=user_id)
            if target_user == request.user:
                messages.error(request, "You cannot deactivate your own account.")
            else:
                target_user.is_active = not target_user.is_active
                status_text = 'activated' if target_user.is_active else 'deactivated'
                target_user.save()
                messages.success(request, f"User {target_user.email} successfully {status_text}.")

        # --- Create New User ---
        elif action == 'create':
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip()
            role = request.POST.get('role', 'student')
            batch_name = request.POST.get('batch', '').strip()
            department = request.POST.get('department', '').strip()

            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
            else:
                # Split full name into first/last
                first_name, *last_name_parts = full_name.split(' ', 1)
                last_name = last_name_parts[0] if last_name_parts else ''

                password = request.POST.get('password', 'AssignHub@123')

                new_user = User(
                    email=email,
                    username=email,  # Consistent with registration: email = username
                    first_name=first_name,
                    last_name=last_name,
                    role=role
                )

                # Admin users get staff + superuser privileges
                if role == 'admin':
                    new_user.is_staff = True
                    new_user.is_superuser = True

                new_user.set_password(password)
                new_user.save()

                # Role-specific field setup
                if role == 'student':
                    new_user.enrollment_no = request.POST.get('enrollment_no', '').strip()
                    if batch_name:
                        batch_obj = Batch.objects.filter(name__iexact=batch_name).first()
                        if batch_obj:
                            new_user.batch = batch_obj.name
                            new_user.save()
                            batch_obj.students.add(new_user)  # M2M enrollment
                    new_user.save()
                elif role == 'faculty':
                    new_user.faculty_id = request.POST.get('faculty_id', '').strip()
                    if department:
                        new_user.department = department
                    new_user.save()

                # Notify the admin who created the user
                create_notification(
                    user=request.user,
                    title="User Created",
                    message=f"New {role} account created for {email}. A welcome email has been sent.",
                    link="/dashboard/admin/users/",
                    notification_type='system'
                )

                # Send password reset email so the new user can set their own password
                form = PasswordResetForm({'email': email})
                if form.is_valid():
                    form.save(
                        request=request,
                        email_template_name='auth/password_reset_email.html',
                        subject_template_name='auth/password_reset_subject.txt',
                    )

                messages.success(request, f"User {email} created successfully. Instructions sent to their email.")

        # --- Edit Existing User ---
        elif action == 'edit':
            user_id = request.POST.get('user_id')
            target_user = get_object_or_404(User, pk=user_id)

            full_name = request.POST.get('full_name', '').strip()
            role = request.POST.get('role', target_user.role)
            batch_name = request.POST.get('batch', '').strip()
            department = request.POST.get('department', '').strip()

            first_name, *last_name_parts = full_name.split(' ', 1)
            target_user.first_name = first_name
            target_user.last_name = last_name_parts[0] if last_name_parts else ''
            target_user.role = role

            # Update role-specific fields
            if role == 'faculty':
                target_user.department = department
                target_user.faculty_id = request.POST.get('faculty_id', '').strip()
            elif role == 'student':
                target_user.enrollment_no = request.POST.get('enrollment_no', '').strip()

            target_user.save()

            # Sync student batch enrollment
            if role == 'student' and batch_name:
                batch_obj = Batch.objects.filter(name__iexact=batch_name).first()
                if batch_obj:
                    target_user.batch = batch_obj.name
                    target_user.save()
                    batch_obj.students.add(target_user)

            messages.success(request, f"User {target_user.email} updated successfully.")

        # --- Delete User ---
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            target_user = get_object_or_404(User, pk=user_id)
            if target_user == request.user:
                messages.error(request, "You cannot delete your own account.")
            else:
                user_email = target_user.email
                target_user.delete()
                messages.success(request, f"User {user_email} has been permanently deleted.")

        # --- Send Password Reset Email ---
        elif action == 'send_reset_email':
            user_id = request.POST.get('user_id')
            target_user = get_object_or_404(User, pk=user_id)

            form = PasswordResetForm({'email': target_user.email})
            if form.is_valid():
                form.save(
                    request=request,
                    email_template_name='auth/password_reset_email.html',
                    subject_template_name='auth/password_reset_subject.txt',
                )
                messages.success(request, f"Password reset instructions have been sent to {target_user.email}.")
            else:
                messages.error(request, "Failed to send reset email.")

        return redirect('dashboard:admin_users')

    # GET: List all users
    batches = Batch.objects.filter(is_archived=False).order_by('name')
    users = User.objects.all().prefetch_related('enrolled_batches').order_by('-date_joined')
    context = {
        'users': users,
        'departments': Department.objects.all(),
        'batches': batches,
    }
    return render(request, 'dashboard/admin/users.html', context)