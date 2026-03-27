from django.contrib.auth.models import AbstractUser
from django.db import models


def user_profile_pic_path(instance, filename):
    """Generates upload path: media/profile_pics/user_<id>/<filename>"""
    return f"profile_pics/user_{instance.id}/{filename}"


class User(AbstractUser):
    """
    Custom User model for AssignHub.
    Extends Django's AbstractUser with role-based fields for Students, Faculty, and Admins.
    """

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )

    ACCOUNT_STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    )

    # Core fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='active')

    # Student-specific fields
    enrollment_no = models.CharField(max_length=20, blank=True, null=True)    # e.g., 24CEUBS148
    batch = models.CharField(max_length=20, blank=True, null=True)            # System-managed: synced from Batch model
    semester = models.IntegerField(blank=True, null=True)                     # System-managed: synced from Batch model

    # Faculty-specific fields
    faculty_id = models.CharField(max_length=20, blank=True, null=True)       # e.g., FAC101

    # Shared fields
    department = models.CharField(max_length=100, blank=True, null=True)      # Stored as string, not FK
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
