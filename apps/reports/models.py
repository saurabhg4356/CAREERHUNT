"""
User listing reports and moderation queue models for CareerHunt.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from apps.jobs.models import Job


class Report(TimeStampedModel):
    """
    User-submitted report regarding questionable or expired listings.
    """
    REASON_CHOICES = [
        ("suspicious_link", "Suspicious or Broken Application Link"),
        ("requesting_money", "Opportunity is Requesting Money / Application Fee"),
        ("incorrect_information", "Inaccurate Job Details or Deadlines"),
        ("expired_opportunity", "Opportunity Has Already Closed or Expired"),
        ("fake_company", "Suspected Fraudulent or Impersonated Employer"),
        ("duplicate_listing", "Duplicate Opportunity Listing"),
        ("other", "Other Issue"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("investigating", "Investigating"),
        ("resolved", "Resolved (Action Taken)"),
        ("dismissed", "Dismissed (Valid Listing)"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="reports")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="submitted_reports")
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, default="suspicious_link")
    details = models.TextField(help_text="Please describe why this listing is suspicious or inaccurate.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    admin_notes = models.TextField(blank=True, help_text="Internal moderation notes.")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="moderated_reports")
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Listing Report"
        verbose_name_plural = "Listing Reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report on {self.job.title} ({self.get_reason_display()})"
