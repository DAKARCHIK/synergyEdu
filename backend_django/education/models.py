from django.conf import settings
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self) -> str:
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses_taught")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")

    def __str__(self) -> str:
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_enrollment")]

    def __str__(self) -> str:
        return f"{self.student} -> {self.course}"
