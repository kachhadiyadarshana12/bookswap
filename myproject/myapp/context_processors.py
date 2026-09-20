from .models import Notification


def navbar_notifications(request):
    notifications = []
    unread_count = 0
    if request.user.is_authenticated:
        qs = Notification.objects.select_related("book", "book__seller").filter(
            user=request.user, is_removed=False
        )
        
        # Hide 'offer' notifications for sellers, only show 'chat' and 'exchange'
        if hasattr(request.user, "seller_profile") and not hasattr(request.user, "reader_profile"):
            qs = qs.filter(notification_type__in=["chat", "exchange"])
            
        notifications = list(qs.order_by("-created_at")[:5])
        unread_count = qs.filter(is_read=False).count()

    return {
        "navbar_notifications": notifications,
        "navbar_notification_count": unread_count,
    }
