from django.contrib.auth.models import AbstractUser
from django.db import models


REACTION_CHOICES = (('l', 'Like'), ('d', 'Dislike'))


class Faculty(models.Model):
    full_name = models.CharField(max_length=120)
    short_name = models.CharField(max_length=120)


class User(AbstractUser):
    username = models.CharField(max_length=120, unique=True)
    password = models.CharField(max_length=250)
    USERNAME_FIELD = 'username'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar_url = models.ImageField(null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)


class PostCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(null=True)


class Post(models.Model):
    category_id = models.ForeignKey(PostCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    body = models.TextField()
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover_url = models.ImageField(null=True, upload_to='posts')


class PostReaction(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    type = models.CharField(choices=REACTION_CHOICES, max_length=20)


class PostComment(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    body = models.TextField()
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PostCommentReaction(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_id = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    type = models.CharField(choices=REACTION_CHOICES, max_length=20)
