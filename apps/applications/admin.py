from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "status", "applied_date", "interview_date", "updated_at")
    list_filter = ("status", "applied_date")
    search_fields = ("user__username", "job__title", "job__company__name", "notes")
