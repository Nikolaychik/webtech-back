from rest_framework import serializers

from forum.models import User, Post, PostComment, PostReaction, Reactions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        user = self.context['request'].user
        attrs['user_id'] = user.id
        return attrs


class PostListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    category_name = serializers.CharField(source='category.name')
    title = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    cover_picture = serializers.ImageField(use_url=False)
    owner_id = serializers.IntegerField()
    owner_username = serializers.CharField(source='owner.username')
    owner_avatar_picture = serializers.ImageField(source='owner.avatar_picture', use_url=False)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    user_reaction_type = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, post):
        return post.comments.all().count()

    def get_likes_count(self, post):
        return post.reactions.filter(type=Reactions.LIKE_SHORT.value).count()

    def get_dislikes_count(self, post):
        return post.reactions.filter(type=Reactions.DISLIKE_SHORT.value).count()

    def get_user_reaction_type(self, post):
        # TODO: change to request user
        user = User.objects.first()
        user_reaction = post.reactions.filter(user=user).first()
        return user_reaction and user_reaction.type

    class Meta:
        model = Post
        fields = [
            'id',
            'category_id',
            'category_name',
            'title',
            'created_at',
            'updated_at',
            'cover_picture',
            'owner_id',
            'owner_username',
            'owner_avatar_picture',
            'likes_count',
            'dislikes_count',
            'user_reaction_type',
            'comments_count',
        ]


class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = '__all__'


class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = '__all__'

    # todo: refactor without to_representation
    def to_representation(self, instance):
        """
        :type instance: PostComment
        :rtype: dict
        """
        comment = instance
        return {
            "id": comment.id,
            "body": comment.body,
            "owner": comment.owner.username,
            "updated_at": comment.updated_at,
            "created_at": comment.created_at
        }


class PostDetailSerializer(PostListSerializer):
    comments = PostCommentSerializer(many=True)

    class Meta:
        model = Post
        fields = PostListSerializer.Meta.fields + [
            'comments',
        ]
