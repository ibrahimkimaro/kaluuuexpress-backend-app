import logging

logger = logging.getLogger(__name__)


def send_push_notification(user, title, message, data=None):
    """
    Placeholder for push notification functionality.
    Implement your preferred push notification service here.

    Args:
        user: User object
        title: Notification title
        message: Notification message
        data: Dict of additional data
    """
    logger.info(f"Push notification for user {user.id}: {title} - {message}")


def send_bulk_notification(users, title, message, data=None):
    """Send notification to multiple users"""
    for user in users:
        send_push_notification(user, title, message, data)
