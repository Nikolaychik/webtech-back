from django.contrib.auth.models import AbstractUser
from django.db import models


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


