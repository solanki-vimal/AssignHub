from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from academic.models import Course
from dashboard.notifications import create_notification

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('home')

    # Fetch courses inherited via batch
    all_courses = Course.objects.filter(batches__in=request.user.enrolled_batches.all(), is_archived=False).distinct()

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

    # Calculate completed assignments and average score from Submissions
    from assignments.models import Submission
    from django.db.models import Sum
    
    submissions = Submission.objects.filter(student=request.user)
    completed_assignments = submissions.filter(status__in=['submitted', 'late', 'evaluated']).count()
    
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

@login_required
def student_courses(request):
    if request.user.role != 'student':
        return redirect('home')

    from assignments.models import Assignment, Submission

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

@login_required
def student_assignments(request):
    if request.user.role != 'student':
        return redirect('home')
        
    from assignments.models import Assignment, Submission
    assignments_qs = Assignment.objects.filter(
        batch__in=request.user.enrolled_batches.all(),
        published=True
    ).select_related('course', 'batch').order_by('due_date')
    
    all_assignments = list(assignments_qs)
    
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
    
    # Verify the assignment is legally assigned to the student (via batch)
    assignment = get_object_or_404(Assignment, pk=pk, published=True)
    if assignment.batch not in request.user.enrolled_batches.all():
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
                
                # Notify faculty
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


@login_required
def student_course_detail(request, pk):
    if request.user.role != 'student':
        return redirect('home')

    from django.shortcuts import get_object_or_404
    from assignments.models import Assignment

    # Ensure the student is actually enrolled in this course (via batch)
    all_courses = Course.objects.filter(batches__in=request.user.enrolled_batches.all(), is_archived=False).distinct()

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
