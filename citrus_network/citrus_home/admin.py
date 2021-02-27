from django.contrib import admin
from .models import CitrusAuthor, Post


class CitrusAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'user', 'host', 'displayName', 'github',)


class CitrusPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'content', 'author', 'commonmark', 'visibility',)

admin.site.register(CitrusAuthor, CitrusAuthorAdmin)
admin.site.register(Post, CitrusPostAdmin)
