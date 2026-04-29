from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.roles import STUDENT, TEACHER
from education.models import Course

from .forms import AssignmentTeacherForm, GradeForm, SubmissionForm
from .models import Assignment, Grade, Submission


def _build_assignment_card(assignment, submission):
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
    is_graded = hasattr(submission, "grade")
    return {
        "submission": submission,
        "status_label": "Оценено" if is_graded else "На проверке",
        "status_badge": "success" if is_graded else "warning",
        "grade_value": submission.grade.value if is_graded else None,
    }


def _teacher_assignments_context(user, selected_course):
    courses = Course.objects.filter(teacher=user).order_by("title")
    assignments = Assignment.objects.filter(course__teacher=user).select_related("course")
    if selected_course:
        assignments = assignments.filter(course_id=selected_course)

    return {
        "assignments": assignments,
        "courses": courses,
        "selected_course": selected_course,
    }


@login_required
@role_required(STUDENT)
def student_assignments_view(request):
    assignments = Assignment.objects.filter(course__enrollments__student=request.user).select_related("course").distinct()
    submissions = Submission.objects.filter(student=request.user, assignment__in=assignments).select_related("grade")
    submissions_map = {submission.assignment_id: submission for submission in submissions}
    assignment_cards = [_build_assignment_card(assignment, submissions_map.get(assignment.id)) for assignment in assignments]
    return render(request, "student_assignments.html", {"assignment_cards": assignment_cards})


@login_required
@role_required(STUDENT)
def student_submission_modal_view(request, assignment_id: int):
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
    existing_submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    form = SubmissionForm(request.POST)

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

    if not request.htmx:
        return redirect("student_assignments")

    response = render(request, "partials/assignment_card.html", {"card": card})
    response["HX-Trigger"] = "closeModal"
    return response


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
    selected_course = request.GET.get("course")
    context = _teacher_assignments_context(request.user, selected_course)
    if request.htmx:
        return render(request, "partials/teacher_assignments_list.html", context)
    return render(request, "teacher_assignments.html", context)


@login_required
@role_required(TEACHER)
def teacher_assignment_create_modal_view(request):
    selected_course = request.GET.get("course")
    initial = {"course": selected_course} if selected_course else {}
    form = AssignmentTeacherForm(teacher=request.user, initial=initial)
    return render(
        request,
        "partials/modal_assignment_form.html",
        {
            "form": form,
            "is_edit": False,
            "assignment": None,
            "selected_course": selected_course,
        },
    )


@login_required
@role_required(TEACHER)
def teacher_assignment_create_save_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    selected_course = request.POST.get("selected_course")
    form = AssignmentTeacherForm(request.POST, teacher=request.user)
    if not form.is_valid():
        return render(
            request,
            "partials/modal_assignment_form.html",
            {
                "form": form,
                "is_edit": False,
                "assignment": None,
                "selected_course": selected_course,
            },
        )

    form.save()
    if not request.htmx:
        messages.success(request, "Задание создано.")
        return redirect("teacher_assignments")

    context = _teacher_assignments_context(request.user, selected_course)
    response = render(request, "partials/teacher_assignments_list.html", context)
    response["HX-Retarget"] = "#teacher-assignment-list"
    response["HX-Trigger"] = "closeModal"
    return response


@login_required
@role_required(TEACHER)
def teacher_assignment_edit_modal_view(request, assignment_id: int):
    selected_course = request.GET.get("course")
    assignment = get_object_or_404(Assignment, id=assignment_id, course__teacher=request.user)
    form = AssignmentTeacherForm(instance=assignment, teacher=request.user)
    return render(
        request,
        "partials/modal_assignment_form.html",
        {
            "form": form,
            "is_edit": True,
            "assignment": assignment,
            "selected_course": selected_course,
        },
    )


@login_required
@role_required(TEACHER)
def teacher_assignment_edit_save_view(request, assignment_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    selected_course = request.POST.get("selected_course")
    assignment = get_object_or_404(Assignment, id=assignment_id, course__teacher=request.user)
    form = AssignmentTeacherForm(request.POST, instance=assignment, teacher=request.user)
    if not form.is_valid():
        return render(
            request,
            "partials/modal_assignment_form.html",
            {
                "form": form,
                "is_edit": True,
                "assignment": assignment,
                "selected_course": selected_course,
            },
        )

    form.save()
    if not request.htmx:
        messages.success(request, "Задание обновлено.")
        return redirect("teacher_assignments")

    context = _teacher_assignments_context(request.user, selected_course)
    response = render(request, "partials/teacher_assignments_list.html", context)
    response["HX-Retarget"] = "#teacher-assignment-list"
    response["HX-Trigger"] = "closeModal"
    return response


@login_required
@role_required(TEACHER)
def teacher_assignment_delete_view(request, assignment_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    selected_course = request.POST.get("selected_course")
    assignment = get_object_or_404(Assignment, id=assignment_id, course__teacher=request.user)
    assignment.delete()

    if not request.htmx:
        messages.success(request, "Задание удалено.")
        return redirect("teacher_assignments")

    context = _teacher_assignments_context(request.user, selected_course)
    return render(request, "partials/teacher_assignments_list.html", context)


@login_required
@role_required(TEACHER)
def teacher_all_submissions_view(request):
    submissions = (
        Submission.objects
        .filter(assignment__course__teacher=request.user)
        .select_related("student", "assignment", "assignment__course", "grade")
        .order_by("assignment__due_date", "-submitted_at")
    )
    submission_rows = [_build_submission_row(s) for s in submissions]
    return render(request, "teacher_all_submissions.html", {"submission_rows": submission_rows})


@login_required
@role_required(TEACHER)
def teacher_submissions_view(request, assignment_id: int):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__teacher=request.user)
    submissions = Submission.objects.filter(assignment=assignment).select_related("student", "assignment", "grade")
    submission_rows = [_build_submission_row(submission) for submission in submissions]
    return render(request, "teacher_submissions.html", {"assignment": assignment, "submission_rows": submission_rows})


@login_required
@role_required(TEACHER)
def teacher_grade_modal_view(request, submission_id: int):
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
    form = GradeForm(request.POST)
    if not form.is_valid():
        value_errors = form.errors.get("value")
        return render(
            request,
            "partials/modal_grade_form.html",
            {
                "submission": submission,
                "grade": getattr(submission, "grade", None),
                "errors": {"value": value_errors[0]} if value_errors else {},
                "value": request.POST.get("value", "").strip(),
                "comment": request.POST.get("comment", "").strip(),
            },
        )

    value = form.cleaned_data["value"]
    comment = form.cleaned_data["comment"]

    Grade.objects.update_or_create(
        submission=submission,
        defaults={"value": value, "comment": comment, "graded_by": request.user, "graded_at": timezone.now()},
    )
    submission = Submission.objects.select_related("student", "assignment", "grade").get(id=submission.id)
    row = _build_submission_row(submission)

    if not request.htmx:
        return redirect("teacher_submissions", assignment_id=submission.assignment_id)

    response = render(request, "partials/submission_row.html", {"row": row, "assignment": submission.assignment})
    response["HX-Trigger"] = "closeModal"
    return response

