from django.contrib import admin
from .models import JobSource, ScrapingLog


@admin.register(JobSource)
class JobSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "source_type", "status", "is_verified", "total_jobs_collected", "error_count", "last_checked_at")
    list_filter = ("source_type", "status", "is_verified")
    search_fields = ("name", "source_url")


@admin.register(ScrapingLog)
class ScrapingLogAdmin(admin.ModelAdmin):
    list_display = ("source", "status", "items_fetched", "items_created", "items_updated", "items_skipped", "duration_seconds", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("source__name", "error_message")
    readonly_fields = ("created_at", "updated_at")
