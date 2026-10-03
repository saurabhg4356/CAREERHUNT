from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("job", "reason", "status", "reported_by", "created_at", "resolved_at")
    list_filter = ("status", "reason", "created_at")
    search_fields = ("job__title", "details", "admin_notes")
