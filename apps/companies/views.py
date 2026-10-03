"""
Company views for CareerHunt.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from .models import Company


class CompanyListView(ListView):
    """Lists hiring companies and their open opportunities."""
    model = Company
    template_name = "companies/company_list.html"
    context_object_name = "companies"
    paginate_by = 12

    def get_queryset(self):
        return Company.objects.annotate(
            active_jobs_count=Count("jobs", filter=Q(jobs__status__in=["active", "closing-soon"]))
        ).order_by("-active_jobs_count", "name")


class CompanyDetailView(DetailView):
    """Displays company profile, headquarters, industry, and its open opportunities."""
    model = Company
    template_name = "companies/company_detail.html"
    context_object_name = "company"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jobs"] = self.object.jobs.select_related("source").prefetch_related("job_skills__skill").order_by("-posted_at")
        return context
