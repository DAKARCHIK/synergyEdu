from django.conf import settings
from django.db import models

from education.models import Group


class Announcement(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="announcements")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
