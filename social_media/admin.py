from django.contrib import admin
from social_media.models import Post, Commentary, Like


class CommentsInline(admin.TabularInline):
    model = Commentary
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [CommentsInline]


admin.site.register(Commentary)
admin.site.register(Like)
