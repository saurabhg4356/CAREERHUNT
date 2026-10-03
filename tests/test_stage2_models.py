"""
Stage 2 verification tests for CareerHunt core database models.
Validates Company, JobSource, Category, Skill, Job, and JobSkill.
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.companies.models import Company
from apps.sources.models import JobSource, ScrapingLog
from apps.jobs.models import Category, Skill, Job, JobSkill


class Stage2ModelsTestCase(TestCase):
    """
    Test suite validating Stage 2 database entities, managers, and constraints.
    """

    def setUp(self):
        self.company = Company.objects.create(
            name="Google DeepMind",
            website="https://deepmind.google",
            industry="Artificial Intelligence",
            headquarters="London, UK",
            is_verified=True,
        )

        self.source = JobSource.objects.create(
            name="Google Careers Official",
            source_type="official_company",
            source_url="https://careers.google.com",
            status="active",
            is_verified=True,
        )

        self.category = Category.objects.create(
            name="Software Engineering",
            description="Software development and systems engineering",
        )

        self.skill_python = Skill.objects.create(
            name="Python",
            category=self.category,
        )
        self.skill_django = Skill.objects.create(
            name="Django",
            category=self.category,
        )

    def test_company_slug_generation(self):
        """Verify automatic slug generation for companies."""
        self.assertEqual(self.company.slug, "google-deepmind")
        self.assertTrue(self.company.is_verified)

    def test_job_source_and_scraping_log(self):
        """Verify JobSource creation and telemetry log relationship."""
        log = ScrapingLog.objects.create(
            source=self.source,
            status="success",
            items_fetched=25,
            items_created=10,
            duration_seconds=2.4,
        )
        self.assertEqual(self.source.scraping_logs.count(), 1)
        self.assertEqual(log.status, "success")

    def test_job_lifecycle_and_dynamic_status(self):
        """Verify dynamic status assignment based on dates."""
        now = timezone.now()

        # 1. Active opportunity
        active_job = Job.objects.create(
            title="Software Engineering Intern",
            company=self.company,
            source=self.source,
            category=self.category,
            source_url="https://careers.google.com/jobs/123",
            application_url="https://careers.google.com/apply/123",
            description="Work on frontier AI models.",
            opportunity_type="internship",
            experience_level="fresher",
            location_name="Bangalore, India",
            application_deadline=now + timedelta(days=15),
        )
        self.assertEqual(active_job.status, "active")
        self.assertIn("15 days remaining", active_job.deadline_display())
        self.assertFalse(active_job.is_closing_soon)

        # 2. Closing soon opportunity (within 3 days)
        closing_job = Job.objects.create(
            title="AI Research Fellow",
            company=self.company,
            source=self.source,
            category=self.category,
            source_url="https://careers.google.com/jobs/456",
            application_url="https://careers.google.com/apply/456",
            description="Research fellow position.",
            opportunity_type="graduate-program",
            experience_level="0-1",
            location_name="Remote",
            application_deadline=now + timedelta(days=2),
        )
        self.assertEqual(closing_job.status, "closing-soon")
        self.assertTrue(closing_job.is_closing_soon)
        self.assertIn("Closing soon", closing_job.deadline_display())

        # 3. Upcoming opportunity (opens in future)
        upcoming_job = Job.objects.create(
            title="Summer Analyst 2027",
            company=self.company,
            source=self.source,
            category=self.category,
            source_url="https://careers.google.com/jobs/789",
            application_url="https://careers.google.com/apply/789",
            description="Upcoming 2027 summer opening.",
            opportunity_type="internship",
            experience_level="fresher",
            location_name="Hyderabad, India",
            application_open_date=now + timedelta(days=7),
            application_deadline=now + timedelta(days=30),
        )
        self.assertEqual(upcoming_job.status, "upcoming")
        self.assertIn(upcoming_job.days_until_opening, [6, 7])

    def test_job_skill_relationships(self):
        """Verify M2M relationship between Job and Skill via JobSkill."""
        job = Job.objects.create(
            title="Backend Python Developer",
            company=self.company,
            source=self.source,
            category=self.category,
            source_url="https://careers.google.com/jobs/999",
            application_url="https://careers.google.com/apply/999",
            description="High scale backend.",
            opportunity_type="full-time",
            experience_level="fresher",
            location_name="Bangalore, India",
        )

        JobSkill.objects.create(job=job, skill=self.skill_python, is_mandatory=True)
        JobSkill.objects.create(job=job, skill=self.skill_django, is_mandatory=False)

        self.assertEqual(job.skills.count(), 2)
        mandatory_skills = job.job_skills.filter(is_mandatory=True)
        self.assertEqual(mandatory_skills.count(), 1)
        self.assertEqual(mandatory_skills.first().skill.name, "Python")

    def test_job_manager_custom_querysets(self):
        """Verify active(), upcoming(), internships(), and closing_soon() queries."""
        now = timezone.now()

        Job.objects.create(
            title="Intern Role",
            company=self.company,
            source=self.source,
            source_url="https://careers.google.com/jobs/i1",
            application_url="https://careers.google.com/apply/i1",
            description="Intern role.",
            opportunity_type="internship",
            experience_level="fresher",
            location_name="Remote",
            application_deadline=now + timedelta(days=10),
        )

        self.assertEqual(Job.objects.internships().count(), 1)
        self.assertEqual(Job.objects.active().count(), 1)
