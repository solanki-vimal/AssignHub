from django.contrib import admin
from .models import Assignment, AssignmentAttachment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'batch', 'created_by', 'due_date', 'published', 'created_at')
    list_filter = ('course', 'batch', 'published', 'created_by')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(AssignmentAttachment)
class AssignmentAttachmentAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
