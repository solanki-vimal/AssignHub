"""
Student Dashboard views.

Handles the student home dashboard, course listing with progress stats,
assignment listing with submission status, individual assignment detail
with file upload/submission, and course detail pages.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Course
from assignments.models import Assignment, Submission, SubmissionFile
from dashboard.notifications import create_notification


# =============================================================================
# Student Dashboard (Home)
# =============================================================================

@login_required
def student_dashboard(request):
    """
    Student home page showing:
      - Total enrolled courses
      - Upcoming (incomplete) and completed assignment counts
      - Average score across evaluated submissions
      - 5 nearest-due upcoming assignments
    """
    if request.user.role != 'student':
        return redirect('home')

    # Courses inherited via batch enrollment
    all_courses = Course.objects.filter(
        batches__in=request.user.enrolled_batches.all(),
        is_archived=False
    ).distinct()
    total_courses = all_courses.count()

    submissions = Submission.objects.filter(student=request.user)
    completed_submissions = submissions.filter(status__in=['submitted', 'late', 'evaluated'])
    completed_assignment_ids = completed_submissions.values_list('assignment_id', flat=True)
    completed_assignments = completed_submissions.count()

    # Upcoming = published assignments not yet submitted, ordered by due date
    upcoming_assignments_qs = Assignment.objects.filter(
        batch__in=request.user.enrolled_batches.all(),
        published=True
    ).exclude(id__in=completed_assignment_ids).order_by('due_date')

    upcoming_assignments = upcoming_assignments_qs.count()
    recent_assignments = upcoming_assignments_qs[:5]

    # Calculate average score across evaluated submissions
    evaluated_submissions = submissions.filter(status='evaluated', marks_obtained__isnull=False)
    if evaluated_submissions.exists():
        total_obtained = sum(s.marks_obtained for s in evaluated_submissions)
        total_max = sum(s.assignment.max_marks for s in evaluated_submissions)
        average_score = round((total_obtained / total_max) * 100) if total_max > 0 else "--"
    else:
        average_score = "--"

    context = {
        'total_courses': total_courses,
        'upcoming_assignments': upcoming_assignments,
        'recent_assignments': recent_assignments,
        'completed_assignments': completed_assignments,
        'average_score': average_score,
    }
    return render(request, 'dashboard/student/dashboard.html', context)


# =============================================================================
# Student Courses
# =============================================================================

@login_required
def student_courses(request):
    """
    Lists all enrolled courses with per-course progress:
    total assignments vs. submitted assignments and completion percentage.
    """
    if request.user.role != 'student':
        return redirect('home')

    all_courses = Course.objects.filter(
        batches__in=request.user.enrolled_batches.all(),
        is_archived=False
    ).distinct().select_related('faculty')

    course_data = []
    for course in all_courses:
        total_assignments = Assignment.objects.filter(
            course=course,
            published=True,
            batch__in=request.user.enrolled_batches.all()
        ).count()

        submitted = Submission.objects.filter(
            assignment__course=course,
            assignment__published=True,
            assignment__batch__in=request.user.enrolled_batches.all(),
            student=request.user,
            status__in=['submitted', 'late', 'evaluated']
        ).count()

        progress_pct = round((submitted / total_assignments) * 100) if total_assignments > 0 else 0

        course_data.append({
            'course': course,
            'total_assignments': total_assignments,
            'submitted': submitted,
            'progress_pct': progress_pct,
        })

    context = {
        'course_data': course_data,
    }
    return render(request, 'dashboard/student/courses.html', context)


# =============================================================================
# Student Assignments List
# =============================================================================

@login_required
def student_assignments(request):
    """
    Lists all published assignments for the student's enrolled batches.
    Efficiently fetches submission statuses in a single query (submission_map).
    """
    if request.user.role != 'student':
        return redirect('home')

    assignments_qs = Assignment.objects.filter(
        batch__in=request.user.enrolled_batches.all(),
        published=True
    ).select_related('course', 'batch').order_by('due_date')

    all_assignments = list(assignments_qs)

    # Batch-fetch all submissions for these assignments in one query
    submission_map = {
        s.assignment_id: s.status
        for s in Submission.objects.filter(
            student=request.user,
            assignment_id__in=[a.id for a in all_assignments]
        )
    }

    # Attach submission status to each assignment for template access
    for assignment in all_assignments:
        assignment.submission_status = submission_map.get(assignment.id, 'pending')

    context = {
        'assignments': all_assignments,
    }
    return render(request, 'dashboard/student/assignments.html', context)


# =============================================================================
# Student Assignment Detail (View + Submit)
# =============================================================================

@login_required
def student_assignment_detail(request, pk):
    """
    GET:  Shows assignment details and existing submission (or creates a pending one).
    POST: Handles file upload for submission.
          Validates file size, sets status to 'submitted', and notifies faculty.
          Blocks re-submission on already-evaluated assignments.
    """
    if request.user.role != 'student':
        return redirect('home')

    # Verify student has access to this assignment via batch enrollment
    assignment = get_object_or_404(Assignment, pk=pk, published=True)
    if assignment.batch not in request.user.enrolled_batches.all():
        messages.error(request, "You do not have permission to view this assignment.")
        return redirect('dashboard:student_assignments')

    # Get or create the student's submission record
    submission, created = Submission.objects.get_or_create(
        assignment=assignment,
        student=request.user
    )

    if request.method == 'POST':
        # Block submission on already-evaluated assignments
        if submission.status == 'evaluated':
            messages.error(request, 'This assignment has already been evaluated.')
            return redirect('dashboard:student_assignment_detail', pk=pk)

        files = request.FILES.getlist('files')
        if not files:
            messages.error(request, 'Please select at least one file to upload.')
        else:
            has_valid_upload = False
            for file in files:
                # Validate file size against assignment limit
                if file.size > (assignment.max_file_size_mb * 1024 * 1024):
                    messages.error(request, f"File {file.name} exceeds the {assignment.max_file_size_mb}MB limit.")
                else:
                    SubmissionFile.objects.create(submission=submission, file=file)
                    has_valid_upload = True

            if has_valid_upload:
                # Only change status on first submission (pending → submitted)
                if submission.status == 'pending':
                    submission.status = 'submitted'
                    submission.save()

                    # Notify the faculty who created the assignment
                    create_notification(
                        user=assignment.created_by,
                        title="New Submission",
                        message=f"{request.user.get_full_name() or request.user.email} submitted '{assignment.title}'.",
                        link=f"/dashboard/faculty/submissions/{submission.pk}/",
                        notification_type='submission'
                    )

                messages.success(request, 'Files successfully uploaded.')
            return redirect('dashboard:student_assignment_detail', pk=pk)

    context = {
        'assignment': assignment,
        'submission': submission,
    }
    return render(request, 'dashboard/student/assignment_detail.html', context)


# =============================================================================
# Student Course Detail
# =============================================================================

@login_required
def student_course_detail(request, pk):
    """Shows a single course's details with all published assignments for the student."""
    if request.user.role != 'student':
        return redirect('home')

    # Verify enrollment: only show courses the student has access to
    all_courses = Course.objects.filter(
        batches__in=request.user.enrolled_batches.all(),
        is_archived=False
    ).distinct()
    course = get_object_or_404(all_courses, pk=pk)

    # Published assignments for this course in the student's batches
    assignments = Assignment.objects.filter(
        course=course,
        published=True,
        batch__in=request.user.enrolled_batches.all()
    ).prefetch_related('attachments').order_by('due_date')

    context = {
        'course': course,
        'assignments': assignments,
    }
    return render(request, 'dashboard/student/course_detail.html', context)
