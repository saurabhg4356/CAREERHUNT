"""
CareerHunt Stage 18 & 19 Tests: Security Hardening & Performance Optimization.
Verifies authorization controls, IDOR prevention, security headers, and query profiling / N+1 avoidance.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.utils import timezone

from apps.companies.models import Company
from apps.sources.models import JobSource
from apps.jobs.models import Category, Skill, Job, JobSkill, SavedJob
from apps.applications.models import Application
from apps.accounts.models import UserEducation

User = get_user_model()


class Stage1819SecurityPerformanceTestCase(TestCase):
    """Test suite verifying security isolation and query performance."""

    def setUp(self):
        self.client = Client()
        self.user_alice = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="StrongPassword123!"
        )
        self.user_bob = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="StrongPassword123!"
        )
        self.staff_user = User.objects.create_user(
            username="admin_staff",
            email="admin@example.com",
            password="StrongPassword123!",
            is_staff=True
        )

        self.category = Category.objects.create(name="Data Engineering", slug="data-engineering")
        self.skill_python = Skill.objects.create(name="Python", slug="python", category=self.category)
        self.skill_sql = Skill.objects.create(name="SQL", slug="sql", category=self.category)

        self.source = JobSource.objects.create(
            name="Verified Tech Portal",
            source_type="official_company",
            source_url="https://portal.example.com"
        )
        self.company = Company.objects.create(
            name="SecureCorp",
            website="https://securecorp.example.com",
            is_verified=True
        )

        # Create multiple jobs for performance testing
        self.jobs = []
        for i in range(5):
            job = Job.objects.create(
                title=f"Data Engineer {i+1}",
                slug=f"data-engineer-{i+1}",
                company=self.company,
                category=self.category,
                source=self.source,
                source_url=f"https://securecorp.example.com/job-{i+1}",
                application_url=f"https://securecorp.example.com/job-{i+1}/apply",
                description=f"Building robust data pipelines at scale {i+1}.",
                opportunity_type="full-time",
                experience_level="fresher",
                remote_type="remote",
                location_name="Remote",
                status="active",
                verification_status="verified",
                posted_at=timezone.now(),
            )
            JobSkill.objects.create(job=job, skill=self.skill_python, is_mandatory=True)
            JobSkill.objects.create(job=job, skill=self.skill_sql, is_mandatory=False)
            self.jobs.append(job)

        # Alice creates an application
        self.alice_app = Application.objects.create(
            user=self.user_alice,
            job=self.jobs[0],
            status="applied",
            notes="Confidential referral notes from Alice."
        )

        # Alice creates an education record
        self.alice_edu = UserEducation.objects.create(
            profile=self.user_alice.profile,
            degree="B.Tech Computer Science",
            institution="Premier Institute",
            start_year=2021,
            end_year=2025
        )

    def test_security_headers_present(self):
        """Verify essential security HTTP headers are returned in responses."""
        resp = self.client.get(reverse("core:home"))
        assert resp.status_code == 200
        # X-Frame-Options preventing clickjacking
        assert resp.headers.get("X-Frame-Options") in ["DENY", "SAMEORIGIN"]
        # nosniff preventing MIME sniffing
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"

    def test_idor_prevention_on_applications(self):
        """Verify candidate Bob cannot update or delete Alice's application."""
        self.client.login(username="bob", password="StrongPassword123!")

        # Attempt to delete Alice's application
        del_resp = self.client.post(reverse("applications:delete_application", kwargs={"pk": self.alice_app.pk}))
        assert del_resp.status_code == 404  # Bob cannot see or delete Alice's app
        assert Application.objects.filter(pk=self.alice_app.pk).exists()

        # Attempt to update Alice's application
        update_resp = self.client.post(reverse("applications:update_application", kwargs={"pk": self.alice_app.pk}), {
            "status": "rejected",
            "notes": "Hacked by Bob",
        })
        assert update_resp.status_code == 404
        self.alice_app.refresh_from_db()
        assert self.alice_app.status == "applied"
        assert "Hacked" not in self.alice_app.notes

    def test_idor_prevention_on_education(self):
        """Verify candidate Bob cannot delete Alice's education credential."""
        self.client.login(username="bob", password="StrongPassword123!")

        del_resp = self.client.post(reverse("accounts:delete_education", kwargs={"pk": self.alice_edu.pk}))
        assert del_resp.status_code == 404
        assert UserEducation.objects.filter(pk=self.alice_edu.pk).exists()

    def test_unauthenticated_protected_routes_redirect(self):
        """Verify unauthenticated requests to protected endpoints redirect to login."""
        protected_urls = [
            reverse("applications:dashboard"),
            reverse("jobs:saved_jobs"),
            reverse("notifications:list"),
            reverse("recommendations:list"),
            reverse("accounts:profile"),
            reverse("accounts:resume_matcher"),
        ]
        for url in protected_urls:
            resp = self.client.get(url)
            assert resp.status_code == 302
            assert "/accounts/login/" in resp.url

    def test_admin_dashboard_authorization(self):
        """Verify regular users cannot access staff dashboard."""
        self.client.login(username="alice", password="StrongPassword123!")
        denied_resp = self.client.get(reverse("dashboard:admin_dashboard"))
        assert denied_resp.status_code == 302  # redirected to admin login or home

        self.client.login(username="admin_staff", password="StrongPassword123!")
        allowed_resp = self.client.get(reverse("dashboard:admin_dashboard"))
        assert allowed_resp.status_code == 200

    def test_job_list_queries_prevent_n_plus_one(self):
        """Verify JobListView executes bounded constant queries regardless of item count."""
        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get(reverse("jobs:job_list"))
            assert resp.status_code == 200

        # With 5 jobs and prefetch/select_related, query count should be small (< 12 total including session/categories/skills)
        query_count = len(ctx.captured_queries)
        assert query_count < 12, f"Detected potential N+1 query issue: {query_count} queries executed."

    def test_model_indexes_exist(self):
        """Verify critical indexes on the Job model."""
        index_fields = [idx.fields for idx in Job._meta.indexes]
        # Verify compound status & opportunity_type & experience_level index
        assert ["status", "opportunity_type", "experience_level"] in index_fields
        # Verify status & deadline index
        assert ["status", "application_deadline"] in index_fields
