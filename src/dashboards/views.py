from accounts.decorators import check_session_view
from utils.response import JsonResponseBadRequest, JsonResponse
from utils.pagination import generate_pagination_by_sql
from dashboards.filters import EventParamsDashboard
from pydantic import ValidationError
from sql import FETCH_DASHBOARDS_EVENTS
from django.db import connection
from utils.models import dict_fetchall
from orjson import loads


@check_session_view("GET")
def dashboard(request):
    """
    Handles the dashboard view for fetching and displaying event data.

    Args:
        request (HttpRequest): The HTTP request object containing GET parameters.

    Returns:
        JsonResponse: A JSON response containing paginated event data or an error message.

    Example:
        >>> dashboard(request)
       {
        "success": true,
        "previous_page": null,
        "next_page": null,
        "num_pages": 1,
        "total": 2,
        "data": [
            {
            "total": 2,
            "uid": "101dc542-6115-4ce9-b113-514411b7dc93",
            "title": "São João ",
            "description": "O Melhor São João do Brasil",
            "address": "rua 1",
            "start_at": "2025-06-24T00:00:00",
            "is_active": true,
            "created_at": "2024-10-31T23:59:18.037281",
            "updated_at": "2024-10-31T23:59:18.037306",
            "list_subscriptions": [
                {
                "uid": "1efe9a37-3b55-4757-8437-5197bf090671",
                "email": "aa@aa.com",
                "status": "Desinscrito"
                }
            ]
            },
            {
            "total": 2,
            "uid": "fbdbe5fe-3d3c-4ce4-8486-09796c5b1cfc",
            "title": "São João",
            "description": "O São João do Brasil",
            "address": "rua 1",
            "start_at": "2025-06-24T00:00:00",
            "is_active": true,
            "created_at": "2024-11-01T00:03:03.028613",
            "updated_at": "2024-11-01T00:03:03.028754",
            "list_subscriptions": []
            }
            ]
        }

    """
    try:
        event_params = EventParamsDashboard(**request.GET.dict())
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

    with connection.cursor() as cursor:
        cursor.execute(FETCH_DASHBOARDS_EVENTS, [event_params.limit, event_params.offset])
        events = dict_fetchall(cursor)

    [event.update({"list_subscriptions": loads(event["list_subscriptions"])}) for event in events]

    data = generate_pagination_by_sql(events, event_params.page, event_params.limit)
    return JsonResponse(content=data)
