from django.contrib import admin
from .models import Category, Skill, Job, JobSkill


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 2


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug")
    list_filter = ("category",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title", "company", "opportunity_type", "experience_level",
        "remote_type", "location_name", "status", "verification_status",
        "posted_at", "application_deadline"
    )
    list_filter = (
        "opportunity_type", "experience_level", "remote_type",
        "status", "verification_status", "category"
    )
    search_fields = ("title", "company__name", "description", "location_name")
    inlines = [JobSkillInline]
    readonly_fields = ("slug", "created_at", "updated_at")
