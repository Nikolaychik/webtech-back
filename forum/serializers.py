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
    id = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField()
    category_name = serializers.CharField(source='category.name', required=False)
    title = serializers.CharField()
    body = serializers.CharField()
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
    cover_picture = serializers.ImageField(use_url=False, required=False)
    owner_id = serializers.IntegerField(required=False)
    owner_username = serializers.CharField(source='owner.username', required=False)
    owner_avatar_picture = serializers.ImageField(source='owner.avatar_picture', use_url=False, required=False)
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
            'body',
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
    id = serializers.IntegerField(required=False)
    post_id = serializers.IntegerField()
    body = serializers.CharField()
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
    owner_id = serializers.IntegerField(required=False)
    owner_username = serializers.CharField(source='owner.username', required=False)
    owner_avatar_picture = serializers.ImageField(source='owner.avatar_picture',
                                                  use_url=False, required=False)
    # TODO:
    # likes_count = serializers.SerializerMethodField()
    # dislikes_count = serializers.SerializerMethodField()
    # user_reaction_type = serializers.SerializerMethodField()
    class Meta:
        model = PostComment
        fields = [
            'id',
            'body',
            'post_id',
            'created_at',
            'updated_at',
            'owner_id',
            'owner_username',
            'owner_avatar_picture',
        ]


class PostDetailSerializer(PostListSerializer):
    comments = PostCommentSerializer(many=True)

    class Meta:
        model = Post
        fields = PostListSerializer.Meta.fields + [
            'comments',
        ]
