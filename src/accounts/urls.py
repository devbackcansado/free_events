from django.urls import path


from accounts.views import (
    create_user,
    login,
    logout,
    user_me,
    update_user,
    delete_user,
)


urlpatterns = [
    path("login/", login, name="login"),
    path("me/", user_me, name="user-me"),
    path("logout/", logout, name="logout"),
    path("create/", create_user, name="create-user"),
    path("update/", update_user, name="update-user"),
    path("delete/", delete_user, name="delete-user"),
]
