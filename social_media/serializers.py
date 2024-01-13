from rest_framework import serializers

from social_media.models import Post, Commentary, Like


class CommentarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentary
        fields = ("id", "user", "post", "content", "created_time")
        read_only_fields = ("user", "post")


class CommentaryListSerializer(CommentarySerializer):
    full_name = serializers.SlugRelatedField(
        source="user",
        slug_field="full_name",
        read_only=True,
        many=False
    )
    user_id = serializers.SlugRelatedField(
        source="user",
        slug_field="id",
        read_only=True,
        many=False
    )
    post_title = serializers.SlugRelatedField(
        source="post",
        slug_field="title",
        read_only=True,
        many=False
    )
    post_id = serializers.SlugRelatedField(
        source="post",
        slug_field="id",
        read_only=True,
        many=False
    )

    class Meta:
        model = Commentary
        fields = (
            "id",
            "user_id",
            "full_name",
            "content",
            "post_id",
            "post_title",
            "created_time"
        )


class CommentaryPostSerializer(CommentarySerializer):
    author = serializers.SlugRelatedField(
        source="user",
        slug_field="full_name",
        read_only=True,
        many=False
    )

    class Meta:
        model = Commentary
        fields = ("id", "author", "content", "created_time")


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "created_time", "post")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="full_name",
        read_only=True
    )
    hashtags = serializers.CharField(
        allow_blank=True,
        style={'placeholder': 'type example: #tag1, #tag2'}
    )
    comments = CommentaryPostSerializer(
        source="posts",
        many=True,
        read_only=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "photo",
            "title",
            "content",
            "created_time",
            "author",
            "hashtags",
            "comments_count",
            "likes_count",
            "comments"
        )
        read_only_fields = ("author", )

    def create(self, validated_data):

        author = self.context["request"].user.profile
        post = Post.objects.create(author=author, **validated_data)
        return post


class PostListSerializer(PostSerializer):
    author = serializers.SlugRelatedField(
        slug_field="full_name",
        read_only=True
    )
    hashtags = serializers.CharField(
        allow_blank=True,
        style={'placeholder': 'type example: #tag1, #tag2'}
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "photo",
            "title",
            "content",
            "created_time",
            "author",
            "hashtags",
            "comments_count",
            "likes_count"
        )
        read_only_fields = ("author", )


class PostImageSerializer(serializers.ModelSerializer):
    model = Post
    fields = ("id", "photo")
