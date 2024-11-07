from celery import shared_task

from django.contrib.auth import get_user_model

_User = get_user_model()


@shared_task
def send_notification_by_cancell(events_id: int):
    """
    Sends a notification to the users of the canceled events.

    Args:
        events_id (int): The ID of the event.
    Returns:
        None
    """

    print("Notification sent")
    return
