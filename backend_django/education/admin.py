from django.contrib import admin

from .models import Course, Enrollment, Group


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    autocomplete_fields = ("student",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "teacher", "group")
    list_filter = ("teacher", "group")
    search_fields = ("title", "description", "teacher__username", "group__name")
    inlines = (EnrollmentInline,)
    autocomplete_fields = ("teacher", "group")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course")
    list_filter = ("course",)
    search_fields = ("student__username", "course__title")
    autocomplete_fields = ("student", "course")
