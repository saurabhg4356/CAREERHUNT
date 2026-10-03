"""
REST API Serializers for CareerHunt.
Serializes opportunities, companies, sources, skills, applications, and saved jobs.
"""
from rest_framework import serializers
from apps.companies.models import Company
from apps.sources.models import JobSource
from apps.jobs.models import Category, Skill, Job, JobSkill, SavedJob
from apps.applications.models import Application
from apps.notifications.models import JobAlert
from apps.reports.models import Report


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class SkillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default="")

    class Meta:
        model = Skill
        fields = ["id", "name", "slug", "category", "category_name"]


class CompanySerializer(serializers.ModelSerializer):
    jobs_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "slug",
            "website",
            "logo",
            "description",
            "industry",
            "headquarters",
            "is_verified",
            "jobs_count",
        ]


class JobSourceSerializer(serializers.ModelSerializer):
    source_type_display = serializers.CharField(source="get_source_type_display", read_only=True)

    class Meta:
        model = JobSource
        fields = [
            "id",
            "name",
            "source_type",
            "source_type_display",
            "source_url",
            "status",
            "is_verified",
            "last_checked_at",
            "total_jobs_collected",
        ]


class JobSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = JobSkill
        fields = ["id", "skill", "is_mandatory"]


class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    source = JobSourceSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    deadline_display = serializers.CharField(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "slug",
            "company",
            "category",
            "source",
            "source_url",
            "application_url",
            "opportunity_type",
            "experience_level",
            "remote_type",
            "location_name",
            "salary_min",
            "salary_max",
            "salary_currency",
            "is_salary_disclosed",
            "status",
            "verification_status",
            "posted_at",
            "application_open_date",
            "application_deadline",
            "deadline_display",
            "skills",
        ]


class JobDetailSerializer(JobSerializer):
    class Meta(JobSerializer.Meta):
        fields = JobSerializer.Meta.fields + [
            "description",
            "requirements",
            "external_id",
            "last_checked_at",
            "created_at",
            "updated_at",
        ]


class SavedJobSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source="job", read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(), source="job", write_only=True
    )

    class Meta:
        model = SavedJob
        fields = ["id", "job_id", "job_details", "created_at"]
        read_only_fields = ["created_at"]


class ApplicationSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source="job", read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(), source="job", write_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "job_id",
            "job_details",
            "status",
            "status_display",
            "applied_date",
            "interview_date",
            "follow_up_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class JobAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAlert
        fields = [
            "id",
            "name",
            "keywords",
            "location",
            "opportunity_type",
            "frequency",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class ReportSerializer(serializers.ModelSerializer):
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "job",
            "reason",
            "reason_display",
            "details",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]
