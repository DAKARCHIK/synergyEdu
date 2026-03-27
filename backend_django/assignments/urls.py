from django.urls import path

from .views import (
    student_submission_modal_view,
    student_submission_save_view,
    student_assignments_view,
    student_grades_view,
    teacher_assignment_create_modal_view,
    teacher_assignment_create_save_view,
    teacher_assignment_delete_view,
    teacher_assignment_edit_modal_view,
    teacher_assignment_edit_save_view,
    teacher_assignments_view,
    teacher_grade_modal_view,
    teacher_grade_save_view,
    teacher_submissions_view,
)

urlpatterns = [
    path("student/assignments", student_assignments_view, name="student_assignments"),
    path("student/submission/modal/<int:assignment_id>/", student_submission_modal_view, name="student_submission_modal"),
    path("student/submission/save/<int:assignment_id>/", student_submission_save_view, name="student_submission_save"),
    path("student/grades", student_grades_view, name="student_grades"),
    path("teacher/assignments", teacher_assignments_view, name="teacher_assignments"),
    path("teacher/assignments/create/modal/", teacher_assignment_create_modal_view, name="teacher_assignment_create_modal"),
    path("teacher/assignments/create/save/", teacher_assignment_create_save_view, name="teacher_assignment_create_save"),
    path("teacher/assignments/<int:assignment_id>/edit/modal/", teacher_assignment_edit_modal_view, name="teacher_assignment_edit_modal"),
    path("teacher/assignments/<int:assignment_id>/edit/save/", teacher_assignment_edit_save_view, name="teacher_assignment_edit_save"),
    path("teacher/assignments/<int:assignment_id>/delete/", teacher_assignment_delete_view, name="teacher_assignment_delete"),
    path("teacher/submissions/<int:assignment_id>", teacher_submissions_view, name="teacher_submissions"),
    path("teacher/grade/modal/<int:submission_id>/", teacher_grade_modal_view, name="teacher_grade_modal"),
    path("teacher/grade/save/<int:submission_id>/", teacher_grade_save_view, name="teacher_grade_save"),
]
