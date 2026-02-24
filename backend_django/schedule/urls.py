from django.urls import path

from .views import student_schedule_view

urlpatterns = [
    path("student/schedule", student_schedule_view, name="student_schedule"),
]
