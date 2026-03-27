from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        verbose_name="Студент",
    )
    group = models.ForeignKey(
        "education.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profiles",
        verbose_name="Группа",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Профиль студента"
        verbose_name_plural = "Профили студентов"

    def __str__(self) -> str:
        return f"{self.user.username} ({self.group or 'без группы'})"


class TeacherRegistrationRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Ожидает"),
        (STATUS_APPROVED, "Одобрена"),
        (STATUS_REJECTED, "Отклонена"),
    )

    full_name = models.CharField("ФИО", max_length=255)
    username = models.CharField("Логин", max_length=150)
    email = models.EmailField("Email")
    password_hash = models.CharField("Хэш пароля", max_length=128)
    comment = models.TextField("Дисциплина / комментарий", blank=True)
    status = models.CharField("Статус", max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField("Дата заявки", auto_now_add=True)
    reviewed_at = models.DateTimeField("Дата рассмотрения", null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_teacher_requests",
        verbose_name="Проверил",
    )

    class Meta:
        verbose_name = "Заявка преподавателя"
        verbose_name_plural = "Заявки преподавателей"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.username}) - {self.status}"
