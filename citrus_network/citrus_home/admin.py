from django.contrib import admin
from .models import CitrusAuthor,Friend,Follower


class CitrusAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'user', 'host', 'displayName', 'github',)

class FriendAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'friends_uuid',)

class FollowerAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'followers_uuid',)

admin.site.register(CitrusAuthor, CitrusAuthorAdmin,)

admin.site.register(Friend, FriendAdmin,)

admin.site.register(Follower, FollowerAdmin,)