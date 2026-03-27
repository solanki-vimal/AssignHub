"""
Faculty Submission Review & Grading views.

Handles viewing all student submissions for an assignment and
evaluating individual submissions with marks and feedback.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from assignments.models import Assignment, Submission
from dashboard.notifications import create_notification

User = get_user_model()


# =============================================================================
# Submission List (Per Assignment)
# =============================================================================

@login_required
def faculty_submission_list(request, assignment_pk):
    """
    Lists all students in the assignment's batch alongside their submission status.
    Combines actual submissions with "pending" placeholders for students
    who haven't submitted yet, giving a complete class overview.
    """
    if request.user.role != 'faculty':
        return redirect('home')

    assignment = get_object_or_404(Assignment, pk=assignment_pk, created_by=request.user)

    # All students enrolled in this assignment's batch
    enrolled_students = User.objects.filter(
        role='student',
        enrolled_batches=assignment.batch,
        is_active=True
    ).distinct().order_by('first_name', 'email')

    # Map existing submissions by student ID for fast lookup
    actual_submissions = {
        s.student_id: s
        for s in Submission.objects.filter(assignment=assignment).prefetch_related('files')
    }

    # Build combined list: real submission or "pending" placeholder
    combined_submissions = []
    submitted_count = 0
    evaluated_count = 0
    late_count = 0

    for student in enrolled_students:
        sub = actual_submissions.get(student.id)
        if sub:
            combined_submissions.append({
                'student': student,
                'submission': sub,
                'status': sub.status,
                'files_count': sub.files.count(),
                'marks': sub.marks_obtained,
                'pk': sub.pk
            })
            if sub.status == 'submitted':
                submitted_count += 1
            elif sub.status == 'evaluated':
                evaluated_count += 1
            elif sub.status == 'late':
                late_count += 1
        else:
            # Student hasn't submitted — show as pending
            combined_submissions.append({
                'student': student,
                'submission': None,
                'status': 'pending',
                'files_count': 0,
                'marks': None,
                'pk': None
            })

    total_students = len(combined_submissions)
    pending_count = total_students - (submitted_count + evaluated_count + late_count)

    context = {
        'assignment': assignment,
        'combined_submissions': combined_submissions,
        'submitted_count': submitted_count,
        'pending_count': pending_count,
        'evaluated_count': evaluated_count,
        'total_students': total_students,
    }
    return render(request, 'dashboard/faculty/submission_list.html', context)


# =============================================================================
# Submission Detail & Grading
# =============================================================================

@login_required
def faculty_submission_detail(request, submission_pk):
    """
    GET:  Shows a student's submission with uploaded files.
    POST: Saves marks and remarks, sets status to 'evaluated',
          and notifies the student about the evaluation result.
    """
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

                # Notify the student about the evaluation
                create_notification(
                    user=submission.student,
                    title="Evaluation Released",
                    message=f"Your submission for '{submission.assignment.title}' has been evaluated. Marks obtained: {marks_val}/{submission.assignment.max_marks}",
                    link=f"/dashboard/student/assignments/{submission.assignment.pk}/",
                    notification_type='evaluation'
                )

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
