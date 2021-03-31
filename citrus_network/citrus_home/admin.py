from django.contrib import admin
from .models import CitrusAuthor, Post, Comment, Friend, Follower, Node,Inbox, Like

class CitrusAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'user', 'host', 'displayName','url', 'github',)


# class CitrusPostAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'description', 'content', 'author', 'commonmark', 'visibility',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('type',
                    'title',
                    'id',
                    'source',
                    'origin',
                    'description',
                    'contentType',
                    'content',
                    'author',
                    'categories',
                    'count',
                    'size',
                    'comments',
                    'published',
                    'visibility',
                    'unlisted',
                    'shared_with')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'comment', 'published', 'id')


class FriendAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'friends_uuid',)

class FollowerAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'followers_uuid',)

class NodeAdmin(admin.ModelAdmin):
    list_display = ('host', 'node_username', 'node_password',)

class LikeAdmin(admin.ModelAdmin):
    list_display = ('author', 'post_id', 'comment_id')

class InboxAdmin(admin.ModelAdmin):
    list_display = ('author', 'items')

admin.site.register(CitrusAuthor, CitrusAuthorAdmin,)

admin.site.register(Friend, FriendAdmin,)

admin.site.register(Follower, FollowerAdmin,)

admin.site.register(Post, PostAdmin)

admin.site.register(Comment, CommentAdmin)

admin.site.register(Node, NodeAdmin,)

admin.site.register(Inbox, InboxAdmin)

admin.site.register(Like, LikeAdmin,)
