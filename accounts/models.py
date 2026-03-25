from django.contrib.auth.models import AbstractUser
from django.db import models

def user_profile_pic_path(instance, filename):
    return f"profile_pics/user_{instance.id}/{filename}"

class User(AbstractUser):
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

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='active')
    
    # Role-specific fields (optional, simplified for Phase 1)
    # For a more robust design, these could be separate Profile models
    enrollment_no = models.CharField(max_length=20, blank=True, null=True)
    faculty_id = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    batch = models.CharField(max_length=20, blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
