from django.contrib import admin
from .models import CitrusAuthor


class CitrusAuthorAdmin(admin.ModelAdmin):
    list_display = ('author_id', 'user_type', 'user', 'host', 'display_name', 'github',)

admin.site.register(CitrusAuthor, CitrusAuthorAdmin)
