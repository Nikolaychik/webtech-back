from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib.auth.models import AnonymousUser
from rest_framework.response import Response

from forum.models import PostReaction, Reactions


class PostReactionsTool():
    @classmethod
    def get_post_reactions(cls, user, post_id):
        post_reactions = PostReaction.objects.filter(post_id=post_id)

        likes = set(post_reactions.filter(type=Reactions.LIKE_SHORT.value))
        dislikes = set(post_reactions) - likes

        user_reaction = None
        if not isinstance(user, AnonymousUser):
            user_reaction = post_reactions.filter(post_id=post_id, user_id=user).first()

        return Response({
            "likes": len(likes),
            "dislikes": len(dislikes),
            "user_reaction": user_reaction and user_reaction.type
        })
