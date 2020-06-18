from .models import Post, Like, View, Follow
from rest_framework import serializers

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['url','post_file','user', 'current_length','date']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['url','post','user','date']

class ViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        fields = ['url','post','user','date']


# class CommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Comment
#         fields = ['url','post','user','date','comment']

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['url','follower','followed','date']