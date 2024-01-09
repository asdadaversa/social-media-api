from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

from social_media.permissions import IsOwnerOrReadOnly, AnonPermissionOnly
from social_media.models import Post, Commentary, PostHashtags
from social_media.serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
