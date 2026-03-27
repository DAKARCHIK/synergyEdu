from django.contrib import admin

from .models import StudentProfile, TeacherRegistrationRequest


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "created_at")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    list_select_related = ("user", "group")


@admin.register(TeacherRegistrationRequest)
class TeacherRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "username", "email", "status", "created_at", "reviewed_at", "reviewed_by")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "username", "email", "comment")
    readonly_fields = ("created_at", "reviewed_at", "reviewed_by")
