from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.roles import STUDENT
from education.models import Group
from .models import Lesson


@login_required
@role_required(STUDENT)
def student_schedule_view(request):
    student_group = None
    profile = getattr(request.user, "student_profile", None)
    if profile and getattr(profile, "group_id", None):
        student_group = profile.group
    else:
        student_group = Group.objects.filter(courses__enrollments__student=request.user).distinct().first()

    weekday_names = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье",
    }

    context = {
        "group_missing": student_group is None,
        "schedule_days": [],
        "schedule_rows": [],
        "today_weekday": timezone.localdate().weekday(),
        "today_label": weekday_names[timezone.localdate().weekday()],
    }

    if student_group is None:
        return render(request, "student_schedule.html", context)

    lessons = (
        Lesson.objects.filter(group=student_group)
        .select_related("course", "group", "teacher")
        .order_by("start_time", "end_time", "weekday")
    )

    has_saturday = lessons.filter(weekday=5).exists()
    day_indexes = [0, 1, 2, 3, 4] + ([5] if has_saturday else [])
    schedule_days = [{"index": idx, "label": weekday_names[idx]} for idx in day_indexes]

    time_slots = sorted({(lesson.start_time, lesson.end_time) for lesson in lessons}, key=lambda item: (item[0], item[1]))
    lesson_map = {(lesson.weekday, lesson.start_time, lesson.end_time): lesson for lesson in lessons}

    schedule_rows = []
    for start_time, end_time in time_slots:
        row = {
            "time_label": f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
            "cells": [],
        }
        for day_idx in day_indexes:
            row["cells"].append(
                {
                    "day_index": day_idx,
                    "lesson": lesson_map.get((day_idx, start_time, end_time)),
                }
            )
        schedule_rows.append(row)

    context.update(
        {
            "group": student_group,
            "schedule_days": schedule_days,
            "schedule_rows": schedule_rows,
        }
    )
    return render(request, "student_schedule.html", context)
