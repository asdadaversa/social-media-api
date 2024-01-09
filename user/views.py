from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.settings import api_settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from django.db.models.query import QuerySet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from social_media.permissions import IsOwnerOrReadOnly, AnonPermissionOnly
from user.models import UserProfile, UserFollowing, User
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    UserProfileSerializer,
    UserProfileListSerializer,
    UserProfileDetailSerializer,
    UserOwnProfileSerializer,
    UserFollowingSerializer,
    UserProfilePhotoSerializer,
    FollowersSerializer,
    FollowingSerializer
)


class UserProfilesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ManageUserView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserOwnProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (AnonPermissionOnly,)


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response({'message': "Logout successful, token unvalidated, to access log in again"})


class UserProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = UserProfilesPagination

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        username = self.request.query_params.get("username")
        age = self.request.query_params.get("age")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        city = self.request.query_params.get("city")
        country = self.request.query_params.get("country")
        if username is not None:
            queryset = queryset.filter(username__icontains=username)
        if age is not None:
            queryset = queryset.filter(age__exact=age)
        if first_name is not None:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name is not None:
            queryset = queryset.filter(last_name__icontains=last_name)
        if city is not None:
            queryset = queryset.filter(city__icontains=city)
        if country is not None:
            queryset = queryset.filter(country__icontains=country)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return UserProfileListSerializer
        if self.action == "retrieve":
            return UserProfileDetailSerializer
        if self.action == "upload_image":
            return UserProfilePhotoSerializer
        return UserProfileSerializer

    @action(
        methods=["GET", "PUT", "POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAuthenticated],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific userprofile"""
        userprofile = self.get_object()
        serializer = self.get_serializer(userprofile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserFollowingViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = UserFollowingSerializer
    queryset = UserFollowing.objects.all()


class UserFollowers(generics.ListAPIView):
    serializer_class = FollowersSerializer
    queryset = UserFollowing.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user.profile.id
        return UserFollowing.objects.filter(you_follow_to_id=user)


class UserFollowings(generics.ListAPIView):
    queryset = UserFollowing.objects.all()
    serializer_class = FollowingSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user.profile.id
        return UserFollowing.objects.filter(your_followers_id=user)


class UserFollow(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self, pk):
        return UserProfile.objects.get(pk=pk)

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserProfileDetailSerializer(user)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        user = self.request.user.profile
        follow = self.get_object(pk)

        if user == follow:
            return Response({'message': f"You can't subscribe on your self"})
        if user.id in [follower.your_followers_id for follower in follow.following.all()]:
            return Response({'message': f"You already  follow user {follow.first_name} {follow.last_name}"})
        UserFollowing.objects.create(you_follow_to=follow, your_followers=user)

        serializer = UserProfileDetailSerializer(follow)
        first_name = serializer.data["first_name"]
        last_name = serializer.data["last_name"]
        user_id = serializer.data["id"]

        return Response({'message': f"You successful subscribe on {first_name} {last_name} (user_id: {user_id})"})

    def delete(self, request, pk, format=None):
        user = self.request.user.profile
        follow = self.get_object(pk)
        connection = UserFollowing.objects.filter(you_follow_to=follow, your_followers=user).first()
        connection.delete()
        serializer = UserProfileSerializer(follow)
        first_name = serializer.data["first_name"]
        last_name = serializer.data["last_name"]
        user_id = serializer.data["id"]

        return Response({'message': f"You successful unsubscribe from {first_name} {last_name} (user_id: {user_id})"})
