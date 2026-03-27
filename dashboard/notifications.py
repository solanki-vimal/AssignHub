"""
Notification helper functions for the dashboard app.

Provides utility functions to create in-app notifications.
Called from views when events occur (e.g., assignment published,
submission graded, deadline extended).
"""

from .models import Notification


def create_notification(user, title, message, link=None, notification_type='system'):
    """
    Creates a single notification for a specific user.

    Args:
        user: The User object to notify
        title: Short heading (e.g., "Submission Evaluated")
        message: Detailed description
        link: Optional URL for navigation (e.g., "/dashboard/student/assignments/5/")
        notification_type: Category — 'assignment', 'submission', 'evaluation', or 'system'

    Returns:
        The created Notification object
    """
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link,
        notification_type=notification_type
    )


def notify_batch_students(batch, title, message, link=None, notification_type='assignment'):
    """
    Creates notifications for all active students enrolled in a batch.
    Uses bulk_create() for performance — single SQL query instead of one per student.

    Args:
        batch: The Batch object whose students should be notified
        title: Short heading (e.g., "New Assignment Posted")
        message: Detailed description
        link: Optional URL for navigation
        notification_type: Category — defaults to 'assignment'
    """
    from accounts.models import User  # Imported here to avoid circular imports

    students = User.objects.filter(enrolled_batches=batch, role='student', is_active=True)

    notifications = [
        Notification(
            user=student,
            title=title,
            message=message,
            link=link,
            notification_type=notification_type
        ) for student in students
    ]
    Notification.objects.bulk_create(notifications)
