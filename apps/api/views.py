"""
REST API ViewSets for CareerHunt.
Provides secure, filterable, and paginated endpoints for jobs, companies, sources, applications.
"""
from django.db.models import Count
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.companies.models import Company
from apps.sources.models import JobSource
from apps.jobs.models import Category, Skill, Job, SavedJob
from apps.applications.models import Application
from apps.notifications.models import JobAlert
from apps.reports.models import Report

from .serializers import (
    CategorySerializer,
    SkillSerializer,
    CompanySerializer,
    JobSourceSerializer,
    JobSerializer,
    JobDetailSerializer,
    SavedJobSerializer,
    ApplicationSerializer,
    JobAlertSerializer,
    ReportSerializer,
)


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public opportunity listing and detail endpoint.
    Supports multi-facet filtering, full-text searching, and sorting.
    """
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        "opportunity_type",
        "experience_level",
        "remote_type",
        "status",
        "verification_status",
        "company__slug",
        "category__slug",
    ]
    search_fields = ["title", "description", "requirements", "company__name", "location_name", "skills__name"]
    ordering_fields = ["posted_at", "application_deadline", "salary_max", "title"]
    ordering = ["-posted_at"]

    def get_queryset(self):
        return (
            Job.objects.select_related("company", "source", "category")
            .prefetch_related("skills", "skills__category")
            .active()
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return JobDetailSerializer
        return JobSerializer

    @action(detail=False, methods=["get"])
    def closing_soon(self, request):
        """Returns opportunities closing within 3 days."""
        qs = Job.objects.select_related("company", "source", "category").prefetch_related("skills").closing_soon()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def internships(self, request):
        """Returns only internship opportunities."""
        qs = Job.objects.select_related("company", "source", "category").prefetch_related("skills").internships()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def freshers(self, request):
        """Returns opportunities geared for fresh graduates."""
        qs = Job.objects.select_related("company", "source", "category").prefetch_related("skills").freshers()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public directory of hiring employers and organizations.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "industry", "headquarters"]
    ordering_fields = ["name", "created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        return Company.objects.annotate(jobs_count=Count("jobs")).order_by("name")


class JobSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public provenance registry of all aggregation sources and feeds.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = JobSourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["source_type", "status", "is_verified"]
    search_fields = ["name", "source_url"]

    def get_queryset(self):
        return JobSource.objects.all().order_by("name")


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Directory of job categories."""
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    lookup_field = "slug"


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """Directory of known skills in CareerHunt taxonomy."""
    permission_classes = [permissions.AllowAny]
    queryset = Skill.objects.select_related("category").all().order_by("name")
    serializer_class = SkillSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    lookup_field = "slug"


class SavedJobViewSet(viewsets.ModelViewSet):
    """
    Candidate saved opportunities bookmark manager.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related(
            "job", "job__company", "job__source"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Candidate job application pipeline manager.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApplicationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["applied_date", "updated_at"]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user).select_related(
            "job", "job__company", "job__source"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JobAlertViewSet(viewsets.ModelViewSet):
    """
    Candidate automated opportunity alert configurations.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobAlertSerializer

    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReportViewSet(viewsets.ModelViewSet):
    """
    Listing issue submission endpoint for candidate crowdsourced moderation.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer
    http_method_names = ["get", "post"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Report.objects.all().select_related("job", "reported_by")
        return Report.objects.filter(reported_by=self.request.user).select_related("job")

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
