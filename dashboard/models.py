"""
Models for the dashboard app.

Contains the Notification model which powers the real-time notification
bell icon and dropdown across all role-based dashboards.
"""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    In-app notification sent to a user.
    Created by helper functions in notifications.py when events occur
    (e.g., new assignment, submission evaluated, deadline extended).
    """

    NOTIFICATION_TYPES = [
        ('assignment', 'Assignment'),     # New/updated assignment
        ('submission', 'Submission'),     # Student submitted work
        ('evaluation', 'Evaluation'),     # Faculty graded a submission
        ('system', 'System'),             # System-wide announcements
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)                  # e.g., "New Assignment Posted"
    message = models.TextField()                               # Detailed description
    link = models.CharField(max_length=255, blank=True, null=True)  # Optional navigation URL
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)               # Unread = shows in badge count
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Newest first

    def __str__(self):
        return f"{self.user.email} - {self.title}"
