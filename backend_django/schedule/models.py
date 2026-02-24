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

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="lessons")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lessons")
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=120)

    class Meta:
        ordering = ["weekday", "start_time"]

    def __str__(self) -> str:
        return f"{self.get_weekday_display()} {self.course} {self.start_time}-{self.end_time}"
