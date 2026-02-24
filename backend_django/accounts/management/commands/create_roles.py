from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from accounts.roles import ADMIN, STUDENT, TEACHER


class Command(BaseCommand):
    help = "Creates role groups and assigns baseline permissions."

    def handle(self, *args, **options):
        roles = {ADMIN: [], TEACHER: [], STUDENT: []}

        teacher_permissions = [
            "add_assignment",
            "change_assignment",
            "view_assignment",
            "view_submission",
            "add_grade",
            "change_grade",
            "view_grade",
            "add_announcement",
            "change_announcement",
            "view_announcement",
            "view_course",
            "view_enrollment",
            "view_lesson",
        ]
        student_permissions = [
            "view_assignment",
            "add_submission",
            "change_submission",
            "view_submission",
            "view_grade",
            "view_course",
            "view_enrollment",
            "view_lesson",
            "view_announcement",
        ]

        roles[TEACHER] = list(Permission.objects.filter(codename__in=teacher_permissions))
        roles[STUDENT] = list(Permission.objects.filter(codename__in=student_permissions))

        for role_name, perms in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if role_name == ADMIN:
                group.permissions.set(Permission.objects.all())
            else:
                group.permissions.set(perms)
            status = "created" if created else "updated"
            self.stdout.write(self.style.SUCCESS(f"{role_name}: {status}"))
