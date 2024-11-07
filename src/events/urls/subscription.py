from django.urls import path, include


from events.views.subscription import (
    create_subscription,
    list_subscription,
    detail_subscription,
    unsigned_subscription,
)


urlpatterns = [
    path("create/", create_subscription, name="create-subscription"),
    path("list/", list_subscription, name="list-subscription"),
    path(
        "<uuid:subscription_uid>/",
        include(
            [
                path("detail/", detail_subscription, name="detail-subscription"),
                path("unsigned/", unsigned_subscription, name="unsigned-subscription"),
            ]
        ),
    ),
]
