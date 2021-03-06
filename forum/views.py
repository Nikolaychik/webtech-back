from django.db.models import Count
from django.http import Http404
from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404

from rest_framework.response import Response
from forum.models import Post, PostReaction, PostComment, PostCategory, PostCommentReaction, User, Faculty
from forum.serializers import UserSerializer, PostDetailSerializer, PostListSerializer, \
    PostReactionSerializer, PostCommentSerializer, PostCategorySerializer, PostCommentReactionSerializer, \
    UserMeSerializer, FacultySerializer
from forum.tools import ReactionsTool, base64_file


def check_owner_permission(foo):
    def wrapper(self, request, *args, **kwargs):
        if self.request.user != self.get_object().owner:
            raise Http404
        return foo(self, request, *args, **kwargs)
    return wrapper


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        faculty_id = request.data.pop('faculty')
        cover_picture_base64 = request.data.get('avatar_picture')
        if cover_picture_base64:
            request.data['avatar_picture'] = base64_file(cover_picture_base64)

        response = super().create(request, *args, **kwargs)
        user = User.objects.get(id=response.data['id'])
        user.faculty = Faculty.objects.get(id=faculty_id)
        user.save()
        return response


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs["user_id"])


class UserMeDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        faculty_id = request.data.pop('faculty')
        if faculty_id:
            self.request.user.faculty = Faculty.objects.get(id=faculty_id)
            self.request.user.save()

        cover_picture_base64 = request.data.get('avatar_picture')
        if cover_picture_base64:
            request.data['avatar_picture'] = base64_file(cover_picture_base64)

        return super().update(request, *args, **kwargs)


class ListFacultiesView(generics.ListAPIView):
    serializer_class = FacultySerializer
    queryset = Faculty.objects.all()
    permission_classes = [permissions.AllowAny]


class ListCategoriesView(generics.ListAPIView):
    serializer_class = PostCategorySerializer
    queryset = PostCategory.objects.all()


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostListSerializer
    queryset = Post.objects.all()

    def create(self, request, *args, **kwargs):
        request.data['owner_id'] = request.user.id
        cover_picture_base64 = request.data.get('cover_picture')
        if cover_picture_base64:
            request.data['cover_picture'] = base64_file(cover_picture_base64)

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = Post.objects.all()

        owner_filter = self.request.query_params.get('owner_id')
        if owner_filter:
            qs = qs.filter(owner=owner_filter)
        category_filter = self.request.query_params.get('category_id')
        if category_filter:
            qs = qs.filter(category=category_filter)

        order = self.request.query_params.get('order')
        if order == 'new':
            qs = qs.order_by("-created_at")
        elif order == 'popular':
            qs = qs.annotate(num_reactions=Count('reactions')).order_by('-num_reactions')

        qs = qs.distinct()
        return qs


class PostDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostDetailSerializer

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs["post_id"])

    @check_owner_permission
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class PostReactionsUpdateView(generics.UpdateAPIView):
    serializer_class = PostReactionSerializer

    def get_object(self):
        """ rtype: PostReaction | None """
        return PostReaction.objects.filter(
            post=self.request.data["post_id"],
            user=self.request.user).first()

    def put(self, request, *args, **kwargs):
        user = request.user
        post_id, reaction_type = request.data["post_id"], request.data['reaction_type']
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


class PostCommentReactionsUpdateView(generics.UpdateAPIView):
    serializer_class = PostCommentReactionSerializer

    def get_object(self):
        """ rtype: PostCommentReaction | None """
        return PostCommentReaction.objects.filter(
            comment=self.request.data["comment_id"],
            user=self.request.user).first()

    def put(self, request, *args, **kwargs):
        user = request.user
        comment_id, reaction_type = request.data["comment_id"], request.data['reaction_type']
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

    @check_owner_permission
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
