from django.contrib import admin
from social_media.models import Post, PostHashtags, Commentary


class PostHashtagsTagInline(admin.StackedInline):
    model = PostHashtags
    extra = 1


class CommentsInline(admin.TabularInline):
    model = Commentary
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostHashtagsTagInline, CommentsInline]


admin.site.register(PostHashtags)
admin.site.register(Commentary)
