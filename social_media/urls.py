from rest_framework import routers
from django.urls import path, include

from social_media.views import (
    PostViewSet,
    OwnPostView,
    FollowingPostView,
)

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")

urlpatterns = [
    path("posts/your-posts", OwnPostView.as_view(), name="your-post"),
    path("posts/following-post", FollowingPostView.as_view(), name="following-post"),
    path("", include(router.urls))
]

app_name = "social"
