from django.contrib import admin
from .models import UserProfile, UserEducation, UserSkill


class UserEducationInline(admin.TabularInline):
    model = UserEducation
    extra = 1


class UserSkillInline(admin.TabularInline):
    model = UserSkill
    extra = 2


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline", "location", "experience_level", "preferred_work_mode", "created_at")
    list_filter = ("experience_level", "preferred_work_mode")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "location")
    inlines = [UserEducationInline, UserSkillInline]


@admin.register(UserEducation)
class UserEducationAdmin(admin.ModelAdmin):
    list_display = ("profile", "degree", "institution", "start_year", "end_year")
    search_fields = ("degree", "institution", "profile__user__username")


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ("profile", "skill", "proficiency")
    list_filter = ("proficiency", "skill")
    search_fields = ("skill__name", "profile__user__username")
