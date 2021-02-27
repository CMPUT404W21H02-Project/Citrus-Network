from django.contrib import admin
from .models import CitrusAuthor, Post, Comment


class CitrusAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'user', 'host', 'displayName', 'github',)


# class CitrusPostAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'description', 'content', 'author', 'commonmark', 'visibility',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('id','title','description','content','author','origin','commonmark','categories','public','private_to_author','private_to_friend','shared_with','created' )


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'comment', 'published', 'id')


admin.site.register(CitrusAuthor, CitrusAuthorAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
# admin.site.register(Post, CitrusPostAdmin)

