from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
)
from accounts.models import User
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
        exclude = ["username"]


class SinupUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "email",
        ]
        exclude = ["username"]


class ChangeUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


class LoginUserForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
