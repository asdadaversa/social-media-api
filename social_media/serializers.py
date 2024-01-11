from rest_framework import serializers

from social_media.models import Post, Commentary, Like


class CommentarySerializer(serializers.ModelSerializer):
    full_name = serializers.SlugRelatedField(source="user", slug_field="full_name", read_only=True, many=False)
    user_id = serializers.SlugRelatedField(source="user", slug_field="id", read_only=True, many=False)
    post_title = serializers.SlugRelatedField(source="post", slug_field="title", read_only=True, many=False)
    post_id = serializers.SlugRelatedField(source="post", slug_field="id", read_only=True, many=False)

    class Meta:
        model = Commentary
        fields = ("id", "user_id", "full_name", "content", "post_id", "post_title", "created_time")


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "created_time", "post")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="full_name", read_only=True)
    hashtags = serializers.CharField(allow_blank=True, style={'placeholder': 'type example: #tag1, #tag2'})
    likes = LikeSerializer(source="post_likes", many=True)

    class Meta:
        model = Post
        fields = ("id", "photo", "title", "content", "created_time", "author", "hashtags", "likes")
        read_only_fields = ("author", )

    def create(self, validated_data):

        author = self.context["request"].user.profile
        # title = validated_data["title"]
        # content = validated_data["content"]
        # photo = validated_data["photo"]
        # hashtags = validated_data["hashtags"]

        post = Post.objects.create(author=author, **validated_data)
        return post


class PostImageSerializer(serializers.ModelSerializer):
    model = Post
    fields = ("id", "photo")
