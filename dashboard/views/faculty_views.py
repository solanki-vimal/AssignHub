from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from academic.models import Course, Batch
from assignments.models import Assignment

@login_required
def faculty_dashboard(request):
    if request.user.role != 'faculty':
        if request.user.role == 'admin':
            return redirect('dashboard:admin_dashboard')
        elif request.user.role == 'student':
            return redirect('dashboard:student_dashboard')
        return redirect('home')

    # Fetch faculty-specific data
    faculty_courses = Course.objects.filter(faculty=request.user, is_archived=False).annotate(
        students_count=Count('students')
    )
    
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
        
        course_data.append({
            'course': course,
            'student_count': student_count,
            'total_assignments': total_assignments,
            'active_assignments': active_assignments,
            'total_submissions': total_submissions,
            'pending_submissions': pending_submissions,
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
    
    # Get all unique students enrolled in batches associated with this faculty's courses
    User = get_user_model()
    enrolled_students = User.objects.filter(
        role='student',
        enrolled_batches__courses__faculty=request.user,
        enrolled_batches__courses__is_archived=False,
        enrolled_batches__is_archived=False
    ).distinct().prefetch_related('enrolled_batches', 'enrolled_batches__courses')
    
    context = {
        'students': enrolled_students,
        'faculty_courses': faculty_courses,
        'faculty_batches': faculty_batches,
    }
    return render(request, 'dashboard/faculty/students.html', context)
