from rest_framework import routers
from django.urls import path, include

from user.views import(
    CreateUserView,
    CreateTokenView,
    LogoutView,
    UserProfileViewSet,
    UserFollowingViewSet,
    ManageUserView,
    UserFollowers,
    UserFollowings,
)

router = routers.DefaultRouter()
router.register("users", UserProfileViewSet)
router.register("following_history", UserFollowingViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ManageUserView.as_view(), name="profile"),
    path("followers/", UserFollowers.as_view(), name="followers"),
    path("you_follow/", UserFollowings.as_view(), name="followers"),

    path("", include(router.urls))
]

app_name = "user"
