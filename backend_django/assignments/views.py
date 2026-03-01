from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.roles import STUDENT, TEACHER
from education.models import Course
from .forms import SubmissionForm
from .models import Assignment, Grade, Submission


def _build_assignment_card(assignment, submission):
    # Памятка: единое место расчета статуса карточки задания
    today = timezone.localdate()
    is_graded = bool(submission and hasattr(submission, "grade"))

    if is_graded:
        status_label = "Оценено"
        status_badge = "success"
    elif submission:
        status_label = "Сдано"
        status_badge = "warning"
    elif timezone.localtime(assignment.due_date).date() <= today:
        status_label = "Просрочено"
        status_badge = "danger"
    else:
        status_label = "Не сдано"
        status_badge = "secondary"

    return {
        "assignment": assignment,
        "submission": submission,
        "status_label": status_label,
        "status_badge": status_badge,
        "is_graded": is_graded,
        "can_submit": submission is None,
        "can_edit": submission is not None and not is_graded,
    }


def _build_submission_row(submission):
    # Памятка: единое место расчета статуса строки сдачи для преподавателя
    is_graded = hasattr(submission, "grade")
    return {
        "submission": submission,
        "status_label": "Оценено" if is_graded else "На проверке",
        "status_badge": "success" if is_graded else "warning",
        "grade_value": submission.grade.value if is_graded else None,
    }


@login_required
@role_required(STUDENT)
def student_assignments_view(request):
    assignments = (
        Assignment.objects.filter(course__enrollments__student=request.user)
        .select_related("course")
        .distinct()
    )
    submissions = Submission.objects.filter(student=request.user, assignment__in=assignments).select_related("grade")
    submissions_map = {submission.assignment_id: submission for submission in submissions}
    assignment_cards = [_build_assignment_card(assignment, submissions_map.get(assignment.id)) for assignment in assignments]
    return render(request, "student_assignments.html", {"assignment_cards": assignment_cards})


@login_required
@role_required(STUDENT)
def student_submission_modal_view(request, assignment_id: int):
    # Памятка: модалка доступна только студенту, записанному на курс задания
    assignment = get_object_or_404(Assignment, id=assignment_id, course__enrollments__student=request.user)
    submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    form = SubmissionForm(
        initial={
            "text": submission.text if submission else "",
            "link": submission.link if submission else "",
        }
    )
    return render(
        request,
        "partials/modal_submission_form.html",
        {
            "assignment": assignment,
            "submission": submission,
            "form": form,
        },
    )


@login_required
@role_required(STUDENT)
def student_submission_save_view(request, assignment_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    assignment = get_object_or_404(Assignment, id=assignment_id, course__enrollments__student=request.user)
    # Памятка: при редактировании подтягиваем текущую сдачу, чтобы показать форму с данными
    existing_submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    form = SubmissionForm(request.POST)

    # Памятка: валидация формы запрещает "пустую сдачу" (и text, и link пустые)
    if not form.is_valid():
        return render(
            request,
            "partials/modal_submission_form.html",
            {
                "assignment": assignment,
                "submission": existing_submission,
                "form": form,
            },
        )

    text = form.cleaned_data["text"]
    link = form.cleaned_data["link"]
    submission, _ = Submission.objects.update_or_create(
        assignment=assignment,
        student=request.user,
        defaults={"text": text, "link": link, "submitted_at": timezone.now()},
    )
    card = _build_assignment_card(assignment, submission)

    # Памятка: запасной вариант, если HTMX отключен
    if not request.htmx:
        return redirect("student_assignments")

    response = render(request, "partials/assignment_card.html", {"card": card})
    response["HX-Trigger"] = "closeModal"
    return response


@login_required
@role_required(STUDENT)
def submit_assignment_view(request, assignment_id: int):
    if request.method != "POST" or not request.htmx:
        return HttpResponseBadRequest("HTMX POST only")

    assignment = get_object_or_404(Assignment, id=assignment_id, course__enrollments__student=request.user)
    text = request.POST.get("text", "").strip()
    link = request.POST.get("link", "").strip()
    submission, _ = Submission.objects.update_or_create(
        assignment=assignment,
        student=request.user,
        defaults={"text": text, "link": link, "submitted_at": timezone.now()},
    )
    return render(request, "partials/submission_result.html", {"submission": submission, "assignment": assignment})


@login_required
@role_required(STUDENT)
def student_grades_view(request):
    grades = Grade.objects.filter(submission__student=request.user).select_related(
        "submission", "submission__assignment", "submission__assignment__course", "graded_by"
    )
    return render(request, "student_grades.html", {"grades": grades})


@login_required
@role_required(TEACHER)
def teacher_assignments_view(request):
    courses = Course.objects.filter(teacher=request.user).order_by("title")
    selected_course = request.GET.get("course")
    assignments = Assignment.objects.filter(course__teacher=request.user).select_related("course")
    if selected_course:
        assignments = assignments.filter(course_id=selected_course)
    context = {"assignments": assignments, "courses": courses, "selected_course": selected_course}
    if request.htmx:
        return render(request, "partials/teacher_assignments_list.html", context)
    return render(request, "teacher_assignments.html", context)


@login_required
@role_required(TEACHER)
def teacher_submissions_view(request, assignment_id: int):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__teacher=request.user)
    submissions = Submission.objects.filter(assignment=assignment).select_related("student", "assignment", "grade")
    submission_rows = [_build_submission_row(submission) for submission in submissions]
    return render(
        request,
        "teacher_submissions.html",
        {"assignment": assignment, "submission_rows": submission_rows},
    )


@login_required
@role_required(TEACHER)
def teacher_grade_modal_view(request, submission_id: int):
    # Памятка: преподаватель видит только сдачи своих курсов
    submission = get_object_or_404(Submission, id=submission_id, assignment__course__teacher=request.user)
    grade = getattr(submission, "grade", None)
    return render(
        request,
        "partials/modal_grade_form.html",
        {
            "submission": submission,
            "grade": grade,
            "errors": {},
            "value": grade.value if grade else "",
            "comment": grade.comment if grade else "",
        },
    )


@login_required
@role_required(TEACHER)
def teacher_grade_save_view(request, submission_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    submission = get_object_or_404(Submission, id=submission_id, assignment__course__teacher=request.user)
    raw_value = request.POST.get("value", "").strip()
    comment = request.POST.get("comment", "").strip()
    errors = {}

    try:
        value = int(raw_value)
    except ValueError:
        errors["value"] = "Оценка должна быть целым числом."
        value = None

    if value is not None and (value < 0 or value > 100):
        errors["value"] = "Оценка должна быть в диапазоне 0..100."

    # Памятка: возвращаем ту же модалку с ошибками, если ввод невалидный
    if errors:
        return render(
            request,
            "partials/modal_grade_form.html",
            {
                "submission": submission,
                "grade": getattr(submission, "grade", None),
                "errors": errors,
                "value": raw_value,
                "comment": comment,
            },
        )

    Grade.objects.update_or_create(
        submission=submission,
        defaults={"value": value, "comment": comment, "graded_by": request.user, "graded_at": timezone.now()},
    )
    submission = Submission.objects.select_related("student", "assignment", "grade").get(id=submission.id)
    row = _build_submission_row(submission)

    # Памятка: запасной вариант, если HTMX отключен
    if not request.htmx:
        return redirect("teacher_submissions", assignment_id=submission.assignment_id)

    response = render(request, "partials/submission_row.html", {"row": row, "assignment": submission.assignment})
    response["HX-Trigger"] = "closeModal"
    return response


@login_required
@role_required(TEACHER)
def teacher_grade_view(request, submission_id: int):
    if request.method != "POST" or not request.htmx:
        return HttpResponseBadRequest("HTMX POST only")

    submission = get_object_or_404(Submission, id=submission_id, assignment__course__teacher=request.user)
    try:
        value = int(request.POST.get("value", "0"))
    except ValueError:
        return HttpResponseBadRequest("Value must be integer")
    comment = request.POST.get("comment", "").strip()
    grade, _ = Grade.objects.update_or_create(
        submission=submission,
        defaults={"value": value, "comment": comment, "graded_by": request.user, "graded_at": timezone.now()},
    )
    return render(request, "partials/grade_result.html", {"grade": grade, "submission": submission})
