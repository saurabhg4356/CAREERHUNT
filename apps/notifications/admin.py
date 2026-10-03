from django.contrib import admin
from .models import JobAlert, Notification


@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "keywords", "location", "frequency", "is_active", "created_at")
    list_filter = ("is_active", "frequency")
    search_fields = ("name", "user__username", "keywords")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    search_fields = ("title", "user__username", "message")
