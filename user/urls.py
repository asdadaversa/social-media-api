from rest_framework import routers
from django.urls import path, include

from user.views import (
    CreateUserView,
    CreateTokenView,
    LogoutView,
    UserProfileViewSet,
    UserFollowingViewSet,
    ManageUserView,
    UserFollowers,
    UserFollowings,
    UserFollow,
    api_root
)

router = routers.DefaultRouter()
router.register("users", UserProfileViewSet, basename="users")
router.register("following-history", UserFollowingViewSet, basename="following-history")


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ManageUserView .as_view(), name="profile"),
    # path("users/<int:pk>/", UserProfileViewSet.as_view({"get":"retrieve"}), name="userprofile-detail"),
    path("profile/followers/", UserFollowers.as_view(), name="followers"),
    path("profile/followings/", UserFollowings.as_view(), name="followings"),
    path("users/<int:pk>/follow/", UserFollow.as_view(), name="follow-detail"),
    path("", api_root),
    path("", include(router.urls))
]

app_name = "user"
