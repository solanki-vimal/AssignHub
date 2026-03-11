import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings as django_settings
from assignments.models import Assignment, Submission, SubmissionFile


@login_required
def faculty_submission_list(request, assignment_pk):
    """List all student submissions for a given assignment."""
    if request.user.role != 'faculty':
        return redirect('home')

    assignment = get_object_or_404(Assignment, pk=assignment_pk, created_by=request.user)

    submissions = Submission.objects.filter(
        assignment=assignment
    ).select_related('student').prefetch_related('files').order_by('student__first_name')

    submitted_count = submissions.filter(status__in=['submitted', 'late', 'evaluated']).count()
    pending_count = submissions.filter(status='pending').count()
    evaluated_count = submissions.filter(status='evaluated').count()
    total_students = assignment.batch.students.count() if assignment.batch else 0

    context = {
        'assignment': assignment,
        'submissions': submissions,
        'submitted_count': submitted_count,
        'pending_count': pending_count,
        'evaluated_count': evaluated_count,
        'total_students': total_students,
    }
    return render(request, 'dashboard/faculty/submission_list.html', context)


@login_required
def faculty_submission_detail(request, submission_pk):
    """View a single student's submission, and grade/evaluate it."""
    if request.user.role != 'faculty':
        return redirect('home')

    submission = get_object_or_404(
        Submission,
        pk=submission_pk,
        assignment__created_by=request.user
    )
    submission_files = submission.files.all()

    if request.method == 'POST':
        marks = request.POST.get('marks_obtained', '').strip()
        remarks = request.POST.get('faculty_remarks', '').strip()

        try:
            marks_val = float(marks) if marks else None
            if marks_val is not None and marks_val > submission.assignment.max_marks:
                messages.error(request, f"Marks cannot exceed {submission.assignment.max_marks}.")
            else:
                submission.marks_obtained = marks_val
                submission.faculty_remarks = remarks
                submission.status = 'evaluated'
                submission.save()
                messages.success(request, f"Submission by {submission.student.get_full_name() or submission.student.email} evaluated successfully.")
                return redirect('dashboard:faculty_submission_list', assignment_pk=submission.assignment.pk)
        except ValueError:
            messages.error(request, "Please enter a valid number for marks.")

    context = {
        'submission': submission,
        'submission_files': submission_files,
        'assignment': submission.assignment,
    }
    return render(request, 'dashboard/faculty/submission_detail.html', context)
