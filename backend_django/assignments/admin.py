from django.contrib import admin

from .models import Assignment, Grade, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "due_date")
    list_filter = ("course", "due_date")
    search_fields = ("title", "description", "course__title")
    autocomplete_fields = ("course",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "assignment", "student", "submitted_at", "has_grade")
    list_filter = ("assignment__course", "assignment", "submitted_at")
    search_fields = ("assignment__title", "assignment__course__title", "student__username", "text", "link")
    autocomplete_fields = ("assignment", "student")

    @admin.display(boolean=True, description="Graded")
    def has_grade(self, obj):
        return hasattr(obj, "grade")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("id", "submission", "value", "graded_by", "graded_at")
    list_filter = ("value", "graded_at", "graded_by")
    search_fields = ("submission__student__username", "submission__assignment__title", "comment")
    autocomplete_fields = ("submission", "graded_by")
