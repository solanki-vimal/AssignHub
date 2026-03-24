from .admin_views import admin_dashboard, admin_users
from .course_views import admin_courses, admin_course_edit, admin_course_delete, admin_course_archive
from .batch_views import admin_batches, admin_batch_edit, admin_batch_delete, admin_batch_archive, admin_manage_batch_students, admin_manage_batch_courses
from .faculty_views import faculty_dashboard, faculty_courses, faculty_students
from .student_views import student_dashboard, student_courses, student_assignments, student_assignment_detail, student_course_detail
from .submission_views import faculty_submission_list, faculty_submission_detail
from .profile_views import profile_view

__all__ = [
    'admin_dashboard', 'admin_users',
    'admin_courses', 'admin_course_edit', 'admin_course_delete', 'admin_course_archive',
    'admin_batches', 'admin_batch_edit', 'admin_batch_delete', 'admin_batch_archive', 'admin_manage_batch_students', 'admin_manage_batch_courses',
    'faculty_dashboard', 'faculty_courses', 'faculty_students',
    'faculty_submission_list', 'faculty_submission_detail',
    'student_dashboard', 'student_courses', 'student_assignments', 'student_assignment_detail', 'student_course_detail',
    'profile_view'
]
