from rest_framework import routers
from django.urls import path, include

from social_media.views import (
    PostViewSet,
)

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "social"
