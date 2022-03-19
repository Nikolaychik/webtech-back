from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from forum.models import Post
from forum.serializers import UserSerializer, PostSerializer


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
