from django.contrib import admin
from .models import Post, Like, View, Follow, Repost, ChatFiles, Notifications, Tag
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ['id','user','description','date']

class LikeAdmin(admin.ModelAdmin):
    list_display = ['post','user','date']

class ViewAdmin(admin.ModelAdmin):
    list_display = ['post','user','date']

# class CommentAdmin(admin.ModelAdmin):
#     list_display = ['post','user','date']

class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower','followed']

admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(Repost)
admin.site.register(ChatFiles)
admin.site.register(Notifications)
admin.site.register(Tag)
# admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)

