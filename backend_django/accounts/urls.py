from django.urls import path

from .views import UserLoginView, UserLogoutView, dashboard_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("login", UserLoginView.as_view(), name="login"),
    path("logout", UserLogoutView.as_view(), name="logout"),
]
