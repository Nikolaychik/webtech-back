from rest_framework import serializers

from forum.models import User, Post, PostComment, PostReaction, Reactions, Faculty


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'faculty',
            'speciality',
            'course_number',
        )

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This username is already taken")

        return username

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            faculty=validated_data['faculty'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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
        user_reaction = post.reactions.filter(user=self.context['request'].user).first()
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
