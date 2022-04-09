from rest_framework import serializers

from forum.tools import PostReactionsTool
from forum.models import User, Post, PostComment, PostReaction, PostCategory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        user = self.context['request'].user
        attrs['user_id'] = user.id
        return attrs


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        """
        :type instance: forum.models.Post
        :rtype: dict
        """
        post = instance
        reactions = PostReactionsTool.get_post_reactions(post.owner_id, post.id)
        comments = PostComment.objects.filter(post_id=post.id)

        return {
            "id": post.id,
            "category": post.category_id.name,
            "title": post.title,
            "created_at": post. created_at,
            "updated_at": post.updated_at,
            "cover_url": post.cover_url.path,
            "owner": post.owner_id.username,
            "reactions": reactions,
            "comments": len(comments)
        }


class PostSerializer(serializers.ModelSerializer):
    title = serializers.StringRelatedField(required=False)
    body = serializers.StringRelatedField(required=False)
    owner_id = serializers.RelatedField(read_only=True)

    class Meta:
        model = Post
        fields = "__all__"

    def to_representation(self, instance):
        """
        :type instance: forum.models.Post
        :rtype: dict
        """
        post = instance
        reactions = PostReactionsTool.get_post_reactions(post.owner_id, post.id)
        comments = PostComment.objects.filter(post_id=post.id)

        return {
            "id": post.id,
            "category_id": post.category_id.id,
            "category": post.category_id.name,
            "title": post.title,
            "body": post.body,
            "created_at": post. created_at,
            "updated_at": post.updated_at,
            "cover_url": post.cover_url.path,
            "owner": post.owner_id.username,
            "reactions": reactions,
            "comments": [PostCommentSerializer().to_representation(c) for c in comments]
        }


class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = '__all__'


class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = '__all__'

    def to_representation(self, instance):
        """
        :type instance: PostComment
        :rtype: dict
        """
        comment = instance
        return {
            "id": comment.id,
            "body": comment.body,
            "owner": comment.owner_id.username,
            "updated_at": comment.updated_at,
            "created_at": comment.created_at
        }
