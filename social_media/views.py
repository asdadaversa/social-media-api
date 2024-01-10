from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from django.db.models.query import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from social_media.permissions import IsOwnerOrReadOnly, AnonPermissionOnly

from social_media.models import Post, Commentary
from social_media.serializers import PostSerializer, CommentarySerializer, PostImageSerializer
from user.models import UserProfile


def params_to_ints(qs):
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        title = self.request.query_params.get("title")
        content = self.request.query_params.get("content")
        hashtags = self.request.query_params.get("hashtags")
        author = self.request.query_params.get("author")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if content:
            queryset = queryset.filter(content__icontains=content)
        if hashtags:
            queryset = queryset.filter(hashtags__icontains=hashtags)
        if author:
            author_id = params_to_ints(author)
            queryset = queryset.filter(author__id__in=author_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "upload_image":
            return PostImageSerializer
        return PostSerializer

    @action(
        methods=["GET", "PUT", "POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAuthenticated],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific post"""
        userprofile = self.get_object()
        serializer = self.get_serializer(userprofile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnPostView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        user = self.request.user.profile.id
        return Post.objects.filter(author_id=user)


class FollowingPostView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        user = self.request.user.profile.id
        followers = UserProfile.objects.get(id=user).followers.all()
        ids = [users.you_follow_to_id for users in followers]

        return Post.objects.filter(author__id__in=ids)


class CommentaryViewSet(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = CommentarySerializer
    permission_classes = (IsOwnerOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
