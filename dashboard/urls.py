"""
URL configuration for the dashboard app.

Routes all dashboard pages for Admin, Faculty, and Student roles.
All URLs are prefixed with /dashboard/ (configured in core/urls.py).

Faculty assignment CRUD routes point to the assignments app views,
while submission/evaluation routes are handled by dashboard views.
"""

from django.urls import path
from . import views
from assignments import views as assignment_views

app_name = 'dashboard'

urlpatterns = [
    # --- Admin Dashboard ---
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),

    # Admin: Course Management
    path('admin/courses/', views.admin_courses, name='admin_courses'),
    path('admin/courses/<int:pk>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('admin/courses/<int:pk>/delete/', views.admin_course_delete, name='admin_course_delete'),
    path('admin/courses/<int:pk>/archive/', views.admin_course_archive, name='admin_course_archive'),

    # Admin: Batch Management
    path('admin/batches/', views.admin_batches, name='admin_batches'),
    path('admin/batches/<int:pk>/edit/', views.admin_batch_edit, name='admin_batch_edit'),
    path('admin/batches/<int:pk>/delete/', views.admin_batch_delete, name='admin_batch_delete'),
    path('admin/batches/<int:pk>/archive/', views.admin_batch_archive, name='admin_batch_archive'),
    path('admin/batches/<int:pk>/students/', views.admin_manage_batch_students, name='admin_manage_batch_students'),
    path('admin/batches/<int:pk>/courses/', views.admin_manage_batch_courses, name='admin_manage_batch_courses'),

    # --- Faculty Dashboard ---
    path('faculty/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/courses/', views.faculty_courses, name='faculty_courses'),
    path('faculty/students/', views.faculty_students, name='faculty_students'),

    # Faculty: Assignment CRUD (handled by assignments app)
    path('faculty/assignments/', assignment_views.faculty_assignments, name='faculty_assignments'),
    path('faculty/assignments/create/', assignment_views.faculty_create_assignment, name='faculty_create_assignment'),
    path('faculty/assignments/<int:pk>/', assignment_views.faculty_view_assignment, name='faculty_view_assignment'),
    path('faculty/assignments/<int:pk>/edit/', assignment_views.faculty_edit_assignment, name='faculty_edit_assignment'),
    path('faculty/assignments/<int:pk>/toggle-publish/', assignment_views.faculty_toggle_publish, name='faculty_toggle_publish'),
    path('faculty/assignments/<int:pk>/extend/', assignment_views.faculty_extend_deadline, name='faculty_extend_deadline'),
    path('faculty/assignments/<int:pk>/delete/', assignment_views.faculty_delete_assignment, name='faculty_delete_assignment'),

    # Faculty: Submission Review & Grading (handled by dashboard views)
    path('faculty/assignments/<int:assignment_pk>/submissions/', views.faculty_submission_list, name='faculty_submission_list'),
    path('faculty/submissions/<int:submission_pk>/', views.faculty_submission_detail, name='faculty_submission_detail'),

    # --- Student Dashboard ---
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/courses/', views.student_courses, name='student_courses'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/assignments/<int:pk>/', views.student_assignment_detail, name='student_assignment_detail'),
    path('student/courses/<int:pk>/', views.student_course_detail, name='student_course_detail'),

    # --- Shared (All Roles) ---
    path('profile/', views.profile_view, name='profile'),

    # Notification Actions
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:pk>/delete/', views.delete_notification, name='delete_notification'),
]
