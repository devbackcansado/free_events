from django.urls import path, include


from events.views.event import (
    create_event,
    list_events,
    detail_event,
    update_event,
    delete_event,
)


urlpatterns = [
    path("create/", create_event, name="create-event"),
    path("list/", list_events, name="list-event"),
    path(
        "<uuid:event_uid>/",
        include(
            [
                path("detail/", detail_event, name="detail-event"),
                path("update/", update_event, name="update-event"),
                path("delete/", delete_event, name="delete-event"),
            ]
        ),
    ),
]
