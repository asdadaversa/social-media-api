from django.urls import path

from user.views import CreateUserView, CreateTokenView, ManageUserView, LogoutView


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

app_name = "user"

