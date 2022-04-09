from __future__ import unicode_literals, absolute_import, division, print_function
from forum.models import PostReaction, Reactions, PostCommentReaction


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
