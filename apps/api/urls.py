"""
URL configuration for CareerHunt REST API v1.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    JobViewSet,
    CompanyViewSet,
    JobSourceViewSet,
    CategoryViewSet,
    SkillViewSet,
    SavedJobViewSet,
    ApplicationViewSet,
    JobAlertViewSet,
    ReportViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register(r"jobs", JobViewSet, basename="job")
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"sources", JobSourceViewSet, basename="source")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"skills", SkillViewSet, basename="skill")
router.register(r"saved-jobs", SavedJobViewSet, basename="saved-job")
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"alerts", JobAlertViewSet, basename="alert")
router.register(r"reports", ReportViewSet, basename="report")

urlpatterns = [
    path("", include(router.urls)),
]
