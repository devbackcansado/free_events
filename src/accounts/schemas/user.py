from typing import Self, Optional
from pydantic import BaseModel, field_validator, model_validator
from django.core.validators import validate_email

from django.contrib.auth.password_validation import validate_password


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, v):
        try:
            validate_email(v)
        except Exception as e:
            raise ValueError(e.message)
        return v


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password1: str
    password2: str

    @model_validator(mode="after")
    def check_fields(self) -> Self:
        self.email = self.email.lower()
        try:
            validate_email(self.email)
        except Exception as e:
            raise ValueError(e.message)

        if self.password1 != self.password2:
            raise ValueError("Senhas não conferem")

        try:
            validate_password(self.password1)
        except Exception as e:
            raise ValueError(" ".join(e))

        return self


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @model_validator(mode="after")
    def check_fields(self) -> Self:
        if not self.first_name and not self.last_name:
            raise ValueError("Nenhum campo para atualizar")
        return self
