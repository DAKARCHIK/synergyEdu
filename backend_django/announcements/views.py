from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.roles import STUDENT, TEACHER
from education.models import Group
from .models import Announcement


@login_required
@role_required(STUDENT)
def student_announcements_view(request):
    announcements = Announcement.objects.filter(group__courses__enrollments__student=request.user).select_related(
        "group", "author"
    )
    return render(request, "student_announcements.html", {"announcements": announcements})


@login_required
@role_required(TEACHER)
def teacher_announcements_view(request):
    groups = Group.objects.filter(courses__teacher=request.user).distinct().order_by("name")
    if request.method == "POST":
        group_id = request.POST.get("group")
        title = request.POST.get("title", "").strip()
        body = request.POST.get("body", "").strip()
        if group_id and not groups.filter(id=group_id).exists():
            return HttpResponseForbidden("You cannot create announcements for this group.")
        if group_id and title and body:
            Announcement.objects.create(group_id=group_id, author=request.user, title=title, body=body)
            messages.success(request, "Объявление опубликовано.")
            return redirect("teacher_announcements")
        messages.error(request, "Заполните все поля формы.")

    announcements = Announcement.objects.filter(author=request.user).select_related("group").order_by("-created_at")
    return render(request, "teacher_announcements.html", {"groups": groups, "announcements": announcements})
