from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as AuthGroup
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.roles import STUDENT, TEACHER
from education.models import Course, Enrollment, Group as EducationGroup

from .models import Assignment, Grade, Submission


class SubmissionValidationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.student = user_model.objects.create_user(username="student_1", password="pass12345")
        student_role = AuthGroup.objects.create(name=STUDENT)
        self.student.groups.add(student_role)

        teacher = user_model.objects.create_user(username="teacher_1", password="pass12345")
        teacher_role = AuthGroup.objects.create(name=TEACHER)
        teacher.groups.add(teacher_role)

        group = EducationGroup.objects.create(name="ST-101")
        course = Course.objects.create(title="Math", teacher=teacher, group=group)
        Enrollment.objects.create(student=self.student, course=course)
        self.assignment = Assignment.objects.create(
            course=course,
            title="Homework",
            description="",
            due_date=timezone.now() + timedelta(days=1),
        )

    def test_student_cannot_submit_empty_submission_via_main_endpoint(self):
        self.client.login(username="student_1", password="pass12345")
        response = self.client.post(
            reverse("student_submission_save", kwargs={"assignment_id": self.assignment.id}),
            {"text": "", "link": ""},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Submission.objects.filter(assignment=self.assignment, student=self.student).exists())

class GradeValidationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.teacher = user_model.objects.create_user(username="teacher_1", password="pass12345")
        teacher_role = AuthGroup.objects.create(name=TEACHER)
        self.teacher.groups.add(teacher_role)

        self.student = user_model.objects.create_user(username="student_1", password="pass12345")
        student_role = AuthGroup.objects.create(name=STUDENT)
        self.student.groups.add(student_role)

        group = EducationGroup.objects.create(name="ST-101")
        course = Course.objects.create(title="Math", teacher=self.teacher, group=group)
        self.assignment = Assignment.objects.create(
            course=course,
            title="Homework",
            description="",
            due_date=timezone.now() + timedelta(days=1),
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            text="solution",
            submitted_at=timezone.now(),
        )

    def test_modal_grade_save_rejects_value_over_100(self):
        self.client.login(username="teacher_1", password="pass12345")
        response = self.client.post(
            reverse("teacher_grade_save", kwargs={"submission_id": self.submission.id}),
            {"value": "101", "comment": "too high"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "value")
        self.assertFalse(Grade.objects.filter(submission=self.submission).exists())

    def test_modal_grade_save_rejects_non_integer_value(self):
        self.client.login(username="teacher_1", password="pass12345")
        response = self.client.post(
            reverse("teacher_grade_save", kwargs={"submission_id": self.submission.id}),
            {"value": "abc", "comment": "bad type"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "value")
        self.assertFalse(Grade.objects.filter(submission=self.submission).exists())

    def test_modal_grade_save_rejects_negative_value(self):
        self.client.login(username="teacher_1", password="pass12345")
        response = self.client.post(
            reverse("teacher_grade_save", kwargs={"submission_id": self.submission.id}),
            {"value": "-1", "comment": "negative"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "value")
        self.assertFalse(Grade.objects.filter(submission=self.submission).exists())
