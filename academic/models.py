from django.db import models
from django.conf import settings


class Department(models.Model):
    """Represents an academic department (e.g., Computer Engineering)."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Represents a course taught by a faculty member.
    Each course belongs to a department and is offered in a specific semester.
    A course can be linked to multiple batches.
    """

    code = models.CharField(max_length=20, unique=True)         # e.g., CE401
    name = models.CharField(max_length=200)                      # e.g., Data Structures
    semester = models.IntegerField()                              # 1–8
    department = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    # Faculty assigned to teach this course
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
    """
    Represents a student batch (e.g., CE-2024-B1).
    A batch belongs to an academic year and a semester.
    Students and courses are linked to batches via ManyToMany relationships.
    """

    name = models.CharField(max_length=100)                      # e.g., B7, CE-A
    academic_year = models.CharField(max_length=20)              # e.g., 2024-25
    semester = models.IntegerField(null=True, blank=True)        # 1–8 (optional)

    # Students enrolled in this batch
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'student'},
        related_name='enrolled_batches',
        blank=True
    )

    # Courses offered to this batch
    courses = models.ManyToManyField(
        Course,
        related_name='batches',
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.academic_year})"
