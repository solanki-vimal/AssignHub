from django.db import models
from django.conf import settings

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    semester = models.IntegerField()
    department = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'faculty'},
        related_name='assigned_courses'
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

class Batch(models.Model):
    name = models.CharField(max_length=100)  # e.g., Class A, CE Level 2
    academic_year = models.CharField(max_length=20)  # e.g., 2024-25
    semester = models.IntegerField(null=True, blank=True)  # e.g., 1-8
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'faculty'},
        related_name='coordinated_batches'
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'student'},
        related_name='enrolled_batches',
        blank=True
    )
    courses = models.ManyToManyField(
        Course,
        related_name='batches',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"
