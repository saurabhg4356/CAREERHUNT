"""
Stage 10, 11, and 12 verification tests for CareerHunt.
Validates Saved Jobs, Application Tracker, Recommendation Engine, and Skill Gap Analysis.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.companies.models import Company
from apps.sources.models import JobSource
from apps.jobs.models import Job, Category, Skill, JobSkill, SavedJob
from apps.accounts.models import UserSkill
from apps.applications.models import Application
from apps.recommendations.engine import compute_match_score


class Stage101112UserFeaturesTestCase(TestCase):
    """
    Test suite for bookmarking, application tracking, recommendation scoring, and skill gaps.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="candidate_jane",
            password="StrongPassword123!",
            first_name="Jane",
        )
        self.profile = self.user.profile
        self.profile.experience_level = "fresher"
        self.profile.preferred_work_mode = "remote"
        self.profile.preferred_locations = ["Bangalore", "Remote"]
        self.profile.preferred_job_types = ["internship"]
        self.profile.save()

        self.company = Company.objects.create(name="Netflix Tech")
        self.source = JobSource.objects.create(
            name="Netflix Careers",
            source_url="https://jobs.netflix.com",
            source_type="official_company",
        )

        self.category = Category.objects.create(name="Engineering")
        self.skill_python = Skill.objects.create(name="Python", category=self.category)
        self.skill_django = Skill.objects.create(name="Django", category=self.category)
        self.skill_aws = Skill.objects.create(name="AWS", category=self.category)

        # Candidate possesses Python and Django
        UserSkill.objects.create(profile=self.profile, skill=self.skill_python)
        UserSkill.objects.create(profile=self.profile, skill=self.skill_django)

        # Job requires Python, Django, and AWS
        self.job = Job.objects.create(
            title="Cloud Backend Intern",
            company=self.company,
            source=self.source,
            category=self.category,
            opportunity_type="internship",
            experience_level="fresher",
            remote_type="remote",
            location_name="Remote",
            application_url="https://jobs.netflix.com/apply/1",
            source_url="https://jobs.netflix.com/jobs/1",
            description="Backend role at Netflix.",
        )
        JobSkill.objects.create(job=self.job, skill=self.skill_python)
        JobSkill.objects.create(job=self.job, skill=self.skill_django)
        JobSkill.objects.create(job=self.job, skill=self.skill_aws)

    def test_saved_jobs_toggle_and_listing(self):
        """Verify bookmarking an opportunity and listing saved jobs."""
        self.client.login(username="candidate_jane", password="StrongPassword123!")

        # 1. Save job
        toggle_resp = self.client.post(reverse("jobs:toggle_save", kwargs={"slug": self.job.slug}))
        self.assertEqual(toggle_resp.status_code, 302)
        self.assertTrue(SavedJob.objects.filter(user=self.user, job=self.job).exists())

        # 2. View saved jobs page
        saved_list_resp = self.client.get(reverse("jobs:saved_jobs"))
        self.assertEqual(saved_list_resp.status_code, 200)
        self.assertContains(saved_list_resp, "Cloud Backend Intern")

        # 3. Unsave job
        unsave_resp = self.client.post(reverse("jobs:toggle_save", kwargs={"slug": self.job.slug}))
        self.assertEqual(unsave_resp.status_code, 302)
        self.assertFalse(SavedJob.objects.filter(user=self.user, job=self.job).exists())

    def test_application_tracker_lifecycle(self):
        """Verify adding, updating status, and deleting application tracking entries."""
        self.client.login(username="candidate_jane", password="StrongPassword123!")

        # 1. Add application tracking
        track_resp = self.client.post(reverse("applications:track_job", kwargs={"job_id": self.job.pk}), {
            "status": "applied",
            "notes": "Submitted resume via referral.",
        })
        self.assertEqual(track_resp.status_code, 302)

        app = Application.objects.get(user=self.user, job=self.job)
        self.assertEqual(app.status, "applied")
        self.assertEqual(app.notes, "Submitted resume via referral.")

        # 2. Update status to interview
        update_resp = self.client.post(reverse("applications:update_application", kwargs={"pk": app.pk}), {
            "status": "interview",
            "notes": "Technical round scheduled.",
        })
        self.assertEqual(update_resp.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, "interview")

        # 3. Dashboard view
        dash_resp = self.client.get(reverse("applications:dashboard"))
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, "Cloud Backend Intern")
        self.assertContains(dash_resp, "Interviewing")

        # 4. Delete tracking
        del_resp = self.client.post(reverse("applications:delete_application", kwargs={"pk": app.pk}))
        self.assertEqual(del_resp.status_code, 302)
        self.assertFalse(Application.objects.filter(user=self.user, job=self.job).exists())

    def test_recommendation_scoring_and_skill_gap(self):
        """Verify rule-based CareerHunt match score and skill gap identification."""
        score_data = compute_match_score(self.profile, self.job)

        # Job requires: Python, Django, AWS
        # Candidate has: Python, Django
        # Matched: 2/3 = 66.67%
        self.assertIn("Python", score_data["matched_skills"])
        self.assertIn("Django", score_data["matched_skills"])
        self.assertIn("AWS", score_data["missing_skills"])

        # Location: Remote matches candidate preference (100%)
        self.assertEqual(score_data["location_match"], 100)

        # Experience: Fresher matches Fresher (100%)
        self.assertEqual(score_data["experience_match"], 100)

        # Type: Internship matches preferred types (100%)
        self.assertEqual(score_data["type_match"], 100)

        # Total expected score: 0.50*67 + 0.20*100 + 0.20*100 + 0.10*100 = 33.5 + 20 + 20 + 10 = ~83-84%
        self.assertTrue(80 <= score_data["match_percentage"] <= 85)

    def test_recommendation_and_skill_gap_views(self):
        """Verify recommendation list and skill gap detail views."""
        self.client.login(username="candidate_jane", password="StrongPassword123!")

        rec_resp = self.client.get(reverse("recommendations:list"))
        self.assertEqual(rec_resp.status_code, 200)
        self.assertContains(rec_resp, "Cloud Backend Intern")
        self.assertContains(rec_resp, "Match Score")

        gap_resp = self.client.get(reverse("recommendations:skill_gap", kwargs={"slug": self.job.slug}))
        self.assertEqual(gap_resp.status_code, 200)
        self.assertContains(gap_resp, "Missing Skills to Learn")
        self.assertContains(gap_resp, "AWS")
        self.assertContains(gap_resp, "Matched Skills")
        self.assertContains(gap_resp, "Python")
