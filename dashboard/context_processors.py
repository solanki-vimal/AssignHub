"""
Context processor for the dashboard app.

Registered in settings.py under TEMPLATES → context_processors.
Automatically injects notification data into every template so
the notification bell/badge is available on all pages without
needing to add it to each view's context manually.
"""

from .models import Notification


def notification_context(request):
    """
    Provides unread notification count and recent notifications to all templates.

    Returns (for authenticated users):
        unread_notifications: Last 5 unread Notification objects (for bell dropdown)
        unread_notification_count: Total unread count (for badge number)

    Returns empty dict for unauthenticated users (public pages like login/register).
    """
    if request.user.is_authenticated:
        recent_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:5]

        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return {
            'unread_notifications': recent_notifications,
            'unread_notification_count': unread_count,
        }
    return {}
