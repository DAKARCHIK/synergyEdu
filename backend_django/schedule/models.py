from django.conf import settings
from django.db import models

from education.models import Course, Group


class Lesson(models.Model):
    WEEKDAYS = [
        (0, "Понедельник"),
        (1, "Вторник"),
        (2, "Среда"),
        (3, "Четверг"),
        (4, "Пятница"),
        (5, "Суббота"),
        (6, "Воскресенье"),
    ]

    group = models.ForeignKey(Group, verbose_name="Группа", on_delete=models.CASCADE, related_name="lessons")
    course = models.ForeignKey(Course, verbose_name="Дисциплина", on_delete=models.CASCADE, related_name="lessons")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Преподаватель",
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    weekday = models.IntegerField("День недели", choices=WEEKDAYS)
    start_time = models.TimeField("Время начала")
    end_time = models.TimeField("Время окончания")
    room = models.CharField("Аудитория", max_length=120)

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
        ordering = ["weekday", "start_time"]

    def __str__(self) -> str:
        return f"{self.get_weekday_display()} {self.course} {self.start_time}-{self.end_time}"
