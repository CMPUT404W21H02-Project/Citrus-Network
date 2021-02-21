from django.contrib import admin
from .models import CitrusAuthor


class CitrusAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'user', 'host', 'displayName', 'github',)

admin.site.register(CitrusAuthor, CitrusAuthorAdmin)
