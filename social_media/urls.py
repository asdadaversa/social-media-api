from rest_framework import routers
from django.urls import path, include

from social_media.views import (
    PostViewSet,
    OwnPostView,
    FollowingPostView,
    CommentaryViewSet,
    LikeViewSet,
    CommentView,
    CommentaryDeleteApiView,
    OwnCommentary,
    Likes,
    LikedPostView
)

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")
router.register("comments-history", CommentaryViewSet, basename="comments-history")
router.register("likes-history", LikeViewSet, basename="likes-history")


urlpatterns = [
    path("posts/your-posts", OwnPostView.as_view(), name="your-post"),
    path("posts/following-post", FollowingPostView.as_view(), name="following-post"),
    path("posts/<int:pk>/comment/", CommentView.as_view(), name="comment-post"),
    path("comment/<int:pk>/delete/", CommentaryDeleteApiView.as_view(), name="comment-delete"),
    path("comment/own-commentary/", OwnCommentary.as_view(), name="own-commentary"),
    path("posts/<int:pk>/like/", Likes.as_view(), name="like-post"),
    path("posts/liked/", LikedPostView.as_view(), name="liked"),
    path("", include(router.urls))
]

app_name = "social"
