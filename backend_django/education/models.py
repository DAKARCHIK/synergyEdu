from django.conf import settings
from django.db import models


class Group(models.Model):
    name = models.CharField("Название", max_length=120, unique=True)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self) -> str:
        return self.name


class Course(models.Model):
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Преподаватель",
        on_delete=models.CASCADE,
        related_name="courses_taught",
    )
    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

    def __str__(self) -> str:
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Студент",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(Course, verbose_name="Дисциплина", on_delete=models.CASCADE, related_name="enrollments")

    class Meta:
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курс"
        constraints = [models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_enrollment")]

    def __str__(self) -> str:
        return f"{self.student} -> {self.course}"
