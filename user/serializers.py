from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from django.core import exceptions
from user.models import UserProfile, User, UserFollowing


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ("id", "email_id", "first_name", "last_name", "city", "country", "age", "gender", "bio", "registered_at")


class UserProfileDetailSerializer(UserProfileSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "photo",
            "id",
            "first_name",
            "last_name",
            "city",
            "country",
            "age",
            "gender",
            "bio",
            "registered_at",
            "total_followers",
            "total_follow_to"
        )


class UserProfileListSerializer(UserProfileSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "id",
            "photo",
            "first_name",
            "last_name",
            "city",
            "country",
            "age",
            "registered_at",
            "total_followers",
            "total_follow_to"
        )


class UserProfileFollowerSerializer(UserProfileSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "photo",
            "id",
            "full_name",
            "city",
            "country",
            "age",
        )


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff", "profile")
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and profile and return it"""
        user = User.objects.create(email=validated_data["email"])
        profile_data = validated_data.pop("profile")
        first_name = profile_data["first_name"]
        last_name = profile_data["last_name"]
        age = profile_data["age"]
        country = profile_data["country"]
        gender = profile_data["gender"]
        city = profile_data["city"]
        bio = profile_data["bio"]
        userprofile = UserProfile.objects.create(
            email=user,
            first_name=first_name,
            last_name=last_name,
            city=city,
            age=age,
            country=country,
            gender=gender,
            bio=bio,
        )
        return user

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise exceptions.ValidationError(msg)
            else:
                msg = _("Unable to log in with provided credentials.")
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        data["user"] = user
        return data


class UserProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "photo")


class UserFollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFollowing
        fields = ("id", "your_followers", "you_follow_to", "created")


class FollowingSerializer(UserFollowingSerializer):
    full_name = serializers.SlugRelatedField(source="you_follow_to", slug_field="full_name", read_only=True, many=False)
    followers_since = serializers.DateTimeField(source="created")
    info = UserProfileFollowerSerializer(source="you_follow_to")

    class Meta:
        model = UserFollowing
        fields = ("full_name", "followers_since", "info")


class FollowersSerializer(UserFollowingSerializer):
    full_name = serializers.SlugRelatedField(source="your_followers", slug_field="full_name", read_only=True, many=False)
    followers_since = serializers.DateTimeField(source="created")
    info = UserProfileFollowerSerializer(source="your_followers")

    class Meta:
        model = UserFollowing
        fields = ("full_name", "followers_since", "info")


class UserOwnProfileSerializer(UserProfileSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "photo",
            "email",
            "first_name",
            "last_name",
            "city",
            "country",
            "age",
            "gender",
            "bio",
            "registered_at",
            "total_followers",
            "total_follow_to",
        )
