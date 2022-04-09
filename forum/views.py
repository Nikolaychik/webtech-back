from rest_framework import generics
from rest_framework.generics import get_object_or_404

from rest_framework.response import Response
from forum.models import Post, PostReaction, PostComment, User
from forum.serializers import UserSerializer, PostDetailSerializer, PostListSerializer, \
    PostReactionSerializer, PostCommentSerializer
from forum.tools import PostReactionsTool


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostListSerializer
    queryset = Post.objects.all()

    def create(self, request, *args, **kwargs):
        # TODO: change to request.user
        request.data['owner_id'] = User.objects.first().id
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

    def get_the_object(self, user):
        """ rtype: PostReaction | None """
        return PostReaction.objects.filter(
            post=self.kwargs["post_id"],
            user=user).first()

    def put(self, request, *args, **kwargs):
        # TODO: change to request user
        user = User.objects.first()
        post_id, reaction_type = kwargs["post_id"], kwargs['reaction_type']
        user_reaction = self.get_the_object(user)
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

        return Response(PostReactionsTool.get_post_reactions(user, post_id))


class PostCommentsListCreateView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    queryset = PostComment.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, post_id=self.kwargs["post_id"])

    def create(self, request, *args, **kwargs):
        from ipdb import set_trace; set_trace()
        request.data['post_id'] = int(self.kwargs["post_id"])
        # TODO: change to request.user
        request.data['owner_id'] = User.objects.first().id
        return super().create(request, *args, **kwargs)


class PostCommentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostCommentSerializer

    def get_object(self):
        return get_object_or_404(
            PostComment,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"]
        )
