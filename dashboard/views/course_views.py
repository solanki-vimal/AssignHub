import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Course
from academic.constants import DEPARTMENTS, SEMESTERS
from dashboard.notifications import create_notification

@login_required
def admin_courses(request):
    if request.user.role != 'admin':
        return redirect('home')
        
    User = get_user_model()
    faculty_list = User.objects.filter(role='faculty').order_by('first_name')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        semester = request.POST.get('semester')
        department = request.POST.get('department')
        status = request.POST.get('status', 'active')
        faculty_id = request.POST.get('faculty_id')
        
        if not all([code, name, semester, department]):
            messages.error(request, "All required fields must be filled.")
        elif Course.objects.filter(code=code).exists():
            messages.error(request, f"Course with code {code} already exists.")
        else:
            try:
                semester_num = int(re.search(r'\d+', str(semester)).group()) if not str(semester).isdigit() else int(semester)
                faculty = User.objects.get(pk=faculty_id) if faculty_id else None
                course = Course.objects.create(
                    code=code,
                    name=name,
                    semester=semester_num,
                    department=department,
                    is_active=(status == 'active'),
                    faculty=faculty
                )
                
                if faculty:
                    create_notification(
                        user=faculty,
                        title="New Course Assignment",
                        message=f"You have been assigned to teach {code} - {name}.",
                        link="/dashboard/faculty/courses/",
                        notification_type='system'
                    )
                    
                messages.success(request, f"Course {code} added successfully.")
            except Exception as e:
                messages.error(request, f"Error creating course: {str(e)}")
        return redirect('dashboard:admin_courses')
    show_archived = request.GET.get('show_archived', 'false') == 'true'
    courses = Course.objects.select_related('faculty').filter(is_archived=show_archived)
    context = {
        'courses': courses,
        'departments': DEPARTMENTS,
        'semesters': SEMESTERS,
        'faculty_list': faculty_list,
        'show_archived': show_archived,
    }
    return render(request, 'dashboard/admin/courses.html', context)

@login_required
def admin_course_edit(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    User = get_user_model()
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        semester = request.POST.get('semester')
        department = request.POST.get('department')
        status = request.POST.get('status', 'active')
        faculty_id = request.POST.get('faculty_id')
        
        if not all([code, name, semester, department]):
            messages.error(request, "All required fields must be filled.")
        elif Course.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, f"Course with code {code} already exists.")
        else:
            try:
                semester_num = int(re.search(r'\d+', semester).group()) if not semester.isdigit() else int(semester)
                course.code = code
                course.name = name
                course.semester = semester_num
                course.department = department
                course.is_active = (status == 'active')
                # Notify if faculty changed
                if faculty_id and str(course.faculty_id) != str(faculty_id):
                    new_faculty = User.objects.get(pk=faculty_id)
                    create_notification(
                        user=new_faculty,
                        title="New Course Assignment",
                        message=f"You have been assigned to teach {code} - {name}.",
                        link="/dashboard/faculty/courses/",
                        notification_type='system'
                    )
                
                course.faculty = User.objects.get(pk=faculty_id) if faculty_id else None
                course.save()
                
                messages.success(request, f"Course {code} updated successfully.")
            except Exception as e:
                messages.error(request, f"Error updating course: {str(e)}")
                
    return redirect('dashboard:admin_courses')

@login_required
def admin_course_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        code = course.code
        course.delete()
        messages.success(request, f"Course {code} deleted successfully.")
    return redirect('dashboard:admin_courses')

@login_required
def admin_course_archive(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action', 'archive')
        if action == 'unarchive':
            course.is_archived = False
            messages.success(request, f"Course {course.code} unarchived successfully.")
        else:
            course.is_archived = True
            messages.success(request, f"Course {course.code} archived successfully.")
        course.save()
        
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:admin_courses'))

