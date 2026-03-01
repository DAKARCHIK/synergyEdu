from django.conf import settings
from django.db import models
from django.utils import timezone

from education.models import Course


class Assignment(models.Model):
    course = models.ForeignKey(Course, verbose_name="Дисциплина", on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    due_date = models.DateTimeField("Срок сдачи")

    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"
        ordering = ["due_date"]

    def __str__(self) -> str:
        return self.title


class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        verbose_name="Задание",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Студент",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    text = models.TextField("Текст ответа", blank=True)
    link = models.URLField("Ссылка", blank=True)
    submitted_at = models.DateTimeField("Дата сдачи", default=timezone.now)

    class Meta:
        verbose_name = "Сдача работы"
        verbose_name_plural = "Сдачи работ"
        constraints = [models.UniqueConstraint(fields=["assignment", "student"], name="unique_submission_per_student")]
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"{self.student} / {self.assignment}"


class Grade(models.Model):
    submission = models.OneToOneField(
        Submission,
        verbose_name="Сдача работы",
        on_delete=models.CASCADE,
        related_name="grade",
    )
    value = models.IntegerField("Оценка")
    comment = models.TextField("Комментарий", blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Проверил",
        on_delete=models.CASCADE,
        related_name="grades_given",
    )
    graded_at = models.DateTimeField("Дата выставления", default=timezone.now)

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        ordering = ["-graded_at"]

    def __str__(self) -> str:
        return f"{self.value} ({self.submission})"
