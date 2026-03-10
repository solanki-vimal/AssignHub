from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Course, Batch
from academic.constants import SEMESTERS
from dashboard.models import ActivityLog

@login_required
def admin_batches(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    User = get_user_model()
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
