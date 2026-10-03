"""
Stage 7, 8, and 9 verification tests for CareerHunt.
Validates Source management, Collector pipeline, and Deterministic Deduplication.
"""
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from apps.sources.models import JobSource, ScrapingLog
from apps.companies.models import Company
from apps.jobs.models import Job
from collectors.pipeline import (
    canonicalize_url,
    normalize_opportunity,
    validate_opportunity,
    deduplicate_opportunity,
)
from collectors.api.rest_collector import RestApiCollector


class Stage789CollectorsDedupeTestCase(TestCase):
    """
    Test suite for source management, ingestion pipeline, validation, and deduplication.
    """

    def setUp(self):
        self.client = Client()
        self.source = JobSource.objects.create(
            name="Official Acme Careers",
            source_type="official_company",
            source_url="https://acme.example.com/careers",
            status="active",
            is_verified=True,
        )
        self.company = Company.objects.create(name="Acme Corp")

    def test_canonicalize_url(self):
        """Verify tracking parameters and fragments are stripped from URLs."""
        raw_url = "https://example.com/jobs/123/?utm_source=linkedin&utm_campaign=winter26&ref=student_board#apply"
        clean = canonicalize_url(raw_url)
        self.assertEqual(clean, "https://example.com/jobs/123")

    def test_normalization_and_validation(self):
        """Verify field normalization and validation rules."""
        raw = {
            "title": "  Software Engineering Intern (Summer 2026)  ",
            "company_name": "Acme Corp",
            "application_url": "https://acme.example.com/apply/123?utm_medium=email",
            "opportunity_type": "full-time",  # Should be normalized to internship due to title
            "experience_level": "fresher",
            "remote_type": "remote",
            "location_name": "Remote",
        }

        norm = normalize_opportunity(raw)
        self.assertEqual(norm["title"], "Software Engineering Intern (Summer 2026)")
        self.assertEqual(norm["opportunity_type"], "internship")
        self.assertEqual(norm["application_url"], "https://acme.example.com/apply/123")

        valid, err = validate_opportunity(norm)
        self.assertTrue(valid)
        self.assertIsNone(err)

        # Invalid opportunity (missing company and invalid URL scheme)
        invalid_norm = norm.copy()
        invalid_norm["company_name"] = ""
        is_val, err_reason = validate_opportunity(invalid_norm)
        self.assertFalse(is_val)
        self.assertIn("Company name", err_reason)

    def test_deterministic_deduplication(self):
        """Verify multi-tiered duplicate detection."""
        # Create baseline opportunity
        existing_job = Job.objects.create(
            title="DevOps Trainee",
            company=self.company,
            source=self.source,
            external_id="ACM-990",
            application_url="https://acme.example.com/apply/devops-990",
            source_url="https://acme.example.com/jobs/devops-990",
            location_name="Bangalore",
            description="Devops role.",
        )

        # Tier 1 Deduplication: Match on (source, external_id)
        candidate1 = {
            "external_id": "ACM-990",
            "application_url": "https://acme.example.com/apply/different-url",
            "company_name": "Acme Corp",
            "title": "Different Title",
            "location_name": "Bangalore",
        }
        match1 = deduplicate_opportunity(self.source, candidate1)
        self.assertEqual(match1, existing_job)

        # Tier 2 Deduplication: Match on canonical application_url
        candidate2 = {
            "external_id": "ANOTHER-ID-991",
            "application_url": "https://acme.example.com/apply/devops-990",
            "company_name": "Acme Corp",
            "title": "DevOps Trainee",
            "location_name": "Bangalore",
        }
        match2 = deduplicate_opportunity(self.source, candidate2)
        self.assertEqual(match2, existing_job)

        # Tier 3 Deduplication: Match on (company, title, location)
        candidate3 = {
            "external_id": "",
            "application_url": "https://someboard.example.com/apply/xyz",
            "company_name": "Acme Corp",
            "title": "DevOps Trainee",
            "location_name": "Bangalore",
        }
        match3 = deduplicate_opportunity(self.source, candidate3)
        self.assertEqual(match3, existing_job)

        # Non-duplicate
        unique_candidate = {
            "external_id": "NEW-123",
            "application_url": "https://acme.example.com/apply/new-role",
            "company_name": "Acme Corp",
            "title": "Unique Security Specialist",
            "location_name": "Remote",
        }
        no_match = deduplicate_opportunity(self.source, unique_candidate)
        self.assertIsNone(no_match)

    @patch("requests.get")
    def test_rest_api_collector_run_and_logging(self, mock_get):
        """Verify RestApiCollector fetches, normalizes, deduplicates, and logs telemetry."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "ACME-101",
                "title": "Junior Python Developer",
                "company_name": "Acme Corp",
                "application_url": "https://acme.example.com/apply/101",
                "description": "Junior python engineer.",
                "opportunity_type": "full-time",
                "experience_level": "fresher",
                "location_name": "Pune",
                "skills": ["Python", "Django"],
            }
        ]
        mock_get.return_value = mock_response

        collector = RestApiCollector(self.source)
        log = collector.run_with_logging()

        self.assertEqual(log.status, "success")
        self.assertEqual(log.items_fetched, 1)
        self.assertEqual(log.items_created, 1)

        # Verify job was created with skills
        job = Job.objects.get(external_id="ACME-101")
        self.assertEqual(job.title, "Junior Python Developer")
        self.assertEqual(job.skills.count(), 2)

    def test_source_views(self):
        """Verify source transparency directory and detail views."""
        list_resp = self.client.get(reverse("sources:source_list"))
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, "Official Acme Careers")

        detail_resp = self.client.get(reverse("sources:source_detail", kwargs={"pk": self.source.pk}))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, "Official Acme Careers")
        self.assertContains(detail_resp, "Source Provenance")
