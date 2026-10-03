"""
- CareerHunt Stage 16 Tests: Resume Analysis, Skill Matching & Profile Import.
- """
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.jobs.models import Skill, Company, Job, JobSkill
from apps.sources.models import JobSource
from apps.accounts.models import UserSkill
from apps.accounts.resume_parser import extract_skills_from_text, analyze_resume_text

User = get_user_model()


class Stage16ResumeAnalysisTestCase(TestCase):
    """Test suite for Stage 16 resume parsing and matching capabilities."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="resumecandidate",
            email="resumecandidate@example.com",
            password="StrongPassword123!"
        )

        from apps.jobs.models import Category
        self.category = Category.objects.create(name="Engineering", slug="engineering")

        # Create skills in taxonomy
        self.py_skill = Skill.objects.create(name="Python", slug="python", category=self.category)
        self.django_skill = Skill.objects.create(name="Django", slug="django", category=self.category)
        self.sql_skill = Skill.objects.create(name="PostgreSQL", slug="postgresql", category=self.category)
        self.react_skill = Skill.objects.create(name="React", slug="react", category=self.category)
        self.docker_skill = Skill.objects.create(name="Docker", slug="docker", category=self.category)

        # Create source and company
        self.source = JobSource.objects.create(
            name="Official Test Careers",
            source_type="official_company",
            source_url="https://example.com/careers"
        )
        self.company = Company.objects.create(
            name="DevTech Solutions",
            website="https://devtech.example.com",
            is_verified=True
        )

        # Create job with skills
        self.job = Job.objects.create(
            title="Junior Backend Engineer",
            slug="junior-backend-engineer",
            company=self.company,
            source=self.source,
            source_url="https://example.com/careers/jr-backend",
            application_url="https://example.com/careers/jr-backend/apply",
            description="Developing backend APIs and services using Python and Django.",
            opportunity_type="full-time",
            experience_level="fresher",
            remote_type="remote",
            location_name="Remote",
            status="active",
            verification_status="verified"
        )
        JobSkill.objects.create(job=self.job, skill=self.py_skill, is_mandatory=True)
        JobSkill.objects.create(job=self.job, skill=self.django_skill, is_mandatory=True)
        JobSkill.objects.create(job=self.job, skill=self.sql_skill, is_mandatory=False)

    def test_extract_skills_from_text(self):
        """Verify resume parser extracts skills corresponding to database taxonomy."""
        resume = """
        Experienced undergraduate student with hands-on knowledge of Python, Django,
        PostgreSQL database optimization, and basic React web frontend development.
        """
        extracted = extract_skills_from_text(resume)
        assert "Python" in extracted
        assert "Django" in extracted
        assert "PostgreSQL" in extracted
        assert "React" in extracted
        assert "Docker" not in extracted

    def test_analyze_resume_experience_and_matching(self):
        """Verify resume analysis computes fit score against opportunities."""
        resume = """
        B.Tech Computer Science graduate and fresher seeking entry-level backend role.
        Skills: Python, Django, REST APIs, Git.
        """
        analysis = analyze_resume_text(resume)
        assert "Python" in analysis["detected_skills"]
        assert "Django" in analysis["detected_skills"]
        assert analysis["estimated_experience"] == "fresher"

        opportunities = analysis["matching_opportunities"]
        assert len(opportunities) >= 1
        best_match = opportunities[0]
        assert best_match["job"].pk == self.job.pk
        # Matched Python & Django out of 3 skills -> 67%
        assert best_match["match_score"] >= 60
        assert "Python" in best_match["matched_skills"]
        assert "Django" in best_match["matched_skills"]
        assert "PostgreSQL" in best_match["missing_skills"]

    def test_resume_matcher_view_get_and_post(self):
        """Verify resume matcher web interface for authenticated candidate."""
        self.client.login(username="resumecandidate", password="StrongPassword123!")

        # GET request
        resp = self.client.get(reverse("accounts:resume_matcher"))
        assert resp.status_code == 200
        assert "Resume Analysis &amp; Skill Fit" in resp.content.decode() or "Resume Analysis" in resp.content.decode()

        # POST with resume text
        post_resp = self.client.post(reverse("accounts:resume_matcher"), {
            "resume_text": "I am a fresher engineer proficient in Python and PostgreSQL."
        })
        assert post_resp.status_code == 200
        content = post_resp.content.decode()
        assert "Python" in content
        assert "PostgreSQL" in content
        assert "Junior Backend Engineer" in content

    def test_import_resume_skills_into_profile(self):
        """Verify importing extracted resume skills adds them to candidate profile."""
        self.client.login(username="resumecandidate", password="StrongPassword123!")
        
        # Candidate has 0 skills initially
        assert self.user.profile.user_skills.count() == 0

        # Import skills via POST
        import_resp = self.client.post(reverse("accounts:import_resume_skills"), {
            "skills": "Python, PostgreSQL, Docker"
        }, follow=True)

        assert import_resp.status_code == 200
        # Profile now has 3 skills
        assert self.user.profile.user_skills.count() == 3
        user_skill_names = [us.skill.name for us in self.user.profile.user_skills.all()]
        assert "Python" in user_skill_names
        assert "PostgreSQL" in user_skill_names
        assert "Docker" in user_skill_names
