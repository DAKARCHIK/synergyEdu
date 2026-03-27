from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from announcements.models import Announcement
from assignments.models import Assignment
from education.models import Course, Group as StudyGroup
from schedule.models import Lesson
from .decorators import role_required
from .forms import StudentRegistrationForm, TeacherRegistrationRequestForm
from .models import TeacherRegistrationRequest
from .roles import ADMIN, STUDENT, TEACHER, first_role


class UserLoginView(LoginView):
    template_name = "login.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_sidebar"] = True
        return context


class UserLogoutView(LogoutView):
    pass


def home_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "welcome.html", {"hide_sidebar": True})


def student_register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = StudentRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        student_group, _ = Group.objects.get_or_create(name=STUDENT)
        user.groups.add(student_group)
        login(request, user)
        messages.success(request, "Аккаунт студента успешно создан.")
        return redirect("dashboard")

    return render(request, "register_student.html", {"form": form, "hide_sidebar": True})


def teacher_request_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = TeacherRegistrationRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Заявка отправлена. После проверки администратором вы получите доступ.")
        return redirect("login")

    return render(request, "register_teacher.html", {"form": form, "hide_sidebar": True})


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
            {
                "label": "Заявки преподавателей",
                "url": "/admin-dashboard/teacher-requests",
                "icon": "bi-person-workspace",
            },
        ]
        context["stats"] = {
            "groups_count": StudyGroup.objects.count(),
            "courses_count": Course.objects.count(),
            "users_count": user_model.objects.count(),
        }

    return render(request, "dashboard.html", context)


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    role = first_role(request.user)
    student_group = None
    teacher_courses = []

    if role == STUDENT:
        profile = getattr(request.user, "student_profile", None)
        student_group = getattr(profile, "group", None) if profile else None
    elif role == TEACHER:
        teacher_courses = Course.objects.filter(teacher=request.user).order_by("title")

    return render(
        request,
        "profile.html",
        {
            "role": role,
            "student_group": student_group,
            "teacher_courses": teacher_courses,
        },
    )


@role_required(ADMIN)
def teacher_requests_admin_view(request: HttpRequest) -> HttpResponse:
    status_filter = request.GET.get("status", "all")
    requests_qs = TeacherRegistrationRequest.objects.select_related("reviewed_by")
    if status_filter in {
        TeacherRegistrationRequest.STATUS_PENDING,
        TeacherRegistrationRequest.STATUS_APPROVED,
        TeacherRegistrationRequest.STATUS_REJECTED,
    }:
        requests_qs = requests_qs.filter(status=status_filter)

    return render(
        request,
        "admin_teacher_requests.html",
        {
            "requests": requests_qs,
            "status_filter": status_filter,
        },
    )


@role_required(ADMIN)
@transaction.atomic
def teacher_request_approve_view(request: HttpRequest, request_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("teacher_requests_admin")

    item = get_object_or_404(TeacherRegistrationRequest, id=request_id)
    if item.status != TeacherRegistrationRequest.STATUS_PENDING:
        messages.warning(request, "Эта заявка уже обработана.")
        return redirect("teacher_requests_admin")

    user_model = get_user_model()
    if user_model.objects.filter(username__iexact=item.username).exists():
        messages.error(request, "Невозможно одобрить: логин уже занят существующим пользователем.")
        return redirect("teacher_requests_admin")
    if user_model.objects.filter(email__iexact=item.email).exists():
        messages.error(request, "Невозможно одобрить: email уже занят существующим пользователем.")
        return redirect("teacher_requests_admin")

    parts = [part for part in item.full_name.split() if part]
    first_name = parts[0] if parts else ""
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    created_user = user_model.objects.create(
        username=item.username,
        email=item.email,
        first_name=first_name,
        last_name=last_name,
        password=item.password_hash,
    )
    teacher_group, _ = Group.objects.get_or_create(name=TEACHER)
    created_user.groups.add(teacher_group)

    item.status = TeacherRegistrationRequest.STATUS_APPROVED
    item.reviewed_by = request.user
    item.reviewed_at = timezone.now()
    item.save(update_fields=["status", "reviewed_by", "reviewed_at"])

    messages.success(request, f"Заявка одобрена. Пользователь {created_user.username} создан с ролью TEACHER.")
    return redirect("teacher_requests_admin")


@role_required(ADMIN)
def teacher_request_reject_view(request: HttpRequest, request_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("teacher_requests_admin")

    item = get_object_or_404(TeacherRegistrationRequest, id=request_id)
    if item.status != TeacherRegistrationRequest.STATUS_PENDING:
        messages.warning(request, "Эта заявка уже обработана.")
        return redirect("teacher_requests_admin")

    item.status = TeacherRegistrationRequest.STATUS_REJECTED
    item.reviewed_by = request.user
    item.reviewed_at = timezone.now()
    item.save(update_fields=["status", "reviewed_by", "reviewed_at"])

    messages.info(request, "Заявка отклонена.")
    return redirect("teacher_requests_admin")
