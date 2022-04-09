from django.contrib import admin

from forum.models import User, Faculty, Post, PostCategory, PostReaction, PostComment, PostCommentReaction

admin.site.register(User)
admin.site.register(Faculty)
admin.site.register(Post)
admin.site.register(PostCategory)
admin.site.register(PostReaction)
admin.site.register(PostComment)
admin.site.register(PostCommentReaction)
