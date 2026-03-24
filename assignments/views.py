import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings as django_settings
from .models import Assignment, AssignmentAttachment
from .forms import AssignmentForm
from academic.models import Course, Batch


@login_required
def faculty_assignments(request):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignments = Assignment.objects.filter(
        created_by=request.user
    ).select_related('course', 'batch').prefetch_related('attachments').order_by('-created_at')
    
    # Compute stats for each assignment
    from .models import Submission
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    for assignment in assignments:
        # Total students assigned to this assignment (via its batch)
        total_students = User.objects.filter(
            role='student',
            enrolled_batches=assignment.batch,
            is_active=True
        ).distinct().count()
        
        assignment.submitted_count = Submission.objects.filter(assignment=assignment, status='submitted').count()
        assignment.evaluated_count = Submission.objects.filter(assignment=assignment, status='evaluated').count()
        assignment.late_count = Submission.objects.filter(assignment=assignment, status='late').count()
        
        # Pending is everyone who hasn't submitted/evaluated yet
        completed_count = assignment.submitted_count + assignment.evaluated_count + assignment.late_count
        assignment.pending_count = max(0, total_students - completed_count)
        
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
                
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False).annotate(
        students_count=Count('students', distinct=True)
    ).prefetch_related('batches')
    
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


@login_required
def faculty_view_assignment(request, pk):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)

    from assignments.models import Submission
    from django.contrib.auth import get_user_model
    User = get_user_model()

    total_students = User.objects.filter(
        role='student',
        enrolled_batches=assignment.batch,
        is_active=True
    ).distinct().count()

    submitted_count = Submission.objects.filter(
        assignment=assignment, status__in=['submitted', 'late', 'evaluated']
    ).count()
    
    pending_count = max(0, total_students - submitted_count)
    
    context = {
        'assignment': assignment,
        'submitted_count': submitted_count,
        'pending_count': pending_count,
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
                
                # Handle removing existing attachments (DB record + physical file)
                remove_ids = request.POST.getlist('remove_attachments')
                if remove_ids:
                    attachments_to_remove = AssignmentAttachment.objects.filter(
                        id__in=remove_ids, assignment=assignment
                    )
                    for att in attachments_to_remove:
                        if att.file and att.file.name:
                            abs_path = os.path.join(django_settings.MEDIA_ROOT, att.file.name)
                            if os.path.isfile(abs_path):
                                os.remove(abs_path)
                    attachments_to_remove.delete()
                    
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
                
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False).annotate(
        students_count=Count('students', distinct=True)
    ).prefetch_related('batches')
    
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
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    
    title = assignment.title
    assignment.delete()
    
    messages.success(request, f"Assignment '{title}' was deleted successfully.")
    
    return redirect('dashboard:faculty_assignments')


@login_required
@require_POST
def faculty_extend_deadline(request, pk):
    if request.user.role != 'faculty':
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    
    from dashboard.forms import DeadlineExtensionForm
    form = DeadlineExtensionForm(request.POST, instance=assignment)
    
    if form.is_valid():
        form.save()
        messages.success(request, f"Deadline for '{assignment.title}' extended successfully.")
    else:
        messages.error(request, "Invalid date provided. Please try again.")
        
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:faculty_assignments'))
