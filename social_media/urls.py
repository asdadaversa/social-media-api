from rest_framework import routers
from django.urls import path, include

from social_media.views import (
    PostViewSet,
    OwnPostView,
    FollowingPostView,
    CommentaryViewSet,
    LikeViewSet
)

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")
router.register("comments-history", CommentaryViewSet, basename="comments-history")
router.register("likes-history", LikeViewSet, basename="likes-history")


urlpatterns = [
    path("posts/your-posts", OwnPostView.as_view(), name="your-post"),
    path("posts/following-post", FollowingPostView.as_view(), name="following-post"),
    path("", include(router.urls))
]

app_name = "social"
