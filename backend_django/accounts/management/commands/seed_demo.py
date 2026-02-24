from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.roles import ADMIN, STUDENT, TEACHER
from announcements.models import Announcement
from assignments.models import Assignment
from education.models import Course, Enrollment, Group as EduGroup
from schedule.models import Lesson


class Command(BaseCommand):
    help = "Seeds demo users and data."

    def handle(self, *args, **options):
        call_command("create_roles")
        User = get_user_model()

        admin, _ = User.objects.get_or_create(username="admin", defaults={"is_staff": True, "is_superuser": True})
        admin.set_password("Admin123!")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        teacher, _ = User.objects.get_or_create(username="teacher1", defaults={"is_staff": True})
        teacher.set_password("Teacher123!")
        teacher.is_staff = True
        teacher.save()

        student, _ = User.objects.get_or_create(username="student1")
        student.set_password("Student123!")
        student.save()

        Group.objects.get(name=ADMIN).user_set.add(admin)
        Group.objects.get(name=TEACHER).user_set.add(teacher)
        Group.objects.get(name=STUDENT).user_set.add(student)

        edu_group, _ = EduGroup.objects.get_or_create(name="ИС-22")
        course, _ = Course.objects.get_or_create(
            title="Web-разработка",
            defaults={"description": "Базовый курс по веб-разработке", "teacher": teacher, "group": edu_group},
        )
        if course.teacher_id != teacher.id or course.group_id != edu_group.id:
            course.teacher = teacher
            course.group = edu_group
            course.save(update_fields=["teacher", "group"])

        Enrollment.objects.get_or_create(student=student, course=course)

        lessons = [
            (0, time(9, 0), time(10, 30), "А-101"),
            (2, time(11, 0), time(12, 30), "А-103"),
            (4, time(10, 0), time(11, 30), "Лаб-2"),
        ]
        for weekday, start_time, end_time, room in lessons:
            Lesson.objects.get_or_create(
                group=edu_group,
                course=course,
                teacher=teacher,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
                room=room,
            )

        Assignment.objects.get_or_create(
            course=course,
            title="Домашняя работа №1",
            defaults={
                "description": "Сверстать страницу профиля студента и подключить форму отправки.",
                "due_date": timezone.now() + timedelta(days=7),
            },
        )

        Announcement.objects.get_or_create(
            group=edu_group,
            author=teacher,
            title="Старт курса",
            defaults={"body": "Добро пожаловать на курс Web-разработка. Проверьте расписание и дедлайны."},
        )

        self.stdout.write(self.style.SUCCESS("Demo data has been seeded."))
