from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "headquarters", "is_verified", "created_at")
    list_filter = ("is_verified", "industry")
    search_fields = ("name", "industry", "headquarters")
    prepopulated_fields = {"slug": ("name",)}
