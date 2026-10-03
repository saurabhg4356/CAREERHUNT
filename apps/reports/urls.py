"""
URL configuration for apps.reports.
"""
from django.urls import path
from .views import submit_report_view, resolve_report_view

app_name = "reports"

urlpatterns = [
    path("submit/<int:job_id>/", submit_report_view, name="submit_report"),
    path("<int:pk>/resolve/", resolve_report_view, name="resolve_report"),
]
