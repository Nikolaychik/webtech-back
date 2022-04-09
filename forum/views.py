from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404

from rest_framework.response import Response
from forum.models import Post, PostReaction, PostComment, User, PostCategory, PostCommentReaction
from forum.serializers import UserSerializer, PostDetailSerializer, PostListSerializer, \
    PostReactionSerializer, PostCommentSerializer, PostCategorySerializer, PostCommentReactionSerializer
from forum.tools import ReactionsTool


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user


class ListCategoriesView(generics.ListAPIView):
    serializer_class = PostCategorySerializer
    queryset = PostCategory.objects.all()


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostListSerializer
    queryset = Post.objects.all()

    def create(self, request, *args, **kwargs):
        request.data['owner_id'] = request.user.id
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = Post.objects.all()
        order = self.request.query_params.get('order')
        if order == 'new':
            qs = qs.order_by("-created_at")
        elif order == 'popular':
            qs = qs.order_by('-reactions')
        return qs


class PostDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostDetailSerializer

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs["post_id"])


class PostReactionsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostReactionSerializer

    def get_object(self):
        """ rtype: PostReaction | None """
        return PostReaction.objects.filter(
            post=self.kwargs["post_id"],
            user=self.request.user).first()

    def put(self, request, *args, **kwargs):
        user = request.user
        post_id, reaction_type = kwargs["post_id"], kwargs['reaction_type']
        user_reaction = self.get_object()
        if not user_reaction:
            serializer = self.get_serializer(
                data={"user": user.id,
                      "post": post_id,
                      "type": reaction_type})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif user_reaction.type == reaction_type:
            user_reaction.delete()
        else:
            setattr(user_reaction, 'type', reaction_type)
            user_reaction.save()

        return Response(ReactionsTool.get_post_reactions(user, post_id))


class PostCommentReactionsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostCommentReactionSerializer

    def get_object(self):
        """ rtype: PostCommentReaction | None """
        return PostCommentReaction.objects.filter(
            comment=self.kwargs["comment_id"],
            user=self.request.user).first()

    def put(self, request, *args, **kwargs):
        user = request.user
        comment_id, reaction_type = kwargs["comment_id"], kwargs['reaction_type']
        user_reaction = self.get_object()
        if not user_reaction:
            serializer = self.get_serializer(
                data={"user": user.id,
                      "comment": comment_id,
                      "type": reaction_type})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif user_reaction.type == reaction_type:
            user_reaction.delete()
        else:
            setattr(user_reaction, 'type', reaction_type)
            user_reaction.save()

        return Response(ReactionsTool.get_post_comment_reactions(user, comment_id))


class PostCommentsListCreateView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    queryset = PostComment.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, post_id=self.kwargs["post_id"])

    def create(self, request, *args, **kwargs):
        request.data['post_id'] = int(self.kwargs["post_id"])
        request.data['owner_id'] = request.user.id
        return super().create(request, *args, **kwargs)


class PostCommentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostCommentSerializer

    def get_object(self):
        return get_object_or_404(
            PostComment,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"]
        )
