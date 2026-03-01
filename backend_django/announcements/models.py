from django.conf import settings
from django.db import models

from education.models import Group


class Announcement(models.Model):
    group = models.ForeignKey(Group, verbose_name="Группа", on_delete=models.CASCADE, related_name="announcements")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="announcements",
    )
    title = models.CharField("Заголовок", max_length=255)
    body = models.TextField("Текст объявления")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
