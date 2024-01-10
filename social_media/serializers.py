from rest_framework import serializers

from social_media.models import Post, Commentary


class CommentarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentary
        fields = ("id", "user", "created_time", "content", "post")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="full_name", read_only=True)
    hashtags = serializers.CharField(allow_blank=True, style={'placeholder': 'type example: #tag1, #tag2'})

    class Meta:
        model = Post
        fields = ("id", "photo", "title", "content", "created_time", "author", "hashtags")
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
