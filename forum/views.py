from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from forum.models import Post, PostComment
from forum.serializers import UserSerializer, PostSerializer, PostCommentSerializer


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


class PostDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs["post_id"])


class PostCommentsView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    queryset = PostComment.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, post_id=self.kwargs["post_id"])


class PostCommentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostCommentSerializer

    def get_object(self):
        return get_object_or_404(
            PostComment,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"]
        )
