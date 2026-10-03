"""
Application tracking models for CareerHunt candidates.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from apps.jobs.models import Job


class Application(TimeStampedModel):
    """
    Candidate application tracking lifecycle record.
    """
    STATUS_CHOICES = [
        ("saved", "Saved for Later"),
        ("applied", "Application Submitted"),
        ("assessment", "Online Assessment / Test"),
        ("interview", "Interviewing"),
        ("offer", "Offer Received"),
        ("rejected", "Not Selected"),
        ("withdrawn", "Withdrawn"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="candidate_applications")
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="applied", db_index=True)
    applied_date = models.DateField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Personal preparation notes, referral contact, or interview feedback.")

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        unique_together = ("user", "job")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} - {self.job.title} ({self.get_status_display()})"
