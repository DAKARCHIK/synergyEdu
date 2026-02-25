from .roles import ADMIN, STUDENT, TEACHER, first_role, has_role


def role_flags(request):
    user = request.user
    return {
        "is_admin": has_role(user, ADMIN),
        "is_teacher": has_role(user, TEACHER),
        "is_student": has_role(user, STUDENT),
        "current_role": first_role(user),
    }
