from django.db import models
from django.db.models.functions import Now
from django.db.models.expressions import Func
from django.db.models.fields import UUIDField
from uuid import uuid4
import os


class CreatedMixin(models.Model):
    """
    Mixin to add created and updated timestamp fields to a model.

    Args:
        created_at (DateTimeField): The date and time when the object was created.
                                    Automatically set to the current date and time when the object is first created.
        updated_at (DateTimeField): The date and time when the object was last updated.
                                    Automatically set to the current date and time whenever the object is saved.
    """

    created_at = models.DateTimeField(db_default=Now(), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUID4Generator(Func):
    """
    UUID4Generator is a custom Django database function that generates a UUID version 4.

    Args:
        template (str): The SQL template used to generate the UUID.
        output_field (UUIDField): The type of field that this function outputs.

    Methods:
        as_postgresql(compiler, connection, **extra_context):
            Generates the SQL for PostgreSQL databases.

        as_sqlite(compiler, connection, **extra_context):
            Generates the SQL for SQLite databases.
    """

    template = "GEN_RANDOM_UUID"
    output_field = UUIDField()

    def as_postgresql(self, compiler, connection, **extra_context):
        return self.as_sql(compiler, connection, template="GEN_RANDOM_UUID()", **extra_context)

    def as_sqlite(self, compiler, connection, **extra_context):
        return self.as_sql(
            compiler,
            connection,
            template=(
                "lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)),2) ||",
                " '-a' || substr(hex(randomblob(2)),2) || '-' || hex(randomblob(6)))",
            ),
            **extra_context,
        )


def get_upload_path_user(instance, filename):
    """
    Generate a file upload path for a user.

    Args:
        instance: The instance of the model that the file is associated with.
        filename: The original name of the file being uploaded.

    Returns:
        str: A string representing the file path where the uploaded file should be stored.
    """
    ext = filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"

    models_path = instance.__class__.__name__.lower()

    return os.path.join(
        f"users/{instance.user.uid}",
        models_path,
        filename,
    )


def dict_fetchall(cursor):
    """
    Return all rows from a cursor as a dict.

    Args:
        cursor: The cursor object to fetch rows from.

    Returns:
        list: A list of dictionaries representing the rows fetched from the cursor.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
