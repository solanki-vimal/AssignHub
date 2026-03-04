from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from academic.models import Course, Batch
import re

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('home')

    User = get_user_model()
    context = {
        'total_users': User.objects.count(),
        'active_courses': Course.objects.count(),
        'total_batches': Batch.objects.count(),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def admin_courses(request):
    if request.user.role != 'admin':
        return redirect('home')
        
    User = get_user_model()
    DEPARTMENTS = [
        ('CE', 'Computer Engineering'),
        ('IT', 'Information Technology'),
        ('EC', 'Electronics Communication'),
        ('ME', 'Mechanical Engineering'),
        ('CL', 'Civil Engineering')
    ]
    SEMESTERS = list(range(1, 9))
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
                Course.objects.create(
                    code=code,
                    name=name,
                    semester=semester_num,
                    department=department,
                    is_active=(status == 'active'),
                    faculty=faculty
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

@login_required
def admin_manage_course_students(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
        
    User = get_user_model()
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')
        
        if student_id:
            student = get_object_or_404(User, pk=student_id, role='student')
            if action == 'add':
                course.students.add(student)
                messages.success(request, f"Added student {student.first_name} to {course.name}.")
            elif action == 'remove':
                course.students.remove(student)
                messages.success(request, f"Removed student {student.first_name} from {course.name}.")
                
        return redirect('dashboard:admin_manage_course_students', pk=pk)
        
    enrolled_students = course.students.all().order_by('first_name')
    available_students = User.objects.filter(role='student').exclude(enrolled_courses=course).order_by('first_name')
    
    context = {
        'course': course,
        'enrolled_students': enrolled_students,
        'available_students': available_students
    }
    return render(request, 'dashboard/admin/manage_course_students.html', context)

@login_required
def admin_batches(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    User = get_user_model()
    SEMESTERS = list(range(1, 9))
    faculty_list = User.objects.filter(role='faculty').order_by('first_name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status', 'active')
        semester = request.POST.get('semester')
        coordinator_id = request.POST.get('coordinator_id')
        
        if not all([name, start_date, end_date]):
            messages.error(request, "Name and dates are required.")
        else:
            try:
                s_year = start_date.split('-')[0]
                e_year = end_date.split('-')[0][-2:]
                academic_year = f"{s_year}-{e_year}"
                coordinator = User.objects.get(pk=coordinator_id) if coordinator_id else None
                semester_num = int(semester) if semester else None
                
                if Batch.objects.filter(name=name, academic_year=academic_year).exists():
                    messages.error(request, f"Batch {name} for {academic_year} already exists.")
                else:
                    Batch.objects.create(
                        name=name,
                        academic_year=academic_year,
                        is_active=(status == 'active'),
                        semester=semester_num,
                        coordinator=coordinator
                    )
                    messages.success(request, f"Batch {name} added successfully.")
            except Exception as e:
                messages.error(request, f"Error creating batch: {str(e)}")
        return redirect('dashboard:admin_batches')
    show_archived = request.GET.get('show_archived', 'false') == 'true'
    batches = Batch.objects.select_related('coordinator').prefetch_related('students').filter(is_archived=show_archived).order_by('-id')
    context = {
        'batches': batches,
        'semesters': SEMESTERS,
        'faculty_list': faculty_list,
        'show_archived': show_archived,
    }
    return render(request, 'dashboard/admin/batches.html', context)

@login_required
def admin_batch_edit(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    User = get_user_model()
    batch = get_object_or_404(Batch, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status', 'active')
        semester = request.POST.get('semester')
        coordinator_id = request.POST.get('coordinator_id')
        
        if not all([name, start_date, end_date]):
            messages.error(request, "Name and dates are required.")
        else:
            try:
                s_year = start_date.split('-')[0]
                e_year = end_date.split('-')[0][-2:]
                academic_year = f"{s_year}-{e_year}"
                
                if Batch.objects.filter(name=name, academic_year=academic_year).exclude(pk=pk).exists():
                    messages.error(request, f"Batch {name} for {academic_year} already exists.")
                else:
                    batch.name = name
                    batch.academic_year = academic_year
                    batch.is_active = (status == 'active')
                    batch.semester = int(semester) if semester else None
                    batch.coordinator = User.objects.get(pk=coordinator_id) if coordinator_id else None
                    batch.save()
                    messages.success(request, f"Batch {name} updated successfully.")
            except Exception as e:
                messages.error(request, f"Error updating batch: {str(e)}")
                
    return redirect('dashboard:admin_batches')

@login_required
def admin_batch_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    batch = get_object_or_404(Batch, pk=pk)
    
    if request.method == 'POST':
        name = batch.name
        batch.delete()
        messages.success(request, f"Batch {name} deleted successfully.")
        
    return redirect('dashboard:admin_batches')

@login_required
def admin_batch_archive(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action', 'archive')
        if action == 'unarchive':
            batch.is_archived = False
            messages.success(request, f"Batch {batch.name} unarchived successfully.")
        else:
            batch.is_archived = True
            messages.success(request, f"Batch {batch.name} archived successfully.")
        batch.save()
        
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:admin_batches'))

@login_required
def admin_manage_batch_students(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
        
    User = get_user_model()
    batch = get_object_or_404(Batch, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')
        
        if student_id:
            student = get_object_or_404(User, pk=student_id, role='student')
            if action == 'add':
                batch.students.add(student)
                messages.success(request, f"Added student {student.first_name} to {batch.name}.")
            elif action == 'remove':
                batch.students.remove(student)
                messages.success(request, f"Removed student {student.first_name} from {batch.name}.")
                
        return redirect('dashboard:admin_manage_batch_students', pk=pk)
        
    enrolled_students = batch.students.all().order_by('first_name')
    available_students = User.objects.filter(role='student').exclude(enrolled_batches=batch).order_by('first_name')
    
    context = {
        'batch': batch,
        'enrolled_students': enrolled_students,
        'available_students': available_students
    }
    return render(request, 'dashboard/admin/manage_batch_students.html', context)

@login_required
def faculty_dashboard(request):
    return render(request, 'dashboard/faculty_dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')
