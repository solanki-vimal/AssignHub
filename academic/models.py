from django.db import models
from django.conf import settings

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    semester = models.IntegerField()
    department = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Batch(models.Model):
    name = models.CharField(max_length=100)  # e.g., Class A, CE Level 2
    academic_year = models.CharField(max_length=20) # e.g., 2024-2025
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'student'},
        related_name='enrolled_batches',
        blank=True
    )
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class FacultyCourseBatchMapping(models.Model):
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'faculty'},
        related_name='course_assignments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='faculty_assignments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='faculty_assignments')

    class Meta:
        unique_together = ('faculty', 'course', 'batch')

    def __str__(self):
        return f"{self.faculty.username} - {self.course.code} - {self.batch.name}"
