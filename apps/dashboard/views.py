"""
Admin Telemetry, Source Monitoring, and Moderation Dashboard for CareerHunt.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import Job, Skill, Category
from apps.companies.models import Company
from apps.sources.models import JobSource, ScrapingLog
from apps.reports.models import Report


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_view(request):
    """
    Unified administration dashboard displaying platform health metrics,
    collector telemetry, moderation queues, and skill demand distributions.
    """
    now = timezone.now()
    three_days_later = now + timedelta(days=3)

    # 1. High-Level Metrics
    metrics = {
        "total_users": User.objects.count(),
        "candidates": User.objects.filter(is_staff=False).count(),
        "total_jobs": Job.objects.count(),
        "active_jobs": Job.objects.filter(status__in=["active", "closing-soon"]).count(),
        "internships": Job.objects.filter(opportunity_type="internship").count(),
        "upcoming_jobs": Job.objects.filter(Q(status="upcoming") | Q(application_open_date__gt=now)).count(),
        "closing_soon": Job.objects.filter(application_deadline__gte=now, application_deadline__lte=three_days_later).count(),
        "expired_jobs": Job.objects.filter(status="expired").count(),
        "total_companies": Company.objects.count(),
        "total_sources": JobSource.objects.count(),
        "active_sources": JobSource.objects.filter(status="active").count(),
        "failing_sources": JobSource.objects.filter(status__in=["failing", "degraded"]).count(),
        "pending_reports": Report.objects.filter(status="pending").count(),
    }

    # 2. Source Monitoring
    sources = JobSource.objects.all().order_by("-is_verified", "name")

    # 3. Moderation Reports Queue
    pending_reports = Report.objects.filter(status="pending").select_related("job", "reported_by")[:10]

    # 4. Distribution Breakdown by Opportunity Type
    type_distribution = Job.objects.values("opportunity_type").annotate(count=Count("id")).order_by("-count")

    # 5. Distribution Breakdown by Experience Level
    exp_distribution = Job.objects.values("experience_level").annotate(count=Count("id")).order_by("-count")

    # 6. Top Demanded Skills
    top_skills = Skill.objects.annotate(
        active_job_count=Count("skill_jobs")
    ).order_by("-active_job_count")[:10]

    return render(request, "dashboard/admin_dashboard.html", {
        "metrics": metrics,
        "sources": sources,
        "pending_reports": pending_reports,
        "type_distribution": type_distribution,
        "exp_distribution": exp_distribution,
        "top_skills": top_skills,
    })
