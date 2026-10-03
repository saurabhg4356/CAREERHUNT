"""
URL configuration for apps.core.
"""
from django.urls import path
from .views import HomeView, health_check

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("health/", health_check, name="health_check"),
]
