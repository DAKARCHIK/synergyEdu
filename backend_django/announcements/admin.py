from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "group", "author", "created_at")
    list_filter = ("group", "author", "created_at")
    search_fields = ("title", "body", "group__name", "author__username")
    autocomplete_fields = ("group", "author")
