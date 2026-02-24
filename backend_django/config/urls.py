from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("schedule.urls")),
    path("", include("assignments.urls")),
    path("", include("announcements.urls")),
]
