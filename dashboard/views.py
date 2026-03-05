from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Course, Batch
from dashboard.models import ActivityLog
import re
from datetime import datetime
from django.db.models import Count, Q

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('home')

    User = get_user_model()
    context = {
        'total_users': User.objects.filter(is_active=True).count(),
        'active_courses': Course.objects.filter(is_archived=False).count(),
        'total_batches': Batch.objects.filter(is_archived=False).count(),
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
                
                new_user = User(
                    email=email,
                    username=email.split('@')[0],
                    first_name=first_name,
                    last_name=last_name,
                    role=role
                )
                new_user.set_password('AssignHub@123') # Default password
                
                new_user.save()
                
                if role == 'student' and batch_name:
                    batch_obj = Batch.objects.filter(name__iexact=batch_name).first()
                    if batch_obj:
                        new_user.batch = batch_obj.name
                        new_user.save()
                        batch_obj.students.add(new_user)
                elif role == 'faculty' and department:
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
    return render(request, 'dashboard/faculty_dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')
