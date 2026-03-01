from django.urls import path

from .views import (
    student_submission_modal_view,
    student_submission_save_view,
    student_assignments_view,
    student_grades_view,
    submit_assignment_view,
    teacher_assignments_view,
    teacher_grade_modal_view,
    teacher_grade_save_view,
    teacher_grade_view,
    teacher_submissions_view,
)

urlpatterns = [
    path("student/assignments", student_assignments_view, name="student_assignments"),
    path("student/assignments/<int:assignment_id>/submit", submit_assignment_view, name="submit_assignment"),
    path("student/submission/modal/<int:assignment_id>/", student_submission_modal_view, name="student_submission_modal"),
    path("student/submission/save/<int:assignment_id>/", student_submission_save_view, name="student_submission_save"),
    path("student/grades", student_grades_view, name="student_grades"),
    path("teacher/assignments", teacher_assignments_view, name="teacher_assignments"),
    path("teacher/submissions/<int:assignment_id>", teacher_submissions_view, name="teacher_submissions"),
    path("teacher/grade/<int:submission_id>", teacher_grade_view, name="teacher_grade"),
    path("teacher/grade/modal/<int:submission_id>/", teacher_grade_modal_view, name="teacher_grade_modal"),
    path("teacher/grade/save/<int:submission_id>/", teacher_grade_save_view, name="teacher_grade_save"),
]
