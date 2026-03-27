"""
Faculty Dashboard views.

Handles the faculty home dashboard, course management (description editing),
and student listing with per-student assignment progress and score stats.
"""

from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Course, Batch
from assignments.models import Assignment, Submission
from dashboard.forms import FacultyCourseForm, StudentSearchForm

User = get_user_model()


# =============================================================================
# Faculty Dashboard (Home)
# =============================================================================

@login_required
def faculty_dashboard(request):
    """
    Faculty home page showing:
      - Total courses, students, and active assignments
      - Per-course student counts
      - 5 most recent assignments
    Redirects other roles to their own dashboard.
    """
    if request.user.role != 'faculty':
        if request.user.role == 'admin':
            return redirect('dashboard:admin_dashboard')
        elif request.user.role == 'student':
            return redirect('dashboard:student_dashboard')
        return redirect('home')

    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False)

    # Count students per course (via batch enrollment)
    for course in faculty_courses:
        course.students_count = User.objects.filter(
            role='student',
            enrolled_batches__courses=course,
            enrolled_batches__is_archived=False
        ).distinct().count()

    total_courses = faculty_courses.count()

    # Total unique students across all faculty's courses
    total_students = User.objects.filter(
        role='student',
        enrolled_batches__courses__faculty=request.user,
        enrolled_batches__courses__is_archived=False,
        enrolled_batches__is_archived=False
    ).distinct().count()

    faculty_assignments = Assignment.objects.filter(created_by=request.user)
    active_assignments = faculty_assignments.filter(published=True).count()
    recent_assignments = faculty_assignments.order_by('-created_at')[:5]

    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'active_assignments': active_assignments,
        'faculty_courses': faculty_courses,
        'recent_assignments': recent_assignments,
    }
    return render(request, 'dashboard/faculty/dashboard.html', context)


# =============================================================================
# Faculty Courses
# =============================================================================

@login_required
def faculty_courses(request):
    """
    GET:  Lists the faculty's courses with per-course stats
          (student count, assignments, submissions, evaluation progress).
    POST: Updates a course's description via FacultyCourseForm.
    """
    if request.user.role != 'faculty':
        return redirect('home')

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id, faculty=request.user)
        form = FacultyCourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Description for {course.code} updated successfully.")
            return redirect('dashboard:faculty_courses')

    courses = Course.objects.filter(faculty=request.user, is_archived=False).prefetch_related('batches')

    # Build per-course stats (annotations across multi-level joins are complex)
    course_data = []
    for course in courses:
        student_count = User.objects.filter(
            role='student',
            enrolled_batches__courses=course,
            enrolled_batches__is_archived=False
        ).distinct().count()

        total_assignments = Assignment.objects.filter(course=course, created_by=request.user).count()
        active_assignments = Assignment.objects.filter(course=course, created_by=request.user, published=True).count()

        total_submissions = Submission.objects.filter(assignment__course=course, assignment__created_by=request.user).count()
        pending_submissions = Submission.objects.filter(
            assignment__course=course,
            assignment__created_by=request.user,
            status__in=['submitted', 'pending']
        ).count()

        # Evaluation progress
        evaluated_submissions = Submission.objects.filter(
            assignment__course=course,
            assignment__created_by=request.user,
            status='evaluated'
        ).count()
        eval_percent = round((evaluated_submissions / total_submissions) * 100) if total_submissions > 0 else 0

        course_data.append({
            'course': course,
            'student_count': student_count,
            'total_assignments': total_assignments,
            'active_assignments': active_assignments,
            'total_submissions': total_submissions,
            'pending_submissions': pending_submissions,
            'evaluated_submissions': evaluated_submissions,
            'eval_percent': eval_percent,
        })

    context = {
        'course_data': course_data,
    }
    return render(request, 'dashboard/faculty/courses.html', context)


# =============================================================================
# Faculty Students
# =============================================================================

@login_required
def faculty_students(request):
    """
    Lists students enrolled in the faculty's courses, with optional
    filtering by course and batch. Computes per-student stats:
      - Assignment completion progress (%)
      - Average score across evaluated submissions
    """
    if request.user.role != 'faculty':
        return redirect('home')

    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False)
    faculty_batches = Batch.objects.filter(courses__faculty=request.user, is_archived=False).distinct()

    # Optional filters from query params
    selected_course_id = request.GET.get('course')
    selected_batch_id = request.GET.get('batch')
    search_form = StudentSearchForm(request.GET)

    # Base queryset: students in batches that have this faculty's courses
    enrolled_students = User.objects.filter(
        role='student',
        enrolled_batches__courses__faculty=request.user,
        enrolled_batches__courses__is_archived=False,
        enrolled_batches__is_archived=False
    )

    # Apply optional filters
    if selected_course_id:
        enrolled_students = enrolled_students.filter(enrolled_batches__courses__id=selected_course_id)
    if selected_batch_id:
        enrolled_students = enrolled_students.filter(enrolled_batches__id=selected_batch_id)

    enrolled_students = enrolled_students.distinct().prefetch_related('enrolled_batches', 'enrolled_batches__courses')

    # Compute per-student stats
    for student in enrolled_students:
        student_batches = student.enrolled_batches.all()

        total_assignments = Assignment.objects.filter(
            created_by=request.user,
            published=True,
            batch__in=student_batches
        ).count()

        submissions = Submission.objects.filter(
            student=student,
            assignment__created_by=request.user,
            assignment__published=True,
            assignment__batch__in=student_batches
        )

        # Completion progress
        completed = submissions.filter(status__in=['submitted', 'late', 'evaluated']).count()
        progress_pct = round((completed / total_assignments) * 100) if total_assignments > 0 else 0

        # Average score across evaluated submissions
        evaluated_subs = submissions.filter(status='evaluated', marks_obtained__isnull=False)
        if evaluated_subs.exists():
            total_obtained = sum(s.marks_obtained for s in evaluated_subs)
            total_max = sum(s.assignment.max_marks for s in evaluated_subs)
            avg_score = round((total_obtained / total_max) * 100) if total_max > 0 else "--"
        else:
            avg_score = "--"

        # Attach stats to the student object for template access
        student.faculty_total_assignments = total_assignments
        student.faculty_completed_assignments = completed
        student.faculty_progress_pct = progress_pct
        student.faculty_avg_score = avg_score

    context = {
        'students': enrolled_students,
        'faculty_courses': faculty_courses,
        'faculty_batches': faculty_batches,
        'selected_course': selected_course_id,
        'selected_batch': selected_batch_id,
        'search_form': search_form,
    }
    return render(request, 'dashboard/faculty/students.html', context)
