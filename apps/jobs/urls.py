"""
URL configuration for apps.jobs.
"""
from django.urls import path
from .views import JobListView, InternshipListView, UpcomingListView, JobDetailView

app_name = "jobs"

urlpatterns = [
    path("", JobListView.as_view(), name="job_list"),
    path("internships/", InternshipListView.as_view(), name="internship_list"),
    path("upcoming/", UpcomingListView.as_view(), name="upcoming_list"),
    path("<slug:slug>/", JobDetailView.as_view(), name="job_detail"),
]
