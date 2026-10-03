"""
Stage 4, 5, and 6 verification tests for CareerHunt.
Validates Job & Company management, frontend exploration views, faceted search, and filtering.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.companies.models import Company
from apps.sources.models import JobSource
from apps.jobs.models import Category, Skill, Job, JobSkill


class Stage456JobsSearchTestCase(TestCase):
    """
    Test suite for Job discovery, faceted search, filtering, and company views.
    """

    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name="Stripe Global",
            website="https://stripe.com",
            industry="Fintech",
            headquarters="San Francisco / Dublin",
            is_verified=True,
        )

        self.source = JobSource.objects.create(
            name="Stripe Official Careers",
            source_type="official_company",
            source_url="https://stripe.com/jobs",
            status="active",
            is_verified=True,
        )

        self.category_dev = Category.objects.create(name="Software Engineering")
        self.skill_python = Skill.objects.create(name="Python", category=self.category_dev)
        self.skill_react = Skill.objects.create(name="React", category=self.category_dev)

        now = timezone.now()

        # Job 1: Active Internship in Bangalore with Python
        self.job1 = Job.objects.create(
            title="Backend Engineering Intern",
            company=self.company,
            source=self.source,
            category=self.category_dev,
            opportunity_type="internship",
            experience_level="fresher",
            remote_type="hybrid",
            location_name="Bangalore, India",
            source_url="https://stripe.com/jobs/1",
            application_url="https://stripe.com/apply/1",
            description="Build modern payment infrastructure.",
            requirements="Solid Python skills.",
            application_deadline=now + timedelta(days=10),
            posted_at=now - timedelta(days=2),
        )
        JobSkill.objects.create(job=self.job1, skill=self.skill_python)

        # Job 2: Full-Time Remote Fresher Role with React
        self.job2 = Job.objects.create(
            title="Frontend UI Engineer",
            company=self.company,
            source=self.source,
            category=self.category_dev,
            opportunity_type="full-time",
            experience_level="fresher",
            remote_type="remote",
            location_name="Remote",
            source_url="https://stripe.com/jobs/2",
            application_url="https://stripe.com/apply/2",
            description="Create delightful frontend experiences with React.",
            requirements="Modern React and TypeScript.",
            application_deadline=now + timedelta(days=2),  # Closing soon!
            posted_at=now - timedelta(days=1),
        )
        JobSkill.objects.create(job=self.job2, skill=self.skill_react)

        # Job 3: Upcoming Graduate Program (Opens in future)
        self.job3 = Job.objects.create(
            title="Graduate Leadership Program 2027",
            company=self.company,
            source=self.source,
            category=self.category_dev,
            opportunity_type="graduate-program",
            experience_level="fresher",
            remote_type="on-site",
            location_name="Dublin, Ireland",
            source_url="https://stripe.com/jobs/3",
            application_url="https://stripe.com/apply/3",
            description="Future leaders in fintech.",
            application_open_date=now + timedelta(days=5),
            application_deadline=now + timedelta(days=25),
        )

    def test_job_list_view_and_rendering(self):
        """Verify job discovery page returns HTTP 200 with job cards."""
        response = self.client.get(reverse("jobs:job_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend Engineering Intern")
        self.assertContains(response, "Frontend UI Engineer")

    def test_search_by_keyword(self):
        """Verify multi-word and skill keyword search."""
        # Search by title
        response = self.client.get(reverse("jobs:job_list") + "?q=Backend")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend Engineering Intern")
        self.assertNotContains(response, "Frontend UI Engineer")

        # Search by company name
        comp_resp = self.client.get(reverse("jobs:job_list") + "?q=Stripe")
        self.assertEqual(comp_resp.status_code, 200)
        self.assertContains(comp_resp, "Backend Engineering Intern")
        self.assertContains(comp_resp, "Frontend UI Engineer")

        # Search by required skill
        skill_resp = self.client.get(reverse("jobs:job_list") + "?q=React")
        self.assertEqual(skill_resp.status_code, 200)
        self.assertContains(skill_resp, "Frontend UI Engineer")
        self.assertNotContains(skill_resp, "Backend Engineering Intern")

    def test_faceted_filtering(self):
        """Verify filtering by opportunity type, remote mode, and deadline."""
        # 1. Filter by opportunity_type=internship
        intern_resp = self.client.get(reverse("jobs:job_list") + "?type=internship")
        self.assertEqual(intern_resp.status_code, 200)
        self.assertContains(intern_resp, "Backend Engineering Intern")
        self.assertNotContains(intern_resp, "Frontend UI Engineer")

        # 2. Filter by remote_type=remote
        remote_resp = self.client.get(reverse("jobs:job_list") + "?mode=remote")
        self.assertEqual(remote_resp.status_code, 200)
        self.assertContains(remote_resp, "Frontend UI Engineer")
        self.assertNotContains(remote_resp, "Backend Engineering Intern")

        # 3. Filter by deadline=this_week
        urgent_resp = self.client.get(reverse("jobs:job_list") + "?deadline=this_week")
        self.assertEqual(urgent_resp.status_code, 200)
        self.assertContains(urgent_resp, "Frontend UI Engineer")
        self.assertNotContains(urgent_resp, "Backend Engineering Intern")

    def test_internship_and_upcoming_views(self):
        """Verify dedicated internship and upcoming opportunity views."""
        # Internships
        intern_resp = self.client.get(reverse("jobs:internship_list"))
        self.assertEqual(intern_resp.status_code, 200)
        self.assertContains(intern_resp, "Backend Engineering Intern")
        self.assertNotContains(intern_resp, "Frontend UI Engineer")

        # Upcoming
        upcoming_resp = self.client.get(reverse("jobs:upcoming_list"))
        self.assertEqual(upcoming_resp.status_code, 200)
        self.assertContains(upcoming_resp, "Graduate Leadership Program 2027")
        self.assertContains(upcoming_resp, "Opens in")

    def test_job_detail_view_provenance(self):
        """Verify opportunity detail view clearly displays provenance and unaltered destination URL."""
        response = self.client.get(reverse("jobs:job_detail", kwargs={"slug": self.job1.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.job1.title)
        self.assertContains(response, self.source.name)
        self.assertContains(response, "Source Provenance")
        self.assertContains(response, self.job1.application_url)

    def test_company_views(self):
        """Verify company list and detail views."""
        list_resp = self.client.get(reverse("companies:company_list"))
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, "Stripe Global")

        detail_resp = self.client.get(reverse("companies:company_detail", kwargs={"slug": self.company.slug}))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, "Stripe Global")
        self.assertContains(detail_resp, "Backend Engineering Intern")
