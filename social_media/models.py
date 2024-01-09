import os
import uuid

from django.db import models
from django.conf import settings
from django.utils.text import slugify
import user.models


def post_image_file_path(instance, filename):
    filename_without_ext, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/post/", filename)


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    # hashtags = models.ManyToManyField("PostHashtags", blank=True, related_name="posts")
    created_time = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(blank=True, null=True, upload_to=post_image_file_path)

    author = models.ForeignKey(
        user.models.UserProfile,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    class Meta:
        ordering = ("-created_time", )

    def __str__(self) -> str:
        return (f"owner:{self.author},"
                f"title: {self.title},"
                f"created: {self.created_time}")


class PostHashtags(models.Model):
    hashtag = models.CharField(max_length=20, null=False)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="hashes"
    )

    def __str__(self):
        return f"#{self.hashtag}"


class Commentary(models.Model):
    user = models.ForeignKey(
        user.models.UserProfile,
        on_delete=models.DO_NOTHING,
        related_name="comments"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="posts")
    created_time = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=255)

    class Meta:
        ordering = ("-created_time", )

    def __str__(self) -> str:
        return f"user:{self.user}, created: {self.created_time}"
