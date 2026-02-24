from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.decorators import role_required
from accounts.roles import STUDENT
from .models import Lesson


@login_required
@role_required(STUDENT)
def student_schedule_view(request):
    lessons = (
        Lesson.objects.filter(course__enrollments__student=request.user)
        .select_related("course", "group", "teacher")
        .distinct()
    )
    return render(request, "student_schedule.html", {"lessons": lessons})
