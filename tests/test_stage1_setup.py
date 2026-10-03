"""
Stage 1 verification tests for CareerHunt.
Validates project configuration, basic routing, health check, and templates.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings


class Stage1SetupTestCase(TestCase):
    """
    Test suite for Stage 1 setup validation.
    """

    def setUp(self):
        self.client = Client()

    def test_settings_loaded(self):
        """Verify that essential settings are correctly initialized."""
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertIn("apps.core.apps.CoreConfig", settings.INSTALLED_APPS)
        self.assertIn("rest_framework", settings.INSTALLED_APPS)

    def test_health_check_endpoint(self):
        """Verify that the /health/ endpoint returns HTTP 200 with ok status."""
        response = self.client.get(reverse("core:health_check"))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "ok")
        self.assertEqual(json_data.get("service"), "CareerHunt Core")

    def test_homepage_loads(self):
        """Verify that the landing page renders with HTTP 200 and expected brand."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CareerHunt")
        self.assertContains(response, "Discover verified job and internship opportunities")

    def test_custom_404_handler(self):
        """Verify custom 404 error page returns HTTP 404 with friendly template."""
        response = self.client.get("/non-existent-endpoint-test-404/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page Not Found", status_code=404)
