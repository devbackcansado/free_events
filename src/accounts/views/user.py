from django.contrib.auth import logout as django_logout, authenticate, login as django_login
from django.db import IntegrityError
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from orjson import loads, JSONDecodeError
from pydantic import ValidationError
from typing import Union
from accounts.models import User
from accounts.schemas.user import UserCreate, UserLogin, UserUpdate
from accounts.decorators import check_session_view

from utils.response import JsonResponseBadRequest, JsonResponse
from utils.tasks import create_periodic_task
from events.models import Event
from utils.tasks import create_periodic_task


@require_POST
@csrf_exempt
def login(request: HttpRequest) -> Union[JsonResponse, JsonResponseBadRequest]:
    try:
        payload = UserLogin(**loads(request.body))
    except (ValidationError, JSONDecodeError) as e:
        error = (
            [
                {
                    "loc": x["loc"],
                    "msg": x["msg"],
                    "type": x["type"],
                }
                for x in e.errors()
            ]
            if isinstance(e, ValidationError)
            else [{"loc": e.lineno, "msg": e.msg, "type": "json_error"}]
        )
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": error,
            }
        )

    user = authenticate(request=request, email=payload.email, password=payload.password)
    if user is None or not user.is_active:
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": [
                    {
                        "loc": "email",
                        "msg": "Email ou senha inválidos",
                        "type": "value_error",
                    }
                ],
            }
        )

    django_login(request, user)
    request.session.save()

    return JsonResponse(
        content={
            "success": True,
            "data": {
                "token": request.session.session_key,
            },
        }
    )


@check_session_view("GET")
def user_me(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        content={
            "success": True,
            "data": request.user.model_dump(),
        }
    )


@check_session_view("POST")
def logout(request: HttpRequest) -> JsonResponse:
    django_logout(request)
    return JsonResponse(
        content={"succes": True, "data": {"message": "Deslogado com sucesso!"}},
    )


@csrf_exempt
@require_POST
def create_user(request: HttpRequest) -> Union[JsonResponse, JsonResponseBadRequest]:
    try:
        payload = UserCreate(**loads(request.body))
    except (ValidationError, JSONDecodeError) as e:
        error = (
            [
                {
                    "loc": x["loc"],
                    "msg": x["msg"],
                    "type": x["type"],
                }
                for x in e.errors()
            ]
            if isinstance(e, ValidationError)
            else [{"loc": e.lineno, "msg": e.msg, "type": "json_error"}]
        )
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": error,
            }
        )

    try:
        user = User.objects.create_user(
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=payload.password1,
            email=payload.email,
        )
    except IntegrityError:
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": [
                    {
                        "loc": "email",
                        "msg": "Usuário já existe",
                        "type": "value_error",
                    }
                ],
            }
        )
    except Exception as e:
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": [
                    {
                        "loc": "email",
                        "msg": str(e),
                        "type": "value_error",
                    }
                ],
            }
        )
    create_periodic_task(
        name=f"Create organization to {user.email}",
        task="accounts.tasks.organization.finished_account_creation",
        args=[user.id],
    )

    create_periodic_task(
        name=f"Send email confirmation to {user.email}",
        task="accounts.tasks.email.send_email_confirmation",
        args=[user.id, request.get_host()],
    )

    return JsonResponse(
        content={
            "success": True,
            "data": {
                "message": f"{user.email} - {user.first_name} - {user.last_name} criado com sucesso!",
            },
        }
    )


@check_session_view("PUT")
def update_user(request: HttpRequest) -> Union[JsonResponse, JsonResponseBadRequest]:
    try:
        payload = UserUpdate(**loads(request.body))
    except (ValidationError, JSONDecodeError) as e:
        error = (
            [
                {
                    "loc": x["loc"],
                    "msg": x["msg"],
                    "type": x["type"],
                }
                for x in e.errors()
            ]
            if isinstance(e, ValidationError)
            else [{"loc": e.lineno, "msg": e.msg, "type": "json_error"}]
        )
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": error,
            }
        )

    user = request.user

    for attr, value in payload.model_dump().items():
        if value is None:
            continue
        setattr(user, attr, value)

    user.save()

    return JsonResponse(
        content={
            "success": True,
            "data": {
                "message": f"Usuario atualizado com sucesso!",
            },
        }
    )


@check_session_view("DELETE")
def delete_user(request: HttpRequest) -> JsonResponse:
    user = request.user
    email = user.email
    events = Event.objects.filter(promoter=user).values_list("id", flat=True)

    for event in events:
        create_periodic_task(
            name=f"Send Notification Cancell Event {event} by promoter {email} deleted account",
            task="events.tasks.event.send_notification_by_cancell",
            args=[event],
        )

    user.is_active = False
    user.save()
    return JsonResponse(
        content={
            "success": True,
            "data": {
                "message": f"{email} deletado com sucesso!",
            },
        }
    )
