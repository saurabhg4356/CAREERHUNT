"""
URL configuration for apps.applications.
"""
from django.urls import path
from .views import (
    application_dashboard,
    track_job_view,
    update_application_view,
    delete_application_view,
)

app_name = "applications"

urlpatterns = [
    path("", application_dashboard, name="dashboard"),
    path("track/<int:job_id>/", track_job_view, name="track_job"),
    path("<int:pk>/update/", update_application_view, name="update_application"),
    path("<int:pk>/delete/", delete_application_view, name="delete_application"),
]
