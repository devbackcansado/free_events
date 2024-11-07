from django.urls import path


from dashboards.views import dashboard


urlpatterns = [
    path("", dashboard, name="dashboard"),
]
