from .models import Notification

def notification_context(request):
    """
    Context processor to provide unread notification count and recent notifications
    to all templates if the user is authenticated.
    """
    if request.user.is_authenticated:
        # Get last 5 unread notifications
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
            'unread_notification_count': unread_count
        }
    return {}
