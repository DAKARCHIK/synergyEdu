from django.urls import path

from .views import student_announcements_view, teacher_announcements_view

urlpatterns = [
    path("student/announcements", student_announcements_view, name="student_announcements"),
    path("teacher/announcements", teacher_announcements_view, name="teacher_announcements"),
]
