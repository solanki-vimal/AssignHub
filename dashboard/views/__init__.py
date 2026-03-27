"""
Dashboard views package.

Re-exports all views from submodules so they can be imported directly:
    from dashboard.views import admin_dashboard, faculty_courses, etc.

Organized into submodules by role/feature:
    - admin_views: Admin dashboard and user management
    - batch_views: Admin batch CRUD and student/course enrollment
    - course_views: Admin course CRUD and archive
    - faculty_views: Faculty dashboard, courses, and students
    - student_views: Student dashboard, courses, assignments, and submissions
    - submission_views: Faculty submission review and grading
    - profile_views: Profile page (shared by all roles)
    - notification_views: Notification mark-read, mark-all, delete
"""

from .admin_views import admin_dashboard, admin_users
from .course_views import admin_courses, admin_course_edit, admin_course_delete, admin_course_archive
from .batch_views import admin_batches, admin_batch_edit, admin_batch_delete, admin_batch_archive, admin_manage_batch_students, admin_manage_batch_courses
from .faculty_views import faculty_dashboard, faculty_courses, faculty_students
from .student_views import student_dashboard, student_courses, student_assignments, student_assignment_detail, student_course_detail
from .submission_views import faculty_submission_list, faculty_submission_detail
from .profile_views import profile_view
from .notification_views import mark_notification_read, mark_all_notifications_read, delete_notification

__all__ = [
    'admin_dashboard', 'admin_users',
    'admin_courses', 'admin_course_edit', 'admin_course_delete', 'admin_course_archive',
    'admin_batches', 'admin_batch_edit', 'admin_batch_delete', 'admin_batch_archive', 'admin_manage_batch_students', 'admin_manage_batch_courses',
    'faculty_dashboard', 'faculty_courses', 'faculty_students',
    'faculty_submission_list', 'faculty_submission_detail',
    'student_dashboard', 'student_courses', 'student_assignments', 'student_assignment_detail', 'student_course_detail',
    'profile_view',
    'mark_notification_read', 'mark_all_notifications_read', 'delete_notification'
]
