from django.http import HttpRequest

from django.contrib.auth import get_user_model

from typing import Optional
from utils.response import UnauthorizedResponse, NotAllowedResponse
from django.contrib.sessions.models import Session
from django.utils import timezone

from django.contrib.auth import get_user_model

_User = get_user_model()


def auth_access(request: HttpRequest) -> Optional[UnauthorizedResponse]:
    """
    Authenticates the access based on the HTTP Authorization header.

    This function checks the HTTP Authorization header in the request to
    authenticate the user. It supports Bearer token authentication.

    Args:
        request (HttpRequest): The HTTP request object containing the
                               Authorization header.

    Returns:
        Optional[UnauthorizedResponse]: Returns an UnauthorizedResponse if
                                        authentication fails, otherwise None.
    """

    http_auth = request.META.get("HTTP_AUTHORIZATION")

    if not http_auth:
        return UnauthorizedResponse()

    type_access, key = http_auth.split(" ")

    request.user = None
    if type_access != "Bearer":
        return UnauthorizedResponse()

    try:
        session = Session.objects.get(session_key=key)
    except Session.DoesNotExist:
        return UnauthorizedResponse()

    if session.expire_date < timezone.now():
        session.delete()

        return UnauthorizedResponse()

    try:
        user = _User.objects.get(
            id=session.get_decoded()["_auth_user_id"],
            is_active=True,
        )
    except _User.DoesNotExist:
        return UnauthorizedResponse()

    request.user = user
    return None


def check_session_view(method: str) -> callable:
    """
    Decorator that checks if the request method matches the specified method
    and if the user is authenticated.

    Args:
        method (str): The allowed request method.

    Returns:
        callable: The decorated view function.

    """

    def decorator(view):
        def wrapper(request, *args, **kwargs):
            if request.method != method:
                return NotAllowedResponse(
                    permitted_method=method,
                )

            error = auth_access(request)
            if error is not None:
                return error

            return view(request, *args, **kwargs)

        wrapper.csrf_exempt = True

        return wrapper

    return decorator
