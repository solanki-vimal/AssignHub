"""
Notification action views.

Handles marking notifications as read (single and bulk) and deletion.
Supports both AJAX (returns JSON) and standard (redirects) requests.
"""

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Notification


@login_required
def mark_notification_read(request, pk):
    """
    Marks a single notification as read.
    AJAX: Returns JSON response.
    Standard: Redirects to the notification's link or the dashboard.
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})

    # Navigate to the notification's link if available
    if notification.link:
        return redirect(notification.link)
    return redirect('accounts:dashboard_redirect')


@login_required
def mark_all_notifications_read(request):
    """Marks all unread notifications as read for the current user."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})

    return redirect('accounts:dashboard_redirect')


@login_required
def delete_notification(request, pk):
    """Permanently deletes a single notification."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})

    return redirect('accounts:dashboard_redirect')
