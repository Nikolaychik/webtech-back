from rest_framework import generics
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from forum.models import Post, PostReaction, Reactions, PostComment
from forum.serializers import UserSerializer, PostSerializer, \
    PostReactionSerializer, PostCommentSerializer


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


class PostReactionsListCreateView(generics.ListCreateAPIView):
    serializer_class = PostReactionSerializer
    queryset = PostReaction.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user
        post_id = int(self.kwargs["post_id"])

        post_reactions = {r for r in self.get_queryset() if r.post_id.id == post_id}
        likes = {r for r in post_reactions if r.type == Reactions.LIKE_SHORT.value}
        dislikes = post_reactions - likes

        if user in [r.user_id for r in likes]:
            user_reaction = Reactions.LIKE.value
        elif user in [r.user_id for r in dislikes]:
            user_reaction = Reactions.DISLIKE.value
        else:
            user_reaction = None

        return Response({
            "likes": len(likes),
            "dislikes": len(dislikes),
            "user_reaction": user_reaction
        })


class PostCommentsListCreateView(generics.ListCreateAPIView):
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
