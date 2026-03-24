from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Course, Batch
from academic.constants import SEMESTERS
from dashboard.notifications import create_notification

@login_required
def admin_batches(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    from dashboard.forms import AdminBatchForm
    
    if request.method == 'POST':
        form = AdminBatchForm(request.POST, prefix='add')
        if form.is_valid():
            try:
                batch = form.save()
                messages.success(request, f"Batch {batch.name} added successfully.")
            except Exception as e:
                messages.error(request, f"Error creating batch: {str(e)}")
            return redirect('dashboard:admin_batches')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AdminBatchForm(prefix='add')
        
    show_archived = request.GET.get('show_archived', 'false') == 'true'
    batches = Batch.objects.prefetch_related('students', 'courses') \
        .annotate(course_count=Count('courses', distinct=True)) \
        .filter(is_archived=show_archived) \
        .order_by('-id')
    
    # Simple form for the edit modal structure
    edit_form = AdminBatchForm(prefix='edit')
    
    context = {
        'batches': batches,
        'semesters': SEMESTERS,
        'show_archived': show_archived,
        'form': form,
        'edit_form': edit_form,
    }
    return render(request, 'dashboard/admin/batches.html', context)

@login_required
def admin_batch_edit(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    batch = get_object_or_404(Batch, pk=pk)
    from dashboard.forms import AdminBatchForm
    
    if request.method == 'POST':
        form = AdminBatchForm(request.POST, instance=batch, prefix='edit')
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Batch {batch.name} updated successfully.")
            except Exception as e:
                messages.error(request, f"Error updating batch: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
                
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
        else:
            batch.is_archived = True
            messages.success(request, f"Batch {batch.name} archived successfully.")
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
            elif action == 'remove':
                batch.students.remove(student)
                messages.success(request, f"Removed student {student.first_name} from {batch.name}.")
                
        return redirect('dashboard:admin_manage_batch_students', pk=pk)
        
    enrolled_students = batch.students.all().order_by('first_name')
    available_students = User.objects.filter(role='student').filter(enrolled_batches__isnull=True).order_by('first_name')
    
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
                
                # Notify Faculty
                if course.faculty:
                    create_notification(
                        user=course.faculty,
                        title="Course Batch Update",
                        message=f"Your course {course.code} has been assigned to a new batch: {batch.name}.",
                        link="/dashboard/faculty/courses/",
                        notification_type='system'
                    )
            elif action == 'remove':
                batch.courses.remove(course)
                messages.success(request, f"Removed course {course.code} from {batch.name}.")
                
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
