from .models import Notification


def navbar_notifications(request):
    notifications = []
    if request.user.is_authenticated:
        notifications = list(
            Notification.objects.select_related("book", "book__seller")
            .filter(user=request.user, is_removed=False)
            .order_by("-created_at")[:5]
        )

    return {
        "navbar_notifications": notifications,
        "navbar_notification_count": Notification.objects.filter(
            user=request.user, is_read=False, is_removed=False
        ).count()
        if request.user.is_authenticated
        else 0,
    }
