"""
Admin Batch Management views.

Handles batch CRUD, archive/unarchive, and managing the M2M relationships
between batches and students/courses. Syncs User.batch and User.semester
fields whenever student enrollment changes.
"""

from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Course, Batch
from academic.constants import SEMESTERS
from dashboard.notifications import create_notification

User = get_user_model()


# =============================================================================
# List & Create Batches
# =============================================================================

@login_required
def admin_batches(request):
    """
    GET:  Lists all batches (active or archived based on query param).
    POST: Creates a new batch via AdminBatchForm.
    """
    if request.user.role != 'admin':
        return redirect('home')

    from dashboard.forms import AdminBatchForm

    if request.method == 'POST':
        form = AdminBatchForm(request.POST, prefix='add')
        if form.is_valid():
            try:
                batch = form.save()
                messages.success(request, f"Batch {batch.name} added successfully.")
            except Exception as e:
                messages.error(request, f"Error creating batch: {str(e)}")
            return redirect('dashboard:admin_batches')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AdminBatchForm(prefix='add')

    # Toggle between active and archived batches via query param
    show_archived = request.GET.get('show_archived', 'false') == 'true'
    batches = Batch.objects.prefetch_related('students', 'courses') \
        .annotate(course_count=Count('courses', distinct=True)) \
        .filter(is_archived=show_archived) \
        .order_by('-id')

    # Empty form for the edit modal
    edit_form = AdminBatchForm(prefix='edit')

    context = {
        'batches': batches,
        'semesters': SEMESTERS,
        'show_archived': show_archived,
        'form': form,
        'edit_form': edit_form,
    }
    return render(request, 'dashboard/admin/batches.html', context)


# =============================================================================
# Edit Batch
# =============================================================================

@login_required
def admin_batch_edit(request, pk):
    """Updates a batch. Name changes are synced to User.batch via AdminBatchForm.save()."""
    if request.user.role != 'admin':
        return redirect('home')

    batch = get_object_or_404(Batch, pk=pk)
    from dashboard.forms import AdminBatchForm

    if request.method == 'POST':
        form = AdminBatchForm(request.POST, instance=batch, prefix='edit')
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Batch {batch.name} updated successfully.")
            except Exception as e:
                messages.error(request, f"Error updating batch: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return redirect('dashboard:admin_batches')


# =============================================================================
# Delete Batch
# =============================================================================

@login_required
def admin_batch_delete(request, pk):
    """Permanently deletes a batch and all related data."""
    if request.user.role != 'admin':
        return redirect('home')

    batch = get_object_or_404(Batch, pk=pk)

    if request.method == 'POST':
        name = batch.name
        batch.delete()
        messages.success(request, f"Batch {name} deleted successfully.")

    return redirect('dashboard:admin_batches')


# =============================================================================
# Archive / Unarchive Batch
# =============================================================================

@login_required
def admin_batch_archive(request, pk):
    """Toggles a batch's archive status based on the 'action' POST param."""
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


# =============================================================================
# Manage Students in a Batch
# =============================================================================

@login_required
def admin_manage_batch_students(request, pk):
    """
    GET:  Shows enrolled students and available (unassigned) students.
    POST: Adds or removes a student from the batch.
          Syncs User.batch and User.semester fields on every change.
    """
    if request.user.role != 'admin':
        return redirect('home')

    batch = get_object_or_404(Batch, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')

        if student_id:
            student = get_object_or_404(User, pk=student_id, role='student')
            if action == 'add':
                # Add to M2M and sync User CharField fields
                batch.students.add(student)
                student.batch = batch.name
                if batch.semester:
                    student.semester = batch.semester
                student.save(update_fields=['batch', 'semester'])
                messages.success(request, f"Added student {student.first_name} to {batch.name}.")
            elif action == 'remove':
                # Remove from M2M and fall back to next enrolled batch (if any)
                batch.students.remove(student)
                remaining = student.enrolled_batches.first()
                student.batch = remaining.name if remaining else ''
                student.semester = remaining.semester if remaining else None
                student.save(update_fields=['batch', 'semester'])
                messages.success(request, f"Removed student {student.first_name} from {batch.name}.")

        return redirect('dashboard:admin_manage_batch_students', pk=pk)

    enrolled_students = batch.students.all().order_by('first_name')
    # Only show students not enrolled in any batch
    available_students = User.objects.filter(role='student').filter(enrolled_batches__isnull=True).order_by('first_name')

    context = {
        'batch': batch,
        'enrolled_students': enrolled_students,
        'available_students': available_students
    }
    return render(request, 'dashboard/admin/manage_batch_students.html', context)


# =============================================================================
# Manage Courses in a Batch
# =============================================================================

@login_required
def admin_manage_batch_courses(request, pk):
    """
    GET:  Shows enrolled courses and available courses (filtered by batch semester).
    POST: Adds or removes a course from the batch. Notifies faculty on add.
    """
    if request.user.role != 'admin':
        return redirect('home')

    batch = get_object_or_404(Batch, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        course_id = request.POST.get('course_id')

        if course_id:
            course = get_object_or_404(Course, pk=course_id)
            if action == 'add':
                batch.courses.add(course)
                messages.success(request, f"Added course {course.code} to {batch.name}.")

                # Notify the assigned faculty about the new batch
                if course.faculty:
                    create_notification(
                        user=course.faculty,
                        title="Course Batch Update",
                        message=f"Your course {course.code} has been assigned to a new batch: {batch.name}.",
                        link="/dashboard/faculty/courses/",
                        notification_type='system'
                    )
            elif action == 'remove':
                batch.courses.remove(course)
                messages.success(request, f"Removed course {course.code} from {batch.name}.")

        return redirect('dashboard:admin_manage_batch_courses', pk=pk)

    enrolled_courses = batch.courses.select_related('faculty').all().order_by('name')
    available_courses = Course.objects.filter(is_active=True).exclude(batches=batch).select_related('faculty').order_by('name')

    # Filter available courses to match the batch's semester
    if batch.semester:
        available_courses = available_courses.filter(semester=batch.semester)

    context = {
        'batch': batch,
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses
    }
    return render(request, 'dashboard/admin/manage_batch_courses.html', context)
