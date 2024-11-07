from django.http import HttpResponse, HttpResponseBadRequest
from orjson import dumps


class JsonResponseBadRequest(HttpResponseBadRequest):
    """
    A custom HttpResponseBadRequest class that returns a JSON response.

    Args:
        content (Any, optional): The content to be included in the response.
            Defaults to None.

    Other arguments are passed to the parent class constructor.

    Example:
        response = JsonResponseBadRequest({"error": "Bad request"})
    """

    def __init__(self, content={}, *args, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        super().__init__(dumps(content), *args, **kwargs)


class JsonResponse(HttpResponse):
    """
    A custom HTTP response class that serializes content to JSON.

    Args:
        content (Any, optional): The content to be serialized to JSON. Defaults to None.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Example:
        response = JsonResponse({"success": True})

    """

    def __init__(self, content={}, *args, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        super().__init__(dumps(content), *args, **kwargs)


class UnauthorizedResponse(HttpResponse):
    """
    Represents an HTTP response indicating that the request is unauthorized.

    Example:
        response = UnauthorizedResponse()
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        super().__init__(
            content=dumps({"success": False, "error": "Não Autorizado"}),
            status=401,
            *args,
            **kwargs,
        )


class NotAllowedResponse(HttpResponse):
    """
    Represents a custom HTTP response for a not allowed request.

    Args:
        permitted_method (str): The permitted HTTP method.

    Example:
        response = NotAllowedResponse("GET")
    """

    def __init__(self, permitted_method: str, *args, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        super().__init__(
            content=dumps(
                {
                    "success": False,
                    "error": f"Metodo Não Permitido, somente permitido: {permitted_method}",
                }
            ),
            status=405,
            *args,
            **kwargs,
        )
