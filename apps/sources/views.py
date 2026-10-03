"""
Public source provenance and transparency views for CareerHunt.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import JobSource


class SourceListView(ListView):
    """
    Public directory of identifiable sources showing verification status,
    source types, and last checked timestamps.
    """
    model = JobSource
    template_name = "sources/source_list.html"
    context_object_name = "sources"

    def get_queryset(self):
        return JobSource.objects.all().order_by("-is_verified", "-total_jobs_collected")


class SourceDetailView(DetailView):
    """
    Detailed provenance view for an individual job source with telemetry and recent jobs.
    """
    model = JobSource
    template_name = "sources/source_detail.html"
    context_object_name = "source"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jobs"] = self.object.jobs.select_related("company").prefetch_related("job_skills__skill").order_by("-posted_at")[:12]
        context["recent_logs"] = self.object.scraping_logs.all()[:5]
        return context
