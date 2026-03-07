import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Course, Batch
from dashboard.models import ActivityLog
import re
from datetime import datetime
from django.db.models import Count, Q
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
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def admin_courses(request):
    if request.user.role != 'admin':
        return redirect('home')
        
    User = get_user_model()
    DEPARTMENTS = [
        ('CE', 'Computer Engineering'),
        ('IT', 'Information Technology'),
        ('EC', 'Electronics Communication'),
        ('ME', 'Mechanical Engineering'),
        ('CL', 'Civil Engineering')
    ]
    SEMESTERS = list(range(1, 9))
    faculty_list = User.objects.filter(role='faculty').order_by('first_name')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        semester = request.POST.get('semester')
        department = request.POST.get('department')
        status = request.POST.get('status', 'active')
        faculty_id = request.POST.get('faculty_id')
        
        if not all([code, name, semester, department]):
            messages.error(request, "All required fields must be filled.")
        elif Course.objects.filter(code=code).exists():
            messages.error(request, f"Course with code {code} already exists.")
        else:
            try:
                semester_num = int(re.search(r'\d+', str(semester)).group()) if not str(semester).isdigit() else int(semester)
                faculty = User.objects.get(pk=faculty_id) if faculty_id else None
                course = Course.objects.create(
                    code=code,
                    name=name,
                    semester=semester_num,
                    department=department,
                    is_active=(status == 'active'),
                    faculty=faculty
                )
                messages.success(request, f"Course {code} added successfully.")
                ActivityLog.objects.create(
                    user=request.user,
                    action='create',
                    action_name='Course Created',
                    details=f'Course {code} - {name} was created.'
                )
            except Exception as e:
                messages.error(request, f"Error creating course: {str(e)}")
        return redirect('dashboard:admin_courses')
    show_archived = request.GET.get('show_archived', 'false') == 'true'
    courses = Course.objects.select_related('faculty').filter(is_archived=show_archived)
    context = {
        'courses': courses,
        'departments': DEPARTMENTS,
        'semesters': SEMESTERS,
        'faculty_list': faculty_list,
        'show_archived': show_archived,
    }
    return render(request, 'dashboard/admin/courses.html', context)

@login_required
def admin_course_edit(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    User = get_user_model()
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        semester = request.POST.get('semester')
        department = request.POST.get('department')
        status = request.POST.get('status', 'active')
        faculty_id = request.POST.get('faculty_id')
        
        if not all([code, name, semester, department]):
            messages.error(request, "All required fields must be filled.")
        elif Course.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, f"Course with code {code} already exists.")
        else:
            try:
                semester_num = int(re.search(r'\d+', semester).group()) if not semester.isdigit() else int(semester)
                course.code = code
                course.name = name
                course.semester = semester_num
                course.department = department
                course.is_active = (status == 'active')
                course.faculty = User.objects.get(pk=faculty_id) if faculty_id else None
                course.save()
                
                messages.success(request, f"Course {code} updated successfully.")
                ActivityLog.objects.create(
                    user=request.user,
                    action='update',
                    action_name='Course Updated',
                    details=f'Course {code} details were updated.'
                )
            except Exception as e:
                messages.error(request, f"Error updating course: {str(e)}")
                
    return redirect('dashboard:admin_courses')

@login_required
def admin_course_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        code = course.code
        course.delete()
        messages.success(request, f"Course {code} deleted successfully.")
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            action_name='Course Deleted',
            details=f'Course {code} was permanently deleted.'
        )
        
    return redirect('dashboard:admin_courses')

@login_required
def admin_course_archive(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action', 'archive')
        if action == 'unarchive':
            course.is_archived = False
            messages.success(request, f"Course {course.code} unarchived successfully.")
            ActivityLog.objects.create(user=request.user, action='update', action_name='Course Unarchived', details=f'{course.code}')
        else:
            course.is_archived = True
            messages.success(request, f"Course {course.code} archived successfully.")
            ActivityLog.objects.create(user=request.user, action='update', action_name='Course Archived', details=f'{course.code}')
        course.save()
        
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:admin_courses'))

@login_required
def admin_manage_course_students(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
        
    User = get_user_model()
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')
        
        if student_id:
            student = get_object_or_404(User, pk=student_id, role='student')
            if action == 'add':
                course.students.add(student)
                messages.success(request, f"Added student {student.first_name} to {course.name}.")
                ActivityLog.objects.create(user=request.user, action='update', action_name='Course Enrollment', details=f'Added {student.email} to {course.code}')
            elif action == 'remove':
                course.students.remove(student)
                messages.success(request, f"Removed student {student.first_name} from {course.name}.")
                ActivityLog.objects.create(user=request.user, action='update', action_name='Course Enrollment', details=f'Removed {student.email} from {course.code}')
                
        return redirect('dashboard:admin_manage_course_students', pk=pk)
        
    enrolled_students = course.students.all().order_by('first_name')
    available_students = User.objects.filter(role='student').exclude(enrolled_courses=course).order_by('first_name')
    
    context = {
        'course': course,
        'enrolled_students': enrolled_students,
        'available_students': available_students
    }
    return render(request, 'dashboard/admin/manage_course_students.html', context)

@login_required
def admin_batches(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    User = get_user_model()
    SEMESTERS = list(range(1, 9))
    faculty_list = User.objects.filter(role='faculty').order_by('first_name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status', 'active')
        semester = request.POST.get('semester')
        coordinator_id = request.POST.get('coordinator_id')
        
        if not all([name, start_date, end_date]):
            messages.error(request, "Name and dates are required.")
        else:
            try:
                s_year = start_date.split('-')[0]
                e_year = end_date.split('-')[0][-2:]
                academic_year = f"{s_year}-{e_year}"
                coordinator = User.objects.get(pk=coordinator_id) if coordinator_id else None
                semester_num = int(semester) if semester else None
                
                if Batch.objects.filter(name=name, academic_year=academic_year).exists():
                    messages.error(request, f"Batch {name} for {academic_year} already exists.")
                else:
                    batch = Batch.objects.create(
                        name=name,
                        academic_year=academic_year,
                        is_active=(status == 'active'),
                        semester=semester_num,
                        coordinator=coordinator
                    )
                            
                    messages.success(request, f"Batch {name} added successfully.")
                    ActivityLog.objects.create(
                        user=request.user,
                        action='create',
                        action_name='Batch Created',
                        details=f'Batch {name} ({academic_year}) was created.'
                    )
            except Exception as e:
                messages.error(request, f"Error creating batch: {str(e)}")
        return redirect('dashboard:admin_batches')
    show_archived = request.GET.get('show_archived', 'false') == 'true'
    batches = Batch.objects.select_related('coordinator') \
        .prefetch_related('students', 'courses') \
        .annotate(course_count=Count('courses', distinct=True)) \
        .filter(is_archived=show_archived) \
        .order_by('-id')
    context = {
        'batches': batches,
        'semesters': SEMESTERS,
        'faculty_list': faculty_list,
        'show_archived': show_archived,
    }
    return render(request, 'dashboard/admin/batches.html', context)

@login_required
def admin_batch_edit(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    User = get_user_model()
    batch = get_object_or_404(Batch, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status', 'active')
        semester = request.POST.get('semester')
        coordinator_id = request.POST.get('coordinator_id')
        
        if not all([name, start_date, end_date]):
            messages.error(request, "Name and dates are required.")
        else:
            try:
                s_year = start_date.split('-')[0]
                e_year = end_date.split('-')[0][-2:]
                academic_year = f"{s_year}-{e_year}"
                
                if Batch.objects.filter(name=name, academic_year=academic_year).exclude(pk=pk).exists():
                    messages.error(request, f"Batch {name} for {academic_year} already exists.")
                else:
                    batch.name = name
                    batch.academic_year = academic_year
                    batch.is_active = (status == 'active')
                    batch.semester = int(semester) if semester else None
                    batch.coordinator = User.objects.get(pk=coordinator_id) if coordinator_id else None
                    batch.save()
                            
                    messages.success(request, f"Batch {name} updated successfully.")
                    ActivityLog.objects.create(
                        user=request.user,
                        action='update',
                        action_name='Batch Updated',
                        details=f'Batch {name} details were updated.'
                    )
            except Exception as e:
                messages.error(request, f"Error updating batch: {str(e)}")
                
    return redirect('dashboard:admin_batches')

@login_required
def admin_batch_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    batch = get_object_or_404(Batch, pk=pk)
    
    if request.method == 'POST':
        name = batch.name
        batch.delete()
        messages.success(request, f"Batch {name} deleted successfully.")
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            action_name='Batch Deleted',
            details=f'Batch {name} was permanently deleted.'
        )
        
    return redirect('dashboard:admin_batches')

@login_required
def admin_batch_archive(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action', 'archive')
        if action == 'unarchive':
            batch.is_archived = False
            messages.success(request, f"Batch {batch.name} unarchived successfully.")
            ActivityLog.objects.create(user=request.user, action='update', action_name='Batch Unarchived', details=f'{batch.name}')
        else:
            batch.is_archived = True
            messages.success(request, f"Batch {batch.name} archived successfully.")
            ActivityLog.objects.create(user=request.user, action='update', action_name='Batch Archived', details=f'{batch.name}')
        batch.save()
        
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:admin_batches'))

@login_required
def admin_manage_batch_students(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
        
    User = get_user_model()
    batch = get_object_or_404(Batch, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')
        
        if student_id:
            student = get_object_or_404(User, pk=student_id, role='student')
            if action == 'add':
                batch.students.add(student)
                messages.success(request, f"Added student {student.first_name} to {batch.name}.")
                ActivityLog.objects.create(user=request.user, action='update', action_name='Batch Enrollment', details=f'Added {student.email} to {batch.name}')
            elif action == 'remove':
                batch.students.remove(student)
                messages.success(request, f"Removed student {student.first_name} from {batch.name}.")
                ActivityLog.objects.create(user=request.user, action='update', action_name='Batch Enrollment', details=f'Removed {student.email} from {batch.name}')
                
        return redirect('dashboard:admin_manage_batch_students', pk=pk)
        
    enrolled_students = batch.students.all().order_by('first_name')
    available_students = User.objects.filter(role='student').exclude(enrolled_batches=batch).order_by('first_name')
    
    context = {
        'batch': batch,
        'enrolled_students': enrolled_students,
        'available_students': available_students
    }
    return render(request, 'dashboard/admin/manage_batch_students.html', context)

@login_required
def admin_manage_batch_courses(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
        
    batch = get_object_or_404(Batch, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        course_id = request.POST.get('course_id')
        
        if course_id:
            course = get_object_or_404(Course, pk=course_id)
            if action == 'add':
                batch.courses.add(course)
                messages.success(request, f"Added course {course.code} to {batch.name}.")
                ActivityLog.objects.create(user=request.user, action='update', action_name='Batch Assignment', details=f'Added Course {course.code} to {batch.name}')
            elif action == 'remove':
                batch.courses.remove(course)
                messages.success(request, f"Removed course {course.code} from {batch.name}.")
                ActivityLog.objects.create(user=request.user, action='update', action_name='Batch Assignment', details=f'Removed Course {course.code} from {batch.name}')
                
        return redirect('dashboard:admin_manage_batch_courses', pk=pk)
        
    enrolled_courses = batch.courses.select_related('faculty').all().order_by('name')
    available_courses = Course.objects.filter(is_active=True).exclude(batches=batch).select_related('faculty').order_by('name')
    
    if batch.semester:
        available_courses = available_courses.filter(semester=batch.semester)
        
    context = {
        'batch': batch,
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses
    }
    return render(request, 'dashboard/admin/manage_batch_courses.html', context)

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

    DEPARTMENTS = [
        ('CE', 'Computer Engineering'),
        ('IT', 'Information Technology'),
        ('EC', 'Electronics Communication'),
        ('ME', 'Mechanical Engineering'),
        ('CL', 'Civil Engineering')
    ]
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
def faculty_dashboard(request):
    if request.user.role != 'faculty':
        if request.user.role == 'admin':
            return redirect('dashboard:admin_dashboard')
        elif request.user.role == 'student':
            return redirect('dashboard:student_dashboard')
        return redirect('home')

    # Fetch faculty-specific data
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False).annotate(
        students_count=Count('students')
    )
    
    total_courses = faculty_courses.count()
    total_students = faculty_courses.aggregate(total=Count('students', distinct=True))['total'] or 0
    
    # Placeholder for assignments until the model is fully implemented/populated
    # Assuming Assignments model exists in assignments app, but seen as empty earlier
    active_assignments = 0 
    recent_assignments = []

    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'active_assignments': active_assignments,
        'faculty_courses': faculty_courses,
        'recent_assignments': recent_assignments,
    }
    return render(request, 'dashboard/faculty_dashboard.html', context)

@login_required
def faculty_courses(request):
    if request.user.role != 'faculty':
        return redirect('home')
        
    # Get courses assigned to this faculty, including prefetching batches
    courses = Course.objects.filter(faculty=request.user, is_archived=False).prefetch_related('batches')
    
    context = {
        'courses': courses,
    }
    return render(request, 'dashboard/faculty/courses.html', context)

@login_required
def faculty_students(request):
    if request.user.role != 'faculty':
        return redirect('home')
        
    # Get all courses assigned to this faculty
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False)
    
    # Get all unique students enrolled in these courses
    # Prefetching to avoid N+1 issues when displaying student details
    students = request.user.assigned_courses.filter(is_archived=False).values_list('students', flat=True)
    User = get_user_model()
    enrolled_students = User.objects.filter(id__in=students, role='student').distinct().prefetch_related('enrolled_batches', 'enrolled_courses')
    
    context = {
        'students': enrolled_students,
    }
    return render(request, 'dashboard/faculty/students.html', context)

@login_required
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')

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
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        contact_no = request.POST.get('contact_no', '').strip()
        
        user.first_name = first_name
        user.last_name = last_name
        user.contact_no = contact_no
        
        if user.role == 'student':
            user.enrollment_no = request.POST.get('enrollment_no', '').strip()
            batch_name = request.POST.get('batch', '').strip()
            if batch_name:
                batch_obj = Batch.objects.filter(name__iexact=batch_name).first()
                if batch_obj:
                    user.batch = batch_obj.name
                    batch_obj.students.add(user)
                    
        elif user.role == 'faculty':
            user.faculty_id = request.POST.get('faculty_id', '').strip()
            user.department = request.POST.get('department', '').strip()
            
        user.save()
        
        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif not user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, "Password updated successfully.")
                
        messages.success(request, "Profile updated successfully.")
        return redirect('dashboard:profile')
        
    DEPARTMENTS = [
        ('CE', 'Computer Engineering'),
        ('IT', 'Information Technology'),
        ('EC', 'Electronics Communication'),
        ('ME', 'Mechanical Engineering'),
        ('CL', 'Civil Engineering')
    ]
    batches = Batch.objects.filter(is_archived=False).order_by('name')
    
    context = {
        'departments': DEPARTMENTS,
        'batches': batches,
    }
    return render(request, 'dashboard/profile.html', context)
