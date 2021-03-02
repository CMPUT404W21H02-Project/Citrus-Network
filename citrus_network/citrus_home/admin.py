from django.contrib import admin
from .models import CitrusAuthor, Post, Comment,Friend,Follower

class CitrusAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'user', 'host', 'displayName','url', 'github',)


# class CitrusPostAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'description', 'content', 'author', 'commonmark', 'visibility',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('id','title','description','content','author','origin','commonmark','categories','visibility','created' )


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'comment', 'published', 'id')


class FriendAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'friends_uuid',)

class FollowerAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'followers_uuid',)

admin.site.register(CitrusAuthor, CitrusAuthorAdmin,)

admin.site.register(Friend, FriendAdmin,)

admin.site.register(Follower, FollowerAdmin,)

admin.site.register(Post, PostAdmin)

admin.site.register(Comment, CommentAdmin)