from django.urls import path

from .views import (
    UserLoginView,
    UserLogoutView,
    dashboard_view,
    home_view,
    profile_view,
    student_register_view,
    teacher_request_approve_view,
    teacher_request_reject_view,
    teacher_request_view,
    teacher_requests_admin_view,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("dashboard", dashboard_view, name="dashboard"),
    path("profile", profile_view, name="profile"),
    path("login", UserLoginView.as_view(), name="login"),
    path("logout", UserLogoutView.as_view(), name="logout"),
    path("register/student", student_register_view, name="register_student"),
    path("register/teacher", teacher_request_view, name="register_teacher"),
    path("admin-dashboard/teacher-requests", teacher_requests_admin_view, name="teacher_requests_admin"),
    path(
        "admin-dashboard/teacher-requests/<int:request_id>/approve",
        teacher_request_approve_view,
        name="teacher_request_approve",
    ),
    path(
        "admin-dashboard/teacher-requests/<int:request_id>/reject",
        teacher_request_reject_view,
        name="teacher_request_reject",
    ),
]
