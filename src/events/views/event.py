from uuid import UUID
from django.http import HttpRequest
from orjson import loads, JSONDecodeError
from pydantic import ValidationError
from typing import Union

from utils.response import JsonResponseBadRequest, JsonResponse
from utils.pagination import generate_pagination_by_models

from events.schemas.event import EventCreate, EventUpdate
from events.models import Event
from events.filters import EventParams

from accounts.decorators import check_session_view
from events.utils import FIELDS_BY_EVENT_MODEL_DUMP


@check_session_view("POST")
def create_event(request: HttpRequest) -> Union[JsonResponse, JsonResponseBadRequest]:
    """
    Create a new event.

    Args:
        body (EventCreate): The request body containing the event data.

    Returns:
        Union[JsonResponse, JsonResponseBadRequest]: A JsonResponse with the created event data
        if successful, or a JsonResponseBadRequest with error details if validation fails.

    Example:
        Request:
        ```
        POST /events/create/
        {
            "title": "My Event",
            "description": "This is a test event",
            "start_at": "2022-01-01T12:00:00",
            "address": "123 Main St"
        }
        ```

        Response:
        ```
        {
            "success": true,
            "data": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "promoter": "aa@aa.com",
                "title": "My Event",
                "description": "This is a test event",
                "address": "123 Main St",
                "start_at": "2022-01-01T12:00:00",
                "is_active": true
            }
        }
        ```
    """
    try:
        payload = EventCreate(**loads(request.body))
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

    event = Event.objects.create(
        title=payload.title,
        description=payload.description,
        start_at=payload.start_at,
        address=payload.address,
        promoter=request.user,
    )

    return JsonResponse(
        content={
            "success": True,
            "data": event.model_dump(),
        }
    )


@check_session_view("GET")
def list_events(request: HttpRequest) -> Union[JsonResponse, JsonResponseBadRequest]:
    """
    List all events.

    This view function handles GET requests to list all events.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Union[JsonResponse, JsonResponseBadRequest]: A JSON response containing
        the list of events if successful, or a JSON response indicating a bad
        request if an error occurs.

    Example:
        Request:
        ```
        GET /events/list/
        PARAMS: {
            "search": "My Event",
            "limit": 10,
            "page": 1,
            "order_by": "start_at",
            "order": "asc"
        }
        ```

        Response:
        ```
        {
            "success": true,
            "previous_page": null,
            "next_page": null,
            "num_pages": 1,
            "total": 10,
            "data": [
                {
                    "uid": "123e4567-e89b-12d3-a456-426614174000",
                    "promoter": "aa@aa.com",
                    "title": "My Event",
                    "description": "This is a test event",
                    "address": "123 Main St",
                    "start_at": "2022-01-01T12:00:00",
                    "is_active": true
                }
            ]
        }
        ```

    """
    try:
        event_params = EventParams(**request.GET.dict())
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

    events = (
        Event.objects.filter(event_params.params)
        .order_by(event_params.order_by)
        .values(
            *FIELDS_BY_EVENT_MODEL_DUMP,
        )
    )

    data = generate_pagination_by_models(events, event_params.page, event_params.limit)

    return JsonResponse(content=data)


@check_session_view("GET")
def detail_event(request: HttpRequest, event_uid: UUID) -> Union[JsonResponse, JsonResponseBadRequest]:
    """
    Retrieve event details based on the provided event UID.

    Args:
        request (HttpRequest): The HTTP request object.
        event_uid (UUID): The unique identifier of the event to retrieve.

    Returns:
        Union[JsonResponse, JsonResponseBadRequest]: A JSON response containing the event details if found,
        otherwise a JSON response indicating that the event was not found.

    Example:
        Request:
        ```
        GET /events/123e4567-e89b-12d3-a456-426614174000/detail/
        ```

        Response:
        ```
        {
            "success": true,
            "data": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "promoter": "aa@aa.com",
                "title": "My Event",
                "description": "This is a test event",
                "address": "123 Main St",
                "start_at": "2022-01-01T12:00:00",
                "is_active": true
            }
        }
        ```
    """
    try:
        event = Event.objects.get(uid=event_uid)
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

    return JsonResponse(
        content={
            "success": True,
            "data": event.model_dump(),
        }
    )


@check_session_view("PUT")
def update_event(request: HttpRequest, event_uid: UUID) -> Union[JsonResponse, JsonResponseBadRequest]:
    """
    Update an event based on the provided event UID and request payload.

    Args:
        request (HttpRequest): The HTTP request object containing the user and the request body.
        event_uid (UUID): The unique identifier of the event to be updated.
        body (EventUpdate): The request body containing the updated event data.

    Returns:
        Union[JsonResponse, JsonResponseBadRequest]: A JsonResponse indicating success with the updated event data,
        or a JsonResponseBadRequest indicating failure with error details.

    Raises:
        Event.DoesNotExist: If the event with the given UID does not exist for the current user.
        ValidationError: If the request body contains invalid data for updating the event.
        JSONDecodeError: If the request body is not a valid JSON.

    Example:
        Request:
        ```
        PUT /events/123e4567-e89b-12d3-a456-426614174000/update/
        {
            "title": "Updated Event",
            "description": "This is an updated event",
            "start_at": "2022-01-01T12:00:00",
            "address": "123 Main St",
            "is_active": true
        }
        ```

        Response:
        ```
        {
            "success": true,
            "data": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "promoter": "aa@aa.com",
                "title": "Updated Event",
                "description": "This is an updated event",
                "address": "123 Main St",
                "start_at": "2022-01-01T12:00:00",
                "is_active": true
            }
        }
        ```
    """
    try:
        event = Event.objects.get(uid=event_uid, promoter=request.user)
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

    try:
        payload = EventUpdate(**loads(request.body))
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

    for key, value in payload.model_dump().items():
        if value is not None:
            setattr(event, key, value)

    event.save()

    return JsonResponse(
        content={
            "success": True,
            "data": event.model_dump(),
        }
    )


@check_session_view("DELETE")
def delete_event(request: HttpRequest, event_uid: UUID) -> Union[JsonResponse, JsonResponseBadRequest]:
    """
    Deletes an event specified by its UID if it belongs to the requesting user.

    Args:
        request (HttpRequest): The HTTP request object containing user information.
        event_uid (UUID): The unique identifier of the event to be deleted.

    Returns:
        Union[JsonResponse, JsonResponseBadRequest]: A JSON response indicating success or failure.
            - If the event is successfully deleted, returns a JsonResponse with {"success": True}.
            - If the event does not exist or does not belong to the user, returns a JsonResponseBadRequest with an error message.

    Example:
        Request:
        ```
        DELETE /events/123e4567-e89b-12d3-a456-426614174000/delete/
        ```

        Response:
        ```
        {
            "success": true
        }
        ```
    """
    try:
        event = Event.objects.get(uid=event_uid, promoter=request.user)
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

    event.delete()

    return JsonResponse(
        content={
            "success": True,
        }
    )
