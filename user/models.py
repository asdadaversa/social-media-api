import os
import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator


def user_image_file_path(instance, filename):
    filename_without_ext, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.last_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/users/", filename)


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class UserProfile(models.Model):
    class GenderChoices(models.TextChoices):
        FEMALE = "Female"
        MALE = "Male"

    email = models.OneToOneField(User, unique=True, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(blank=True, null=True, validators=[MaxValueValidator(120), MinValueValidator(1)])
    gender = models.CharField(max_length=50, choices=GenderChoices.choices, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(blank=True, null=True, upload_to=user_image_file_path)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "profiles"
        ordering = ["id"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def total_followers(self):
        return self.following.count()

    @property
    def total_follow_to(self):
        return self.followers.count()

    def __str__(self):
        return f"{self.full_name}, email: {self.email}"


class UserFollowing(models.Model):

    your_followers = models.ForeignKey(UserProfile, related_name="followers", on_delete=models.CASCADE)
    you_follow_to = models.ForeignKey(UserProfile, related_name="following", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["you_follow_to", "your_followers"],  name="unique_followers")
        ]

        ordering = ["-created"]

    def __str__(self):
        return f"{self.you_follow_to} follows {self.your_followers}"
