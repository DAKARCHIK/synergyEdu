from django.conf import settings
from django.db import models
from django.utils import timezone

from education.models import Course


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()

    class Meta:
        ordering = ["due_date"]

    def __str__(self) -> str:
        return self.title


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    text = models.TextField(blank=True)
    link = models.URLField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["assignment", "student"], name="unique_submission_per_student")]
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"{self.student} / {self.assignment}"


class Grade(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="grade")
    value = models.IntegerField()
    comment = models.TextField(blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grades_given")
    graded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-graded_at"]

    def __str__(self) -> str:
        return f"{self.value} ({self.submission})"
