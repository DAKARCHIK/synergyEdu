from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .roles import ADMIN, STUDENT, TEACHER, first_role


class UserLoginView(LoginView):
    template_name = "login.html"


class UserLogoutView(LogoutView):
    pass


@login_required
def dashboard_view(request):
    role = first_role(request.user)
    if role == ADMIN:
        return redirect("/admin/")
    if role == TEACHER:
        return redirect("/teacher/assignments")
    if role == STUDENT:
        return redirect("/student/schedule")
    return render(request, "dashboard.html", {"role": role})
