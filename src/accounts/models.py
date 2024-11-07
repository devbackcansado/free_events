from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.models import UUID4Generator, get_upload_path_user
from uuid import uuid4
from PIL import Image
from django.db import models
from accounts.managers import UserManager


class User(AbstractUser):
    """
    User model that extends Django's AbstractUser.

    Args:
        USERNAME_FIELD (str): The field used for authentication, set to "email".
        REQUIRED_FIELDS (list): List of required fields, set to an empty list.
        username (None): Username field is set to None.
        uid (UUIDField): Unique identifier for the user, generated using UUID4.
        first_name (CharField): User's first name with a maximum length of 255 characters.
        last_name (CharField): User's last name with a maximum length of 255 characters.
        email (EmailField): User's email address, must be unique.

    Meta:
        verbose_name (str): Human-readable name for the model, set to "User".
        verbose_name_plural (str): Human-readable plural name for the model, set to "Users".
        ordering (list): Default ordering for the model, set to order by "date_joined".

    Methods:
        save(*args, **kwargs): Saves the user instance, and resizes the profile image if it exists.
        __str__(): Returns the user's email address as the string representation of the user.
        resize_image(): Resizes the user's profile image to a maximum of 300x300 pixels.
        model_dump(): Returns a dictionary representation of the user instance.
    """

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username = None
    uid = models.UUIDField(
        db_default=UUID4Generator(),
        unique=True,
        editable=False,
        db_index=True,
        default=uuid4,
    )
    first_name = models.CharField("Primeiro Nome", max_length=255, null=True, blank=True)
    last_name = models.CharField("Ultimo Nome", max_length=255, null=True, blank=True)
    email = models.EmailField("Email", unique=True)
    # profile_image = models.ImageField(
    #     upload_to=get_upload_path_user,
    # )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["date_joined"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # if self.profile_image:
        #     self.resize_image()

    def __str__(self):
        return self.email

    def resize_image(self):
        img = Image.open(self.profile_image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.profile_image.path)

    def model_dump(self):
        return {
            "uid": self.uid,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            # "profile_image": self.profile_image.url,
            "is_active": self.is_active,
            "date_joined": self.date_joined,
            "last_login": self.last_login,
        }
