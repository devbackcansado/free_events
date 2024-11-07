from uuid import UUID
from django.http import HttpRequest
from orjson import loads, JSONDecodeError
from pydantic import ValidationError
from typing import Union
from django.db.models import OuterRef, Subquery, Case, When, Value, CharField

from utils.response import JsonResponseBadRequest, JsonResponse
from utils.pagination import generate_pagination_by_models

from events.schemas.subscription import SubscriptionCreate
from events.models import Subscription, SubscriptionStatus, Event
from events.filters import SubscriptionParams
from events.constants import TypeSubscriptionStatus
from accounts.decorators import check_session_view
from events.utils import FIELDS_BY_SUBSCRIPTION_MODEL_DUMP


@check_session_view("POST")
def create_subscription(request: HttpRequest) -> Union[JsonResponse, JsonResponseBadRequest]:
    """
    Handles the creation of a subscription for an event.

    Args:
        request (HttpRequest): The HTTP request object containing the subscription data in the body.

    Returns:
        Union[JsonResponse, JsonResponseBadRequest]: A JSON response indicating the success or failure of the subscription creation process.

    Raises:
        ValidationError: If the subscription data is invalid.
        JSONDecodeError: If the request body is not valid JSON.
        Event.DoesNotExist: If the event specified in the subscription data does not exist.

    Example:
        Request:
        ```
        POST /subscriptions/create/
        {
            "event_uid": "123e4567-e89b-12d3-a456-426614174000"
        }
        ```

        Response:
        ```
        {
            "success": true,
            "msg": "Inscrição criada com sucesso",
            "data": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "event__title": "My Event",
                "event__description": "This is a test event",
                "event__start_at": "2022-01-01T12:00:00",
                "event__is_active": true,
                "created_at": "2022-01-01T12:00:00",
                "updated_at": "2022-01-01T12:00:00"
            }
        }
        ```
    """
    try:
        payload = SubscriptionCreate(**loads(request.body))
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
        event = Event.objects.get(uid=payload.event_uid)
    except Event.DoesNotExist:
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": [
                    {
                        "loc": "event_uid",
                        "msg": "Evento não encontrado",
                        "type": "not_found",
                    }
                ],
            }
        )

    if not event.is_active:
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": [
                    {
                        "loc": "event_uid",
                        "msg": "Evento não está ativo",
                        "type": "not_active",
                    }
                ],
            }
        )

    subscription = Subscription.objects.create(
        user=request.user,
        event=event,
    )

    SubscriptionStatus.objects.create(
        subscription=subscription,
        status=TypeSubscriptionStatus.CREATED,
    )

    return JsonResponse(
        content={
            "success": True,
            "msg": "Inscrição criada com sucesso",
            "data": subscription.model_dump(),
        }
    )


@check_session_view("GET")
def list_subscription(request: HttpRequest) -> Union[JsonResponse, JsonResponseBadRequest]:
    """
    Handles the listing of subscriptions based on the provided request parameters.

    Args:
        request (HttpRequest): The HTTP request object containing query parameters.

    Returns:
        Union[JsonResponse, JsonResponseBadRequest]: A JSON response containing the list of subscriptions
        or a JSON response indicating a bad request with validation errors.

    Raises:
        ValidationError: If the request parameters fail validation.

    Example:
        Request:
        ```
        GET /subscriptions/list/?limit=10&page=1
        ```

        Response:
        ```
        {
            "success": true,
            "previous_page": null,
            "next_page": null,
            "num_pages": 1,
            "total": 1,
            "data": [
                {
                "uid": "1efe9a37-3b55-4757-8437-5197bf090671",
                "event__title": "São João ",
                "event__description": "O Melhor São João do Brasil",
                "event__address": "rua 1",
                "event__start_at": "2025-06-24T00:00:00",
                "event__is_active": true,
                "created_at": "2024-11-01T22:27:54.402773",
                "updated_at": "2024-11-01T22:27:54.402815",
                "status": "Desinscrito"
                }
            ]
        }
        ```
    """
    try:

        subscription_params = SubscriptionParams(**request.GET.dict())
    except ValidationError as e:
        error = [
            {
                "loc": x["loc"],
                "msg": x["msg"],
                "type": x["type"],
            }
            for x in e.errors()
        ]
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": error,
            }
        )
    latest_status_subquery = (
        SubscriptionStatus.objects.filter(subscription=OuterRef("pk"))
        .order_by("-created_at")
        .annotate(
            translated_status=Case(
                When(status=TypeSubscriptionStatus.CREATED, then=Value("Criado")),
                When(status=TypeSubscriptionStatus.CONFIRMED, then=Value("Confirmado")),
                When(status=TypeSubscriptionStatus.CANCELED, then=Value("Cancelado")),
                When(status=TypeSubscriptionStatus.UNSIGNED, then=Value("Desinscrito")),
                default=Value("Desconhecido"),
                output_field=CharField(),
            )
        )
        .values("translated_status")[:1]
    )

    subscriptions = (
        Subscription.objects.select_related("event")
        .prefetch_related("subscription_statuses")
        .filter(subscription_params.params)
        .values(*FIELDS_BY_SUBSCRIPTION_MODEL_DUMP)
        .annotate(
            status=Subquery(latest_status_subquery),
        )
        .order_by(subscription_params.order_by)
    )

    data = generate_pagination_by_models(subscriptions, subscription_params.page, subscription_params.limit)

    return JsonResponse(content=data)


@check_session_view("GET")
def detail_subscription(request: HttpRequest, subscription_uid: UUID) -> Union[JsonResponse, JsonResponseBadRequest]:
    """
    Retrieve the details of a subscription for the authenticated user.

    Args:
        request (HttpRequest): The HTTP request object containing user information.
        subscription_uid (UUID): The unique identifier of the subscription.

    Returns:
        Union[JsonResponse, JsonResponseBadRequest]: A JSON response with subscription details if found,
        otherwise a JSON response indicating the subscription was not found.

    Raises:
        Subscription.DoesNotExist: If the subscription with the given UID does not exist for the user.

    Example:
        Request:
        ```
        GET /subscriptions/123e4567-e89b-12d3-a456-426614174000/detail/
        ```

        Response:
        ```
        {
            "success": true,
            "data": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "event__title": "My Event",
                "event__description": "This is a test event",
                "event__start_at": "2022-01-01T12:00:00",
                "event__is_active": true,
                "created_at": "2022-01-01T12:00:00",
                "updated_at": "2022-01-01T12:00:00"
            }
        }
        ```
    """
    try:
        subscription = Subscription.objects.get(uid=subscription_uid, user=request.user)
    except Subscription.DoesNotExist:
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": [
                    {
                        "loc": "subscription_uid",
                        "msg": "Inscrição não encontrada",
                        "type": "not_found",
                    }
                ],
            }
        )

    return JsonResponse(
        content={
            "success": True,
            "data": subscription.model_dump(),
        }
    )


@check_session_view("GET")
def unsigned_subscription(request: HttpRequest, subscription_uid: UUID) -> Union[JsonResponse, JsonResponseBadRequest]:
    """
    Handle the unsubscription of a user from an event.

    Args:
        request (HttpRequest): The HTTP request object containing user information.
        subscription_uid (UUID): The unique identifier of the subscription.

    Returns:
        Union[JsonResponse, JsonResponseBadRequest]: A JSON response indicating the success or failure of the unsubscription process.

    Raises:
        Subscription.DoesNotExist: If the subscription with the given UID does not exist for the user.

    Example:
        Request:
        ```
        GET /subscriptions/123e4567-e89b-12d3-a456-426614174000/unsigned/
        ```

        Response:
        ```
        {
            "success": true,
            "msg": "Inscrição removida com sucesso"
        }
        ```
    """
    try:
        subscription = Subscription.objects.get(uid=subscription_uid, user=request.user)
    except Subscription.DoesNotExist:
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": [
                    {
                        "loc": "event_uid",
                        "msg": "Inscrição não encontrada",
                        "type": "not_found",
                    }
                ],
            }
        )

    status = subscription.subscription_statuses.last()
    if status.status == TypeSubscriptionStatus.UNSIGNED:
        return JsonResponseBadRequest(
            content={
                "success": False,
                "error": [
                    {
                        "loc": "status",
                        "msg": "Você já não é inscrito neste evento",
                        "type": "already_unsigned",
                    }
                ],
            }
        )

    SubscriptionStatus.objects.create(
        subscription=subscription,
        status=TypeSubscriptionStatus.UNSIGNED,
    )

    return JsonResponse(
        content={
            "success": True,
            "msg": "Inscrição removida com sucesso",
        }
    )
