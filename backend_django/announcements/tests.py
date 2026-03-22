from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as AuthGroup
from django.test import TestCase
from django.urls import reverse

from accounts.roles import TEACHER
from education.models import Course, Group as EducationGroup

from .models import Announcement


class TeacherAnnouncementsSecurityTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.teacher = user_model.objects.create_user(username="teacher_1", password="pass12345")
        teacher_role = AuthGroup.objects.create(name=TEACHER)
        self.teacher.groups.add(teacher_role)

        self.other_teacher = user_model.objects.create_user(username="teacher_2", password="pass12345")
        self.other_teacher.groups.add(teacher_role)

        self.own_group = EducationGroup.objects.create(name="OWN-101")
        self.foreign_group = EducationGroup.objects.create(name="FOR-202")

        Course.objects.create(title="Own Course", teacher=self.teacher, group=self.own_group)
        Course.objects.create(title="Foreign Course", teacher=self.other_teacher, group=self.foreign_group)

        self.url = reverse("teacher_announcements")

    def test_teacher_cannot_create_announcement_for_foreign_group(self):
        self.client.login(username="teacher_1", password="pass12345")

        response = self.client.post(
            self.url,
            {
                "group": str(self.foreign_group.id),
                "title": "Unauthorized",
                "body": "Should not be created",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Announcement.objects.filter(
                author=self.teacher,
                group=self.foreign_group,
                title="Unauthorized",
            ).exists()
        )
