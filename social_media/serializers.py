from rest_framework import serializers

from social_media.models import Post, Commentary, PostHashtags


class CommentarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentary
        fields = ("id", "user", "created_time", "content", "post")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="full_name", read_only=True)
    comments = CommentarySerializer(source="posts", many=True, read_only=False)

    class Meta:
        model = Post
        fields = ("id", "photo", "title", "content", "created_time", "author", "comments")
        read_only_fields = ("author", )

    def create(self, validated_data):
        author = self.context["request"].user.profile
        title = validated_data["title"]
        content = validated_data["content"]
        photo = validated_data["photo"]

        post = Post.objects.create(
            author=author,
            title=title,
            content=content,
            photo=photo,
        )
        return post


class PostHashtagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostHashtags
        fields = ("id", "hashtag", "post")
