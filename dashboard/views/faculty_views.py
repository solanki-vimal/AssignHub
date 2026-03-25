from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from academic.models import Course, Batch
from assignments.models import Assignment
from dashboard.forms import FacultyCourseForm

@login_required
def faculty_dashboard(request):
    if request.user.role != 'faculty':
        if request.user.role == 'admin':
            return redirect('dashboard:admin_dashboard')
        elif request.user.role == 'student':
            return redirect('dashboard:student_dashboard')
        return redirect('home')

    # Fetch faculty-specific data
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False)
    
    User = get_user_model()
    for course in faculty_courses:
        course.students_count = User.objects.filter(
            role='student',
            enrolled_batches__courses=course,
            enrolled_batches__is_archived=False
        ).distinct().count()
    
    total_courses = faculty_courses.count()
    
    # Calculate total unique students via Batch mapping
    User = get_user_model()
    total_students = User.objects.filter(
        role='student',
        enrolled_batches__courses__faculty=request.user,
        enrolled_batches__courses__is_archived=False,
        enrolled_batches__is_archived=False
    ).distinct().count()
    
    # Fetch real assignment data
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

@login_required
def faculty_courses(request):
    if request.user.role != 'faculty':
        return redirect('home')
    
    if request.method == 'POST':
        from django.shortcuts import get_object_or_404
        from django.contrib import messages
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id, faculty=request.user)
        form = FacultyCourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Description for {course.code} updated successfully.")
            return redirect('dashboard:faculty_courses')

    User = get_user_model()
    from assignments.models import Submission
    
    courses = Course.objects.filter(faculty=request.user, is_archived=False).prefetch_related('batches')
    
    # Build per-course stats manually (annotations across multi-level joins are complex)
    course_data = []
    for course in courses:
        # Count students enrolled in batches tied to this course (same logic as faculty_students)
        student_count = User.objects.filter(
            role='student',
            enrolled_batches__courses=course,
            enrolled_batches__is_archived=False
        ).distinct().count()
        
        # Count assignments for this course
        total_assignments = Assignment.objects.filter(course=course, created_by=request.user).count()
        active_assignments = Assignment.objects.filter(course=course, created_by=request.user, published=True).count()
        
        # Count submissions for this course's assignments
        total_submissions = Submission.objects.filter(assignment__course=course, assignment__created_by=request.user).count()
        pending_submissions = Submission.objects.filter(
            assignment__course=course,
            assignment__created_by=request.user,
            status__in=['submitted', 'pending']
        ).count()
        
        # Count evaluated submissions
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

@login_required
def faculty_students(request):
    if request.user.role != 'faculty':
        return redirect('home')
        
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False)
    faculty_batches = Batch.objects.filter(courses__faculty=request.user, is_archived=False).distinct()
    
    selected_course_id = request.GET.get('course')
    selected_batch_id = request.GET.get('batch')
    
    from dashboard.forms import StudentSearchForm
    search_form = StudentSearchForm(request.GET)
    
    # Get all students enrolled in batches associated with this faculty's courses
    User = get_user_model()
    enrolled_students = User.objects.filter(
        role='student',
        enrolled_batches__courses__faculty=request.user,
        enrolled_batches__courses__is_archived=False,
        enrolled_batches__is_archived=False
    )
    
    if selected_course_id:
        enrolled_students = enrolled_students.filter(enrolled_batches__courses__id=selected_course_id)
    if selected_batch_id:
        enrolled_students = enrolled_students.filter(enrolled_batches__id=selected_batch_id)
        
    enrolled_students = enrolled_students.distinct().prefetch_related('enrolled_batches', 'enrolled_batches__courses')
    
    from assignments.models import Assignment, Submission
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
        
        completed = submissions.filter(status__in=['submitted', 'late', 'evaluated']).count()
        progress_pct = round((completed / total_assignments) * 100) if total_assignments > 0 else 0
        
        evaluated_subs = submissions.filter(status='evaluated', marks_obtained__isnull=False)
        if evaluated_subs.exists():
            total_obtained = sum(s.marks_obtained for s in evaluated_subs)
            total_max = sum(s.assignment.max_marks for s in evaluated_subs)
            avg_score = round((total_obtained / total_max) * 100) if total_max > 0 else "--"
        else:
            avg_score = "--"
            
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
