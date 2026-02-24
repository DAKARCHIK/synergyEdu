from django.contrib import admin

from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "weekday", "start_time", "end_time", "course", "group", "teacher", "room")
    list_filter = ("weekday", "group", "course", "teacher")
    search_fields = ("course__title", "group__name", "teacher__username", "room")
    autocomplete_fields = ("group", "course", "teacher")
