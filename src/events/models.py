from django.db import models
from utils.models import CreatedMixin

from django.contrib.auth import get_user_model
from events.constants import TypeSubscriptionStatus, TRANSLATED_SUBSCRIPTION_STATUS
from utils.models import UUID4Generator
from uuid import uuid4

_User = get_user_model()


class Event(CreatedMixin):
    """
    Event model representing an event created by a promoter.

    Args:
        promoter (ForeignKey): A foreign key to the User model representing the promoter of the event.
        title (CharField): The title of the event.
        description (TextField): A detailed description of the event.
        address (CharField): The address where the event will take place.
        start_at (DateTimeField): The date and time when the event starts.
        is_active (BooleanField): A flag indicating whether the event is active. Defaults to True.

    Methods:
        __str__(): Returns the string representation of the event, which is its title.

    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
        ordering (list): Default ordering for the model, by creation date in descending order.
    """

    uid = models.UUIDField(
        db_default=UUID4Generator(),
        unique=True,
        editable=False,
        db_index=True,
        default=uuid4,
    )
    promoter = models.ForeignKey(
        _User,
        on_delete=models.CASCADE,
        related_name="events",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    start_at = models.DateTimeField()
    is_active = models.BooleanField(default=True, db_default=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def model_dump(self):
        return {
            "uid": self.uid,
            "promoter": self.promoter.email,
            "title": self.title,
            "description": self.description,
            "address": self.address,
            "start_at": self.start_at,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Subscription(CreatedMixin):
    """
    Represents a subscription of a user to an event.

    Args:
        user (ForeignKey): A reference to the user who subscribed to the event.
        event (ForeignKey): A reference to the event to which the user subscribed.

    Methods:
        __str__(): Returns a string representation of the subscription.

    Meta:
        verbose_name (str): Human-readable name for the subscription.
        verbose_name_plural (str): Human-readable plural name for the subscriptions.
        ordering (list): Default ordering for the model, by creation date in descending order.
        constraints (list): Constraints for the subscription model, ensuring unique user-event pairs.
    """

    uid = models.UUIDField(
        db_default=UUID4Generator(),
        unique=True,
        editable=False,
        db_index=True,
        default=uuid4,
    )

    user = models.ForeignKey(
        _User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_user_event_subscription",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.event}"

    def model_dump(self):
        event = self.event
        return {
            "uid": self.uid,
            "event__title": event.title,
            "event__description": event.description,
            "event__start_at": event.start_at,
            "event__is_active": event.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": TRANSLATED_SUBSCRIPTION_STATUS[self.subscription_statuses.last().status],
        }


class SubscriptionStatus(CreatedMixin):
    """
    Model representing the status of a subscription.

    Args:
        subscription (ForeignKey): Foreign key to the Subscription model.
            Deletes related statuses when the subscription is deleted.
        status (IntegerField): The status of the subscription, with choices defined
            in SUBSCRIPTION_STATUS_CHOICES. Defaults to SubscriptionStatus.CREATED.

    Methods:
        __str__(): Returns a string representation of the subscription status.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for the model, by creation date in descending order
    """

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="subscription_statuses",
    )
    status = models.PositiveSmallIntegerField(
        choices=TypeSubscriptionStatus.choices(),
        default=TypeSubscriptionStatus.CREATED,
        db_default=TypeSubscriptionStatus.CREATED,
    )

    class Meta:
        verbose_name = "SubscriptionStatus"
        verbose_name_plural = "SubscriptionStatuses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subscription} - {self.status}"
