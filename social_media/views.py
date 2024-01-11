from rest_framework import viewsets, generics, status, mixins
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from django.db.models.query import QuerySet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination
from social_media.permissions import IsOwnerOrReadOnly, AnonPermissionOnly, IsOwnerOrReadOnlyUserProfile

from social_media.models import Post, Commentary, Like
from social_media.serializers import PostSerializer, CommentarySerializer, PostImageSerializer, LikeSerializer
from user.models import UserProfile


def params_to_ints(qs):
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class CommentaryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


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

    @action(
        methods=["PUT", "GET"],
        detail=True,
        url_path="upload-photo",
        permission_classes=[IsAdminUser],
    )
    def upload_photo(self, request, pk=None):
        """Endpoint for uploading image to specific userprofile"""
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


class CommentaryViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Commentary.objects.all()
    serializer_class = CommentarySerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = CommentaryPagination


class LikeViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = CommentaryPagination
