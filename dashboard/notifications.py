from .models import Notification

def create_notification(user, title, message, link=None, notification_type='system'):
    """
    Utility function to create a new notification for a specific user.
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
    Notify all students enrolled in a specific batch.
    """
    from accounts.models import User
    students = User.objects.filter(batch=batch.id, role='student')
    
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
