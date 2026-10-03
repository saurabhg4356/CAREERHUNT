"""
URL configuration for apps.notifications.
"""
from django.urls import path
from .views import (
    notification_list_view,
    mark_read_view,
    job_alerts_view,
    delete_alert_view,
)

app_name = "notifications"

urlpatterns = [
    path("", notification_list_view, name="list"),
    path("<int:pk>/read/", mark_read_view, name="mark_read"),
    path("alerts/", job_alerts_view, name="alerts"),
    path("alerts/<int:pk>/delete/", delete_alert_view, name="delete_alert"),
]
