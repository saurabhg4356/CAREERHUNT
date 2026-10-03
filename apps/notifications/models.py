"""
Job Alerts and In-App Notifications for CareerHunt.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel


class JobAlert(TimeStampedModel):
    """
    Candidate automated opportunity alert criteria.
    """
    FREQUENCY_CHOICES = [
        ("instant", "Instant"),
        ("daily", "Daily Digest"),
        ("weekly", "Weekly Digest"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_alerts")
    name = models.CharField(max_length=150, help_text="e.g. Fresher Python Backend Roles")
    keywords = models.CharField(max_length=255, blank=True, help_text="e.g. Python, Django, AWS")
    location = models.CharField(max_length=150, blank=True, help_text="e.g. Bangalore or Remote")
    opportunity_type = models.CharField(max_length=30, blank=True)
    experience_level = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default="daily")
    last_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Job Alert"
        verbose_name_plural = "Job Alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}'s Alert: {self.name}"


class Notification(TimeStampedModel):
    """
    In-app alert for deadline warnings, new matching opportunities, and application reminders.
    """
    TYPE_CHOICES = [
        ("job_alert", "New Matching Opportunity"),
        ("deadline_approaching", "Saved Opportunity Deadline"),
        ("application_status", "Application Progress Reminder"),
        ("system", "System Notice"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="system")
    target_url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title} ({'Read' if self.is_read else 'Unread'})"
