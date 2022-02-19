from django.contrib import admin

from forum.models import User, Faculty, UserProfile


admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Faculty)
