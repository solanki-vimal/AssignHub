from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from academic.models import Course

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('home')

    # Fetch courses explicitly enrolled or inherited via batch
    student_courses = request.user.enrolled_courses.filter(is_archived=False)
    batch_courses = Course.objects.filter(batches__in=request.user.enrolled_batches.all(), is_archived=False)
    all_courses = (student_courses | batch_courses).distinct()

    total_courses = all_courses.count()

    # Fetch assignments related to these courses that are published
    from assignments.models import Assignment
    assignments = Assignment.objects.filter(
        batch__in=request.user.enrolled_batches.all(),
        published=True
    ).order_by('due_date')

    # Total unsubmitted assignments (simplified logic for now: all published batch assignments)
    # We will refine 'upcoming' vs 'completed' once the Submission model is created.
    upcoming_assignments = assignments.count()
    recent_assignments = assignments[:5]

    context = {
        'total_courses': total_courses,
        'upcoming_assignments': upcoming_assignments,
        'recent_assignments': recent_assignments,
    }
    return render(request, 'dashboard/student/dashboard.html', context)

@login_required
def student_courses(request):
    if request.user.role != 'student':
        return redirect('home')

    from assignments.models import Assignment, Submission

    student_courses_qs = request.user.enrolled_courses.filter(is_archived=False)
    batch_courses_qs = Course.objects.filter(batches__in=request.user.enrolled_batches.all(), is_archived=False)
    all_courses = (student_courses_qs | batch_courses_qs).distinct().select_related('faculty')

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

@login_required
def student_assignments(request):
    if request.user.role != 'student':
        return redirect('home')
        
    from assignments.models import Assignment, Submission
    assignments_qs = Assignment.objects.filter(
        batch__in=request.user.enrolled_batches.all(),
        published=True
    ).select_related('course', 'batch').order_by('due_date')
    
    # Also include assignments from directly enrolled courses
    direct_course_assignments = Assignment.objects.filter(
        course__in=request.user.enrolled_courses.all(),
        published=True
    ).exclude(id__in=assignments_qs).select_related('course', 'batch')
    
    all_assignments = list(assignments_qs) + list(direct_course_assignments)
    
    # Fetch all submissions for this student in one query
    submission_map = {
        s.assignment_id: s.status
        for s in Submission.objects.filter(
            student=request.user,
            assignment_id__in=[a.id for a in all_assignments]
        )
    }
    
    # Attach the submission_status to each assignment object
    for assignment in all_assignments:
        assignment.submission_status = submission_map.get(assignment.id, 'pending')
    
    context = {
        'assignments': all_assignments,
    }
    return render(request, 'dashboard/student/assignments.html', context)

from django.shortcuts import get_object_or_404
from django.contrib import messages
from assignments.models import Submission, SubmissionFile

@login_required
def student_assignment_detail(request, pk):
    if request.user.role != 'student':
        return redirect('home')

    from assignments.models import Assignment
    
    # Verify the assignment is legally assigned to the student (either directly or via batch)
    assignment = get_object_or_404(Assignment, pk=pk, published=True)
    in_batch = assignment.batch in request.user.enrolled_batches.all()
    in_course = hasattr(assignment, 'course') and assignment.course in request.user.enrolled_courses.all()
    
    if not (in_batch or in_course):
        messages.error(request, "You do not have permission to view this assignment.")
        return redirect('dashboard:student_assignments')
        
    submission, created = Submission.objects.get_or_create(
        assignment=assignment,
        student=request.user
    )
    
    if request.method == 'POST':
        # Don't allow submission if evaluated (or perhaps after deadline if strictly enforced)
        if submission.status == 'evaluated':
            messages.error(request, 'This assignment has already been evaluated.')
            return redirect('dashboard:student_assignment_detail', pk=pk)
            
        files = request.FILES.getlist('files')
        if not files:
            messages.error(request, 'Please select at least one file to upload.')
        else:
            for file in files:
                valid = True
                # In a real app we would check file types / size here as defined in Assignment model
                # e.g., if assignment.allowed_file_types != 'all' ...
                
                if file.size > (assignment.max_file_size_mb * 1024 * 1024):
                    messages.error(request, f"File {file.name} exceeds the {assignment.max_file_size_mb}MB limit.")
                    valid = False
                    
                if valid:
                    SubmissionFile.objects.create(submission=submission, file=file)
            
            # Simple assumption: first file upload turns status to 'submitted'
            if submission.status == 'pending':
                submission.status = 'submitted'
                submission.save()
            messages.success(request, 'Files successfully uploaded.')
            return redirect('dashboard:student_assignment_detail', pk=pk)

    context = {
        'assignment': assignment,
        'submission': submission,
    }
    return render(request, 'dashboard/student/assignment_detail.html', context)


@login_required
def student_course_detail(request, pk):
    if request.user.role != 'student':
        return redirect('home')

    from django.shortcuts import get_object_or_404
    from assignments.models import Assignment

    # Ensure the student is actually enrolled in this course (via batch or direct)
    student_courses = request.user.enrolled_courses.filter(is_archived=False)
    batch_courses = Course.objects.filter(batches__in=request.user.enrolled_batches.all(), is_archived=False)
    all_courses = (student_courses | batch_courses).distinct()

    course = get_object_or_404(all_courses, pk=pk)

    # Get published assignments for this course that belong to the student's batches
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
