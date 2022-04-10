from __future__ import unicode_literals, absolute_import, division, print_function
import base64
from django.core.files.base import ContentFile
from uuid import uuid4
from forum.models import PostReaction, Reactions, PostCommentReaction


def base64_file(data, name=None):
    _format, _img_str = data.split(';base64,')
    _, ext = _format.split('/')
    if not name:
        name = uuid4().hex
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))


class ReactionsTool():
    @classmethod
    def get_post_reactions(cls, user, post_id):
        post_reactions = PostReaction.objects.filter(post_id=post_id)

        likes = set(post_reactions.filter(type=Reactions.LIKE_SHORT.value))
        dislikes = set(post_reactions) - likes
        user_reaction = post_reactions.filter(post_id=post_id, user_id=user).first()

        return {
            "likes": len(likes),
            "dislikes": len(dislikes),
            "user_reaction": user_reaction and user_reaction.type
        }

    @classmethod
    def get_post_comment_reactions(cls, user, comment_id):
        comment_reactions = PostCommentReaction.objects.filter(comment_id=comment_id)

        likes = set(comment_reactions.filter(type=Reactions.LIKE_SHORT.value))
        dislikes = set(comment_reactions) - likes
        user_reaction = comment_reactions.filter(comment_id=comment_id, user_id=user).first()

        return {
            "likes": len(likes),
            "dislikes": len(dislikes),
            "user_reaction": user_reaction and user_reaction.type
        }
