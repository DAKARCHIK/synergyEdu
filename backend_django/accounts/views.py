from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.utils import timezone

from announcements.models import Announcement
from assignments.models import Assignment
from education.models import Course, Group
from schedule.models import Lesson
from .roles import ADMIN, STUDENT, TEACHER, first_role


class UserLoginView(LoginView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_sidebar"] = True
        return context


class UserLogoutView(LogoutView):
    pass


@login_required
def dashboard_view(request):
    role = first_role(request.user)
    now = timezone.now()
    today_weekday = timezone.localdate().weekday()

    context = {
        "role": role,
        "today_lessons": [],
        "upcoming_assignments": [],
        "latest_announcements": [],
        "quick_actions": [],
    }

    if role == STUDENT:
        context["today_lessons"] = (
            Lesson.objects.filter(course__enrollments__student=request.user, weekday=today_weekday)
            .select_related("course", "group", "teacher")
            .order_by("start_time")
            .distinct()[:5]
        )
        context["upcoming_assignments"] = (
            Assignment.objects.filter(course__enrollments__student=request.user, due_date__gte=now)
            .select_related("course")
            .order_by("due_date")
            .distinct()[:5]
        )
        context["latest_announcements"] = (
            Announcement.objects.filter(group__courses__enrollments__student=request.user)
            .select_related("group", "author")
            .distinct()[:3]
        )
        context["quick_actions"] = [
            {"label": "Перейти к заданиям", "url": "/student/assignments", "icon": "bi-journal-check"},
            {"label": "Открыть расписание", "url": "/student/schedule", "icon": "bi-calendar-week"},
        ]
    elif role == TEACHER:
        context["today_lessons"] = (
            Lesson.objects.filter(teacher=request.user, weekday=today_weekday)
            .select_related("course", "group")
            .order_by("start_time")
            .distinct()[:5]
        )
        context["upcoming_assignments"] = (
            Assignment.objects.filter(course__teacher=request.user, due_date__gte=now)
            .select_related("course")
            .order_by("due_date")
            .distinct()[:5]
        )
        context["latest_announcements"] = (
            Announcement.objects.filter(group__courses__teacher=request.user)
            .select_related("group", "author")
            .distinct()[:3]
        )
        context["quick_actions"] = [
            {"label": "Перейти к заданиям", "url": "/teacher/assignments", "icon": "bi-journal-text"},
            {"label": "Открыть объявления", "url": "/teacher/announcements", "icon": "bi-megaphone"},
        ]
    elif role == ADMIN:
        user_model = get_user_model()
        context["today_lessons"] = (
            Lesson.objects.filter(weekday=today_weekday).select_related("course", "group", "teacher").order_by("start_time")[:5]
        )
        context["upcoming_assignments"] = (
            Assignment.objects.select_related("course").filter(due_date__gte=now).order_by("due_date")[:5]
        )
        context["latest_announcements"] = Announcement.objects.select_related("group", "author")[:3]
        context["quick_actions"] = [
            {"label": "Открыть админ-панель", "url": "/admin", "icon": "bi-speedometer2"},
            {"label": "Управление пользователями", "url": "/admin/auth/user/", "icon": "bi-people"},
        ]
        context["stats"] = {
            "groups_count": Group.objects.count(),
            "courses_count": Course.objects.count(),
            "users_count": user_model.objects.count(),
        }

    return render(request, "dashboard.html", context)
