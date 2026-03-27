"""
Django Admin configuration for the assignments app.

Registers all 4 models (Assignment, AssignmentAttachment, Submission, SubmissionFile)
in the Django admin panel (/admin/) with full CRUD control, filters, and search.
"""

from django.contrib import admin
from .models import Assignment, AssignmentAttachment, Submission, SubmissionFile


# --- Assignment Management ---

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin view for faculty-created assignments."""
    list_display = ('title', 'course', 'batch', 'created_by', 'due_date', 'published', 'created_at')
    list_filter = ('course', 'batch', 'published', 'created_by')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'


@admin.register(AssignmentAttachment)
class AssignmentAttachmentAdmin(admin.ModelAdmin):
    """Admin view for reference files attached to assignments by faculty."""
    list_display = ('assignment', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)


# --- Submission Management ---

class SubmissionFileInline(admin.TabularInline):
    """Displays submitted files inline within the Submission edit page."""
    model = SubmissionFile
    extra = 0


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin view for student submissions with inline file viewing."""
    list_display = ('student', 'assignment', 'status', 'marks_obtained', 'submitted_at', 'updated_at')
    list_filter = ('status', 'assignment__course', 'assignment__batch')
    search_fields = ('student__username', 'student__email', 'assignment__title')
    date_hierarchy = 'submitted_at'
    inlines = [SubmissionFileInline]


@admin.register(SubmissionFile)
class SubmissionFileAdmin(admin.ModelAdmin):
    """Standalone admin view for individual submission files."""
    list_display = ('submission', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('submission__student__username', 'submission__assignment__title')
