"""
Source provenance and collector audit models for CareerHunt.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class JobSource(TimeStampedModel):
    """
    Represents an identifiable source of job/internship opportunities.
    """
    SOURCE_TYPES = [
        ("official_company", "Official Company Careers Page"),
        ("government", "Official Government Portal"),
        ("authorized_api", "Authorized API"),
        ("rss_feed", "RSS / Atom Feed"),
        ("job_board", "Job Board / Aggregator"),
        ("manual_admin", "Manual Admin Entry"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("degraded", "Degraded"),
        ("failing", "Failing"),
        ("inactive", "Inactive"),
    ]

    name = models.CharField(max_length=255, unique=True)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES, default="official_company")
    source_url = models.URLField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    is_verified = models.BooleanField(default=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    total_jobs_collected = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Job Source"
        verbose_name_plural = "Job Sources"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class ScrapingLog(TimeStampedModel):
    """
    Telemetry and audit trail for collector pipeline execution runs.
    """
    STATUS_CHOICES = [
        ("started", "Started"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("failed", "Failed"),
    ]

    source = models.ForeignKey(JobSource, on_delete=models.CASCADE, related_name="scraping_logs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="started")
    items_fetched = models.PositiveIntegerField(default=0)
    items_created = models.PositiveIntegerField(default=0)
    items_updated = models.PositiveIntegerField(default=0)
    items_skipped = models.PositiveIntegerField(default=0)
    duration_seconds = models.FloatField(default=0.0)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "Scraping Log"
        verbose_name_plural = "Scraping Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Log {self.source.name} - {self.status} at {self.created_at:%Y-%m-%d %H:%M}"
