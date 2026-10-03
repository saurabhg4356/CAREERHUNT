"""
Stage 3 verification tests for CareerHunt candidate authentication and profiles.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile, UserEducation, UserSkill
from apps.jobs.models import Category, Skill


class Stage3AuthTestCase(TestCase):
    """
    Test suite for registration, login/logout, profile updates, and skills management.
    """

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Engineering")
        self.skill_python = Skill.objects.create(name="Python", category=self.category)
        self.skill_django = Skill.objects.create(name="Django", category=self.category)

    def test_registration_success_and_profile_signal(self):
        """Verify candidate registration creates user, hashes password, and triggers profile signal."""
        response = self.client.post(reverse("accounts:register"), {
            "username": "alexfresher",
            "first_name": "Alex",
            "last_name": "Rivera",
            "email": "alex@example.com",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:profile"))

        user = User.objects.get(username="alexfresher")
        self.assertTrue(user.check_password("StrongPassword123!"))
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.experience_level, "fresher")

    def test_registration_password_mismatch(self):
        """Verify registration rejects mismatched passwords."""
        response = self.client.post(reverse("accounts:register"), {
            "username": "badpass",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "PasswordOne123!",
            "confirm_password": "PasswordTwo456!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="badpass").exists())
        self.assertContains(response, "Passwords do not match")

    def test_login_and_logout_flow(self):
        """Verify authentication login and logout flows."""
        user = User.objects.create_user(
            username="john_doe",
            email="john@example.com",
            password="SecureSecretPass1!",
            first_name="John",
        )

        # Login with correct password
        response = self.client.post(reverse("accounts:login"), {
            "username": "john_doe",
            "password": "SecureSecretPass1!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:home"))

        # Access protected profile
        profile_resp = self.client.get(reverse("accounts:profile"))
        self.assertEqual(profile_resp.status_code, 200)
        self.assertContains(profile_resp, "John")

        # Logout
        logout_resp = self.client.get(reverse("accounts:logout"))
        self.assertEqual(logout_resp.status_code, 302)
        self.assertRedirects(logout_resp, reverse("core:home"))

    def test_profile_update_and_preferences(self):
        """Verify profile headline, location, and career preference updates."""
        user = User.objects.create_user(
            username="candidate1",
            email="cand1@example.com",
            password="Password123!",
            first_name="Sara",
            last_name="Connor",
        )
        self.client.login(username="candidate1", password="Password123!")

        response = self.client.post(reverse("accounts:profile"), {
            "first_name": "Sara",
            "last_name": "Connor",
            "email": "cand1@example.com",
            "headline": "Junior AI & Data Engineer",
            "phone": "+91 9988776655",
            "location": "Bangalore",
            "bio": "Enthusiastic graduate specializing in Python.",
            "experience_level": "fresher",
            "preferred_work_mode": "remote",
            "preferred_locations_str": "Bangalore, Pune, Remote",
            "preferred_job_types_raw": ["internship", "full-time"],
            "expected_salary_min": "600000",
        })
        self.assertEqual(response.status_code, 302)

        user.refresh_from_db()
        profile = user.profile
        self.assertEqual(profile.headline, "Junior AI & Data Engineer")
        self.assertEqual(profile.preferred_work_mode, "remote")
        self.assertIn("Bangalore", profile.preferred_locations)
        self.assertIn("internship", profile.preferred_job_types)

    def test_education_crud(self):
        """Verify adding and deleting educational credentials."""
        user = User.objects.create_user(username="student1", password="Password123!")
        self.client.login(username="student1", password="Password123!")

        # Add education
        resp = self.client.post(reverse("accounts:add_education"), {
            "degree": "B.Tech Computer Science",
            "institution": "National Institute of Technology",
            "start_year": 2023,
            "end_year": 2027,
            "grade_or_cgpa": "9.2 CGPA",
        })
        self.assertEqual(resp.status_code, 302)

        edu = UserEducation.objects.get(profile=user.profile)
        self.assertEqual(edu.degree, "B.Tech Computer Science")

        # Delete education
        del_resp = self.client.post(reverse("accounts:delete_education", kwargs={"pk": edu.pk}))
        self.assertEqual(del_resp.status_code, 302)
        self.assertEqual(UserEducation.objects.filter(profile=user.profile).count(), 0)

    def test_skills_management(self):
        """Verify adding and removing skills."""
        user = User.objects.create_user(username="coder1", password="Password123!")
        self.client.login(username="coder1", password="Password123!")

        # Add skill
        resp = self.client.post(reverse("accounts:add_skill"), {
            "skill_id": self.skill_python.id,
            "proficiency": "advanced",
        })
        self.assertEqual(resp.status_code, 302)

        user_skill = UserSkill.objects.get(profile=user.profile)
        self.assertEqual(user_skill.skill.name, "Python")
        self.assertEqual(user_skill.proficiency, "advanced")

        # Remove skill
        rem_resp = self.client.post(reverse("accounts:remove_skill", kwargs={"pk": user_skill.pk}))
        self.assertEqual(rem_resp.status_code, 302)
        self.assertEqual(UserSkill.objects.filter(profile=user.profile).count(), 0)
