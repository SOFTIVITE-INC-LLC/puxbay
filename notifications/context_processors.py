from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        latest = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {
            'latest_notifications': latest,
            'unread_notification_count': unread_count
        }
    return {
        'latest_notifications': [],
        'unread_notification_count': 0
    }
