from django.contrib import admin
from .models import Course, Batch

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'semester', 'department', 'is_active')
    list_filter = ('semester', 'department', 'is_active')
    search_fields = ('code', 'name')
    filter_horizontal = ('students',)

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'semester', 'is_active')
    list_filter = ('academic_year', 'semester', 'is_active')
    search_fields = ('name', 'academic_year')
    filter_horizontal = ('students', 'courses')
