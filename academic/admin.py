from django.contrib import admin
from .models import Course, Batch, FacultyCourseBatchMapping

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'semester', 'department')
    search_fields = ('code', 'name', 'department')
    list_filter = ('semester', 'department')

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year')
    search_fields = ('name', 'academic_year')
    list_filter = ('academic_year',)
    filter_horizontal = ('students',)

@admin.register(FacultyCourseBatchMapping)
class FacultyCourseBatchMappingAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'course', 'batch')
    list_filter = ('course', 'batch')
    search_fields = ('faculty__username', 'faculty__first_name', 'course__code', 'batch__name')
