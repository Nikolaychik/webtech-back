from django.contrib.auth.models import AnonymousUser
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from forum.models import Post, PostReaction, PostComment, User
from forum.serializers import UserSerializer, PostSerializer, \
    PostReactionSerializer, PostCommentSerializer
from forum.tools import PostReactionsTool


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

    def get(self, request, *args, **kwargs):
        return PostReactionsTool.get_post_reactions(self.request.user, self.kwargs["post_id"])


class PostReactionsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostReactionSerializer

    def get_object(self):
        """ rtype: PostReaction | None """
        return PostReaction.objects.filter(
            post_id=self.kwargs["post_id"],
            user_id=self.request.user).first()

    def put(self, request, *args, **kwargs):
        post_id, reaction_type = kwargs["post_id"], kwargs['reaction_type']
        user_reaction = self.get_object()
        if not user_reaction:
            serializer = self.get_serializer(
                data={"user_id": request.user.id,
                      "post_id": post_id,
                      "type": reaction_type})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif user_reaction.type == reaction_type:
            user_reaction.delete()
        else:
            setattr(user_reaction, 'type', reaction_type)
            user_reaction.save()

        return PostReactionsTool.get_post_reactions(request.user, post_id)


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
