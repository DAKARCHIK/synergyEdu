from django.contrib.auth.models import Group

ADMIN = "ADMIN"
TEACHER = "TEACHER"
STUDENT = "STUDENT"
ROLE_CHOICES = [ADMIN, TEACHER, STUDENT]


def has_role(user, role: str) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser and role == ADMIN:
        return True
    return user.groups.filter(name=role).exists()


def first_role(user) -> str | None:
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return ADMIN
    role_group = Group.objects.filter(user=user, name__in=ROLE_CHOICES).first()
    return role_group.name if role_group else None
