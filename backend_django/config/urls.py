from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    # Памятка: healthcheck для мониторинга/балансировщика
    path("healthz", lambda request: HttpResponse("ok", content_type="text/plain"), name="healthz"),
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("schedule.urls")),
    path("", include("assignments.urls")),
    path("", include("announcements.urls")),
]
