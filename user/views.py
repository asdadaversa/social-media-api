from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
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
from user.models import UserProfile
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    UserProfileSerializer,
    UserProfileListSerializer,
    UserProfileDetailSerializer,
    UserOwnProfileSerializer
)


class UserProfilesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ManageUserView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserOwnProfileSerializer
    authentication_classes = (TokenAuthentication,)

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
    permission_classes = (IsOwnerOrReadOnly,)
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
