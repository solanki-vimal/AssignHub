import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Course, Batch
from academic.constants import DEPARTMENTS
from dashboard.models import ActivityLog, SystemSettings

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('home')

    User = get_user_model()
    
    total_users = User.objects.filter(is_active=True).count()
    student_count = User.objects.filter(is_active=True, role='student').count()
    faculty_count = User.objects.filter(is_active=True, role='faculty').count()
    admin_count = User.objects.filter(is_active=True, role='admin').count()
    
    student_percent = round((student_count / total_users * 100)) if total_users > 0 else 0
    faculty_percent = round((faculty_count / total_users * 100)) if total_users > 0 else 0
    admin_percent = round((admin_count / total_users * 100)) if total_users > 0 else 0
    
    recent_logs = ActivityLog.objects.select_related('user').order_by('-timestamp')[:5]

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
        'recent_logs': recent_logs,
    }
    return render(request, 'dashboard/admin/dashboard.html', context)

@login_required
def admin_users(request):
    if request.user.role != 'admin':
        return redirect('home')
        
    User = get_user_model()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
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
                ActivityLog.objects.create(
                    user=request.user,
                    action='update',
                    action_name='User Status Changed',
                    details=f'User {target_user.email} was {status_text}.'
                )
                
        elif action == 'create':
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip()
            role = request.POST.get('role', 'student')
            batch_name = request.POST.get('batch', '').strip()
            department = request.POST.get('department', '').strip()
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
            else:
                first_name, *last_name_parts = full_name.split(' ', 1)
                last_name = last_name_parts[0] if last_name_parts else ''
                
                password = request.POST.get('password', 'AssignHub@123')
                
                new_user = User(
                    email=email,
                    username=email, # Use email as username pattern to match registration
                    first_name=first_name,
                    last_name=last_name,
                    role=role
                )
                
                if role == 'admin':
                    new_user.is_staff = True
                    new_user.is_superuser = True
                    
                new_user.set_password(password)
                
                new_user.save()
                
                if role == 'student':
                    new_user.enrollment_no = request.POST.get('enrollment_no', '').strip()
                    if batch_name:
                        batch_obj = Batch.objects.filter(name__iexact=batch_name).first()
                        if batch_obj:
                            new_user.batch = batch_obj.name
                            new_user.save()
                            batch_obj.students.add(new_user)
                    new_user.save()
                elif role == 'faculty':
                    new_user.faculty_id = request.POST.get('faculty_id', '').strip()
                    if department:
                        new_user.department = department
                    new_user.save()
                messages.success(request, f"User {email} created successfully.")
                ActivityLog.objects.create(
                    user=request.user,
                    action='create',
                    action_name='User Created',
                    details=f'Created new {role} account: {email}'
                )
                
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
            
            if role == 'faculty':
                target_user.department = department
                target_user.faculty_id = request.POST.get('faculty_id', '').strip()
            elif role == 'student':
                target_user.enrollment_no = request.POST.get('enrollment_no', '').strip()
                
            target_user.save()
            
            if role == 'student' and batch_name:
                batch_obj = Batch.objects.filter(name__iexact=batch_name).first()
                if batch_obj:
                    target_user.batch = batch_obj.name
                    target_user.save()
                    batch_obj.students.add(target_user)
                    
            messages.success(request, f"User {target_user.email} updated successfully.")
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                action_name='User Updated',
                details=f'Updated details for {target_user.email}'
            )
            
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            target_user = get_object_or_404(User, pk=user_id)
            if target_user == request.user:
                messages.error(request, "You cannot delete your own account.")
            else:
                user_email = target_user.email
                target_user.delete()
                messages.success(request, f"User {user_email} has been permanently deleted.")
                ActivityLog.objects.create(
                    user=request.user,
                    action='delete',
                    action_name='User Deleted',
                    details=f'Permanently deleted user: {user_email}'
                )
                
        elif action == 'reset_password':
            user_id = request.POST.get('user_id')
            new_password = request.POST.get('new_password')
            target_user = get_object_or_404(User, pk=user_id)
            
            if new_password:
                target_user.set_password(new_password)
                target_user.save()
                messages.success(request, f"Password for {target_user.email} has been reset successfully.")
                ActivityLog.objects.create(
                    user=request.user,
                    action='update',
                    action_name='Password Reset',
                    details=f'Password manually reset for: {target_user.email}'
                )
            else:
                messages.error(request, "New password cannot be empty.")
                
        return redirect('dashboard:admin_users')

    batches = Batch.objects.filter(is_archived=False).order_by('name')
    users = User.objects.all().prefetch_related('enrolled_batches').order_by('-date_joined')
    context = {
        'users': users,
        'departments': DEPARTMENTS,
        'batches': batches,
    }
    return render(request, 'dashboard/admin/users.html', context)

@login_required
def admin_logs(request):
    if request.user.role != 'admin':
        return redirect('home')
        
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'dashboard/admin/logs.html', context)

@login_required
def admin_logs_export(request):
    if request.user.role != 'admin':
        return redirect('home')
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="activity_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Action Name', 'Action Type', 'User Email', 'Role', 'Details'])
    
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    for log in logs:
        user_email = log.user.email if log.user else 'System'
        user_role = log.user.get_role_display() if log.user else 'System'
        timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, log.action_name, log.action, user_email, user_role, log.details])
        
    return response

@login_required
def admin_settings(request):
    if request.user.role != 'admin':
        return redirect('home')
        
    settings = SystemSettings.load()
    
    if request.method == 'POST':
        tab = request.POST.get('tab', 'general')
        
        if tab == 'general':
            settings.institution_name = request.POST.get('institution_name', settings.institution_name)
            settings.system_email = request.POST.get('system_email', settings.system_email)
            settings.current_academic_year = request.POST.get('current_academic_year', settings.current_academic_year)
            settings.current_semester = request.POST.get('current_semester', settings.current_semester)
            settings.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
            
        elif tab == 'submissions':
            settings.max_file_size_mb = int(request.POST.get('max_file_size_mb', settings.max_file_size_mb))
            settings.allowed_formats = request.POST.get('allowed_formats', settings.allowed_formats)
            settings.allow_late_submissions = request.POST.get('allow_late_submissions') == 'on'
            
        elif tab == 'notifications':
            settings.email_notifications = request.POST.get('email_notifications') == 'on'
            
        elif tab == 'security':
            settings.session_timeout_mins = int(request.POST.get('session_timeout_mins', settings.session_timeout_mins))
            settings.max_login_attempts = int(request.POST.get('max_login_attempts', settings.max_login_attempts))
            settings.require_2fa = request.POST.get('require_2fa') == 'on'
            
        # The 'archives' tab logic is intentionally bypassed as per MVP design
            
        settings.save()
        messages.success(request, f"{tab.capitalize()} settings updated successfully.")
        
        ActivityLog.objects.create(
            user=request.user,
            action='update',
            action_name='Settings Updated',
            details=f'Updated system {tab} settings'
        )
        return redirect('dashboard:admin_settings')

    context = {
        'settings': settings,
    }
    return render(request, 'dashboard/admin/settings.html', context)
