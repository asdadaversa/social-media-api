from rest_framework import viewsets, generics, status, mixins
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from django.db.models.query import QuerySet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination

from social_media.permissions import IsOwnerOrReadOnly, AnonPermissionOnly, IsOwnerOrReadOnlyUserProfile, \
    IsOwnerOrReadOnlyDeleteComment, IsAdminOrOwner
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from social_media.models import Post, Commentary, Like
from social_media.serializers import PostSerializer, CommentarySerializer, PostImageSerializer, LikeSerializer, \
    CommentaryListSerializer, CommentaryPostSerializer, PostListSerializer
from user.models import UserProfile
from user.serializers import UserProfileDetailSerializer


def params_to_ints(qs):
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


def like_post(request, *args, **kwargs):
    pk = kwargs.get("pk")
    user = request.user.profile
    post = get_object_or_404(Post, pk=pk)

    if user.id in [post.user_id for post in post.post_likes.all()]:
        return Response({'message': f"You already liked this post"})
    Like.objects.create(user=user, post=post)
    return Response({'message': f"post was liked"})


def unlike_post(request, *args, **kwargs):
    pk = kwargs.get("pk")
    user = request.user.profile
    post = get_object_or_404(Post, pk=pk)
    like = Like.objects.filter(user=user, post=post).first()
    if like:
        like.delete()
        return Response({'message': f"you have unliked post"})
    return Response({'message': f"you never liked post"})


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

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    @action(
        methods=["GET", "PUT"],
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

    @action(
        methods=["GET", "POST"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def like_the_post(self, request, *args, **kwargs):
        return like_post(request, *args, **kwargs)

    @action(
        methods=["GET", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def unlike_the_post(self, request, *args, **kwargs):
        return unlike_post(request, *args, **kwargs)


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


class CommentaryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = Commentary.objects.all()
    serializer_class = CommentaryListSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = CommentaryPagination

    #add search


class LikeViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = CommentaryPagination


class CommentView(APIView):
    queryset = Commentary.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = CommentarySerializer

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = self.request.user.profile
        post = self.get_object()
        content = self.request.data["content"]
        if content:
            comment = Commentary.objects.create(user=user, post=post, content=content)
            serializer = CommentaryPostSerializer(comment)
            return Response(("Your commentary was posted", serializer.data), status=status.HTTP_201_CREATED)
        else:
            return Response("Cant post empty comment")


class CommentaryDeleteApiView(generics.DestroyAPIView):
    permission_classes = (IsOwnerOrReadOnlyDeleteComment,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Commentary, pk=pk)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        comment = self.get_object(pk)
        serializer = CommentaryListSerializer(comment)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        commentary = get_object_or_404(Commentary, pk=pk)
        commentary.delete()
        return Response({'message': f"commentary was successful deleted"})


class OwnCommentary(generics.ListAPIView):
    serializer_class = CommentaryListSerializer
    queryset = Commentary.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user.profile.id
        return Commentary.objects.filter(user_id=user)


class Likes(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return like_post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return unlike_post(request, *args, **kwargs)

