from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.roles import STUDENT, TEACHER
from education.models import Course
from .models import Assignment, Grade, Submission


@login_required
@role_required(STUDENT)
def student_assignments_view(request):
    assignments = (
        Assignment.objects.filter(course__enrollments__student=request.user)
        .select_related("course")
        .prefetch_related("submissions")
        .distinct()
    )
    submissions = Submission.objects.filter(student=request.user, assignment__in=assignments)
    submissions_map = {submission.assignment_id: submission for submission in submissions}
    return render(
        request,
        "student_assignments.html",
        {"assignments": assignments, "submissions_map": submissions_map},
    )


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
    submissions = Submission.objects.filter(assignment=assignment).select_related("student", "grade")
    return render(
        request,
        "teacher_submissions.html",
        {"assignment": assignment, "submissions": submissions},
    )


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
