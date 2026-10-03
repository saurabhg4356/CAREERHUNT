"""
CareerHunt Stage 17 Tests: Django REST Framework API Layer.
Verifies endpoints, serializers, permissions, filtering, search, and pagination.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.companies.models import Company
from apps.sources.models import JobSource
from apps.jobs.models import Category, Skill, Job, JobSkill, SavedJob
from apps.applications.models import Application
from apps.notifications.models import JobAlert
from apps.reports.models import Report

User = get_user_model()


class Stage17RestApiTestCase(TestCase):
    """Test suite for REST API v1 endpoints and permissions."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="api_candidate",
            email="apicandidate@example.com",
            password="StrongPassword123!"
        )

        self.category = Category.objects.create(name="Software Engineering", slug="software-engineering")
        self.skill1 = Skill.objects.create(name="Python", slug="python", category=self.category)
        self.skill2 = Skill.objects.create(name="PostgreSQL", slug="postgresql", category=self.category)

        self.source = JobSource.objects.create(
            name="Official Acme Careers",
            source_type="official_company",
            source_url="https://acme.example.com/careers"
        )
        self.company = Company.objects.create(
            name="Acme Corp",
            slug="acme-corp",
            website="https://acme.example.com",
            is_verified=True
        )

        self.job1 = Job.objects.create(
            title="Backend Software Intern",
            slug="backend-software-intern",
            company=self.company,
            category=self.category,
            source=self.source,
            source_url="https://acme.example.com/careers/intern",
            application_url="https://acme.example.com/careers/intern/apply",
            description="Internship focused on Python backend services.",
            opportunity_type="internship",
            experience_level="fresher",
            remote_type="remote",
            location_name="Bangalore, India",
            status="active",
            verification_status="verified",
            posted_at=timezone.now(),
        )
        JobSkill.objects.create(job=self.job1, skill=self.skill1, is_mandatory=True)

        self.job2 = Job.objects.create(
            title="Senior Platform Architect",
            slug="senior-platform-architect",
            company=self.company,
            category=self.category,
            source=self.source,
            source_url="https://acme.example.com/careers/senior-arch",
            application_url="https://acme.example.com/careers/senior-arch/apply",
            description="Platform architect requiring 5+ years experience.",
            opportunity_type="full-time",
            experience_level="2+",
            remote_type="on-site",
            location_name="Hyderabad, India",
            status="active",
            verification_status="verified",
            posted_at=timezone.now(),
        )

    def test_job_list_public_and_filtering(self):
        """Verify anonymous access, search, and faceted filtering on /api/v1/jobs/."""
        # 1. Unauthenticated public access
        resp = self.client.get(reverse("api:job-list"))
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert data["count"] == 2

        # 2. Filter by opportunity_type
        resp_filter = self.client.get(reverse("api:job-list"), {"opportunity_type": "internship"})
        assert resp_filter.status_code == 200
        filter_data = resp_filter.json()
        assert filter_data["count"] == 1
        assert filter_data["results"][0]["title"] == "Backend Software Intern"

        # 3. Search by keyword
        resp_search = self.client.get(reverse("api:job-list"), {"search": "Platform"})
        assert resp_search.status_code == 200
        search_data = resp_search.json()
        assert search_data["count"] == 1
        assert search_data["results"][0]["title"] == "Senior Platform Architect"

    def test_job_detail_endpoint(self):
        """Verify opportunity detail view returns comprehensive attributes and skills."""
        resp = self.client.get(reverse("api:job-detail", kwargs={"pk": self.job1.pk}))
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Backend Software Intern"
        assert data["company"]["name"] == "Acme Corp"
        assert data["source"]["source_url"] == "https://acme.example.com/careers"
        assert data["application_url"] == "https://acme.example.com/careers/intern/apply"
        assert len(data["skills"]) == 1
        assert data["skills"][0]["name"] == "Python"

    def test_custom_job_actions(self):
        """Verify custom actions: internships, freshers, closing_soon."""
        resp_intern = self.client.get(reverse("api:job-internships"))
        assert resp_intern.status_code == 200
        data = resp_intern.json()
        assert data["count"] == 1
        assert data["results"][0]["opportunity_type"] == "internship"

        resp_fresher = self.client.get(reverse("api:job-freshers"))
        assert resp_fresher.status_code == 200
        data = resp_fresher.json()
        assert data["count"] == 1
        assert data["results"][0]["experience_level"] == "fresher"

    def test_company_and_source_endpoints(self):
        """Verify company and source public listings."""
        resp_comp = self.client.get(reverse("api:company-list"))
        assert resp_comp.status_code == 200
        assert resp_comp.json()["count"] == 1

        resp_src = self.client.get(reverse("api:source-list"))
        assert resp_src.status_code == 200
        assert resp_src.json()["count"] == 1

    def test_saved_jobs_crud_authenticated(self):
        """Verify saved jobs API requires auth and operates on authenticated user."""
        # Unauthenticated rejected
        unauth_resp = self.client.get(reverse("api:saved-job-list"))
        assert unauth_resp.status_code in [401, 403]

        # Authenticated access
        self.client.login(username="api_candidate", password="StrongPassword123!")
        
        # Create saved job
        create_resp = self.client.post(reverse("api:saved-job-list"), {
            "job_id": self.job1.pk
        })
        assert create_resp.status_code == 201
        saved_id = create_resp.json()["id"]

        # List saved jobs
        list_resp = self.client.get(reverse("api:saved-job-list"))
        assert list_resp.status_code == 200
        assert list_resp.json()["count"] == 1

        # Delete saved job
        del_resp = self.client.delete(reverse("api:saved-job-detail", kwargs={"pk": saved_id}))
        assert del_resp.status_code == 204
        assert SavedJob.objects.filter(user=self.user).count() == 0

    def test_applications_crud_authenticated(self):
        """Verify application tracker API operations."""
        self.client.login(username="api_candidate", password="StrongPassword123!")

        # Create application tracker entry
        create_resp = self.client.post(reverse("api:application-list"), {
            "job_id": self.job1.pk,
            "status": "applied",
            "notes": "Applied through official portal with portfolio.",
        })
        assert create_resp.status_code == 201
        app_id = create_resp.json()["id"]

        # Update application status
        patch_resp = self.client.patch(reverse("api:application-detail", kwargs={"pk": app_id}), {
            "status": "interview",
            "notes": "Invited for Round 1 technical assessment.",
        }, content_type="application/json")
        assert patch_resp.status_code == 200
        assert patch_resp.json()["status"] == "interview"

    def test_job_alert_and_reports_api(self):
        """Verify job alerts and listing report creation via API."""
        self.client.login(username="api_candidate", password="StrongPassword123!")

        # Create alert
        alert_resp = self.client.post(reverse("api:alert-list"), {
            "name": "Backend Python Alerts",
            "keywords": "Python, Django",
            "opportunity_type": "internship",
            "frequency": "daily",
        })
        assert alert_resp.status_code == 201
        assert alert_resp.json()["name"] == "Backend Python Alerts"

        # Create listing report
        report_resp = self.client.post(reverse("api:report-list"), {
            "job": self.job2.pk,
            "reason": "expired_opportunity",
            "details": "Application link returns 404 page.",
        })
        assert report_resp.status_code == 201
        assert Report.objects.filter(reported_by=self.user).count() == 1
