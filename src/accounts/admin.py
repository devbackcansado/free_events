from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.forms import CreateUserForm, ChangeUserForm
from accounts.models import User


class UserAdmin(UserAdmin):
    add_form = CreateUserForm
    form = ChangeUserForm
    model = User
    readonly_fields = ["uid"]
    list_display = (
        "email",
        "uid",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_active",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "uid",
                    "last_login",
                    "date_joined",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, UserAdmin)
