from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assignment, AssignmentAttachment
from .forms import AssignmentForm
from academic.models import Course, Batch
from django.db.models import Count
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def faculty_assignments(request):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignments = Assignment.objects.filter(created_by=request.user).select_related('course', 'batch').prefetch_related('attachments').order_by('-created_at')
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False)
    
    context = {
        'assignments': assignments,
        'faculty_courses': faculty_courses,
    }
    return render(request, 'dashboard/faculty/assignments.html', context)

@login_required
def faculty_create_assignment(request):
    if request.user.role != 'faculty':
        return redirect('home')
        
    if request.method == 'POST':
        form = AssignmentForm(request.POST, faculty=request.user)
        if form.is_valid():
            try:
                assignment = form.save(commit=False)
                assignment.created_by = request.user
                assignment.save()
                
                # Handle file attachments
                files = request.FILES.getlist('attachments')
                for f in files:
                    AssignmentAttachment.objects.create(assignment=assignment, file=f)
                
                messages.success(request, f"Assignment '{assignment.title}' created successfully.")
                return redirect('dashboard:faculty_assignments')
            except Exception as e:
                messages.error(request, f"Error creating assignment: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AssignmentForm(faculty=request.user)
                
    # Get courses for batch filtering and display
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False).annotate(
        students_count=Count('students', distinct=True)
    ).prefetch_related('batches')
    
    
    # Serialize course-to-batches mapping for JavaScript
    course_batches_data = {}
    for course in faculty_courses:
        course_batches_data[str(course.id)] = [
            {"id": str(batch.id), "name": f"{batch.name} ({batch.academic_year})"}
            for batch in course.batches.all()
        ]
    
    context = {
        'form': form,
        'faculty_courses': faculty_courses,
        'course_to_batches_json': json.dumps(course_batches_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'dashboard/faculty/create_assignment.html', context)

from django.shortcuts import get_object_or_404

@login_required
def faculty_view_assignment(request, pk):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    
    context = {
        'assignment': assignment,
    }
    return render(request, 'dashboard/faculty/assignment_detail.html', context)

@login_required
def faculty_edit_assignment(request, pk):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment, faculty=request.user)
        if form.is_valid():
            try:
                form.save()
                
                # Handle removing existing attachments
                remove_ids = request.POST.getlist('remove_attachments')
                if remove_ids:
                    AssignmentAttachment.objects.filter(id__in=remove_ids, assignment=assignment).delete()
                    
                # Handle NEW file attachments
                files = request.FILES.getlist('attachments')
                for f in files:
                    AssignmentAttachment.objects.create(assignment=assignment, file=f)
                
                messages.success(request, f"Assignment '{assignment.title}' updated successfully.")
                return redirect('dashboard:faculty_view_assignment', pk=assignment.pk)
            except Exception as e:
                messages.error(request, f"Error updating assignment: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AssignmentForm(instance=assignment, faculty=request.user)
                
    # Get courses for batch filtering and display
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False).annotate(
        students_count=Count('students', distinct=True)
    ).prefetch_related('batches')
    
    # Serialize course-to-batches mapping for JavaScript
    course_batches_data = {}
    for course in faculty_courses:
        course_batches_data[str(course.id)] = [
            {"id": str(batch.id), "name": f"{batch.name} ({batch.academic_year})"}
            for batch in course.batches.all()
        ]
    
    context = {
        'form': form,
        'assignment': assignment,
        'faculty_courses': faculty_courses,
        'course_to_batches_json': json.dumps(course_batches_data, cls=DjangoJSONEncoder),
        'is_edit': True,
    }
    return render(request, 'dashboard/faculty/create_assignment.html', context)

from django.views.decorators.http import require_POST

@login_required
@require_POST
def faculty_toggle_publish(request, pk):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assignment, AssignmentAttachment
from .forms import AssignmentForm
from academic.models import Course, Batch
from django.db.models import Count
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def faculty_assignments(request):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignments = Assignment.objects.filter(created_by=request.user).select_related('course', 'batch').prefetch_related('attachments').order_by('-created_at')
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False)
    
    context = {
        'assignments': assignments,
        'faculty_courses': faculty_courses,
    }
    return render(request, 'dashboard/faculty/assignments.html', context)

@login_required
def faculty_create_assignment(request):
    if request.user.role != 'faculty':
        return redirect('home')
        
    if request.method == 'POST':
        form = AssignmentForm(request.POST, faculty=request.user)
        if form.is_valid():
            try:
                assignment = form.save(commit=False)
                assignment.created_by = request.user
                assignment.save()
                
                # Handle file attachments
                files = request.FILES.getlist('attachments')
                for f in files:
                    AssignmentAttachment.objects.create(assignment=assignment, file=f)
                
                messages.success(request, f"Assignment '{assignment.title}' created successfully.")
                return redirect('dashboard:faculty_assignments')
            except Exception as e:
                messages.error(request, f"Error creating assignment: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AssignmentForm(faculty=request.user)
                
    # Get courses for batch filtering and display
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False).annotate(
        students_count=Count('students', distinct=True)
    ).prefetch_related('batches')
    
    
    # Serialize course-to-batches mapping for JavaScript
    course_batches_data = {}
    for course in faculty_courses:
        course_batches_data[str(course.id)] = [
            {"id": str(batch.id), "name": f"{batch.name} ({batch.academic_year})"}
            for batch in course.batches.all()
        ]
    
    context = {
        'form': form,
        'faculty_courses': faculty_courses,
        'course_to_batches_json': json.dumps(course_batches_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'dashboard/faculty/create_assignment.html', context)

from django.shortcuts import get_object_or_404

@login_required
def faculty_view_assignment(request, pk):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    
    context = {
        'assignment': assignment,
    }
    return render(request, 'dashboard/faculty/assignment_detail.html', context)

@login_required
def faculty_edit_assignment(request, pk):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment, faculty=request.user)
        if form.is_valid():
            try:
                form.save()
                
                # Handle removing existing attachments
                remove_ids = request.POST.getlist('remove_attachments')
                if remove_ids:
                    AssignmentAttachment.objects.filter(id__in=remove_ids, assignment=assignment).delete()
                    
                # Handle NEW file attachments
                files = request.FILES.getlist('attachments')
                for f in files:
                    AssignmentAttachment.objects.create(assignment=assignment, file=f)
                
                messages.success(request, f"Assignment '{assignment.title}' updated successfully.")
                return redirect('dashboard:faculty_view_assignment', pk=assignment.pk)
            except Exception as e:
                messages.error(request, f"Error updating assignment: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AssignmentForm(instance=assignment, faculty=request.user)
                
    # Get courses for batch filtering and display
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False).annotate(
        students_count=Count('students', distinct=True)
    ).prefetch_related('batches')
    
    # Serialize course-to-batches mapping for JavaScript
    course_batches_data = {}
    for course in faculty_courses:
        course_batches_data[str(course.id)] = [
            {"id": str(batch.id), "name": f"{batch.name} ({batch.academic_year})"}
            for batch in course.batches.all()
        ]
    
    context = {
        'form': form,
        'assignment': assignment,
        'faculty_courses': faculty_courses,
        'course_to_batches_json': json.dumps(course_batches_data, cls=DjangoJSONEncoder),
        'is_edit': True,
    }
    return render(request, 'dashboard/faculty/create_assignment.html', context)

from django.views.decorators.http import require_POST

@login_required
@require_POST
def faculty_toggle_publish(request, pk):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    
    assignment.published = not assignment.published
    assignment.save()
    
    status_text = "published" if assignment.published else "unpublished (saved as draft)"
    messages.success(request, f"Assignment '{assignment.title}' is now {status_text}.")
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:faculty_assignments'))

@login_required
@require_POST
def faculty_delete_assignment(request, pk):
    """
    Deletes an assignment. Must be an explicit POST request.
    """
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    
    title = assignment.title
    assignment.delete()
    
    messages.success(request, f"Assignment '{title}' was deleted successfully.")
    
    return redirect('dashboard:faculty_assignments')
