from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/",
        include(
            [
                path(
                    "v1/",
                    include(
                        [
                            path("dashboards/", include("dashboards.urls")),
                            path("accounts/", include("accounts.urls")),
                            path("events/", include("events.urls.event")),
                            path("subscriptions/", include("events.urls.subscription")),
                        ]
                    ),
                ),
            ]
        ),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Free Events Administration"
admin.site.site_title = "Free Events"
admin.site.index_title = "Free Events Administration"
