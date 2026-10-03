"""
Generic, polite REST API Opportunity Collector for CareerHunt.
Fetches JSON feeds from authorized career endpoints or partner boards.
"""
import time
import requests
from typing import Any, Dict, List, Optional
from django.conf import settings
from django.utils import timezone
from collectors.base import BaseCollector
from collectors.pipeline import (
    normalize_opportunity,
    validate_opportunity,
    deduplicate_opportunity,
)
from apps.sources.models import JobSource, ScrapingLog
from apps.companies.models import Company
from apps.jobs.models import Job, Skill, JobSkill


class RestApiCollector(BaseCollector):
    """
    Standard JSON API collector with timeout, custom User-Agent, and audit logging.
    """

    def __init__(self, source_instance: JobSource, endpoint_url: Optional[str] = None):
        super().__init__(
            source_name=source_instance.name,
            source_type=source_instance.source_type,
            source_url=endpoint_url or source_instance.source_url,
        )
        self.source_instance = source_instance
        self.headers = {
            "User-Agent": getattr(settings, "COLLECTOR_USER_AGENT", "CareerHuntBot/1.0"),
            "Accept": "application/json",
        }
        self.timeout = getattr(settings, "COLLECTOR_REQUEST_TIMEOUT", 15)

    def fetch(self) -> Any:
        response = requests.get(self.source_url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        # Supports list of items or dict with 'jobs' / 'results' key
        if isinstance(raw_data, list):
            return raw_data
        elif isinstance(raw_data, dict):
            for key in ["jobs", "results", "data", "opportunities"]:
                if key in raw_data and isinstance(raw_data[key], list):
                    return raw_data[key]
        return []

    def normalize(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        return normalize_opportunity(raw_item)

    def validate(self, normalized_item: Dict[str, Any]) -> bool:
        valid, reason = validate_opportunity(normalized_item)
        if not valid:
            return False
        return True

    def deduplicate(self, validated_item: Dict[str, Any]) -> Optional[Job]:
        return deduplicate_opportunity(self.source_instance, validated_item)

    def save(self, validated_item: Dict[str, Any], existing_instance: Optional[Job] = None) -> Job:
        company_name = validated_item["company_name"]
        company, _ = Company.objects.get_or_create(
            name=company_name,
            defaults={"is_verified": self.source_instance.is_verified}
        )

        defaults = {
            "source": self.source_instance,
            "category": None,
            "description": validated_item["description"] or f"Opportunity at {company_name}",
            "requirements": validated_item["requirements"],
            "opportunity_type": validated_item["opportunity_type"],
            "experience_level": validated_item["experience_level"],
            "remote_type": validated_item["remote_type"],
            "location_name": validated_item["location_name"],
            "salary_min": validated_item.get("salary_min"),
            "salary_max": validated_item.get("salary_max"),
            "is_salary_disclosed": validated_item.get("is_salary_disclosed", False),
            "application_open_date": validated_item.get("application_open_date"),
            "application_deadline": validated_item.get("application_deadline"),
            "source_url": validated_item["source_url"] or self.source_url,
            "verification_status": "verified" if self.source_instance.is_verified else "unverified",
            "last_checked_at": timezone.now(),
        }

        if existing_instance:
            for k, v in defaults.items():
                setattr(existing_instance, k, v)
            existing_instance.save()
            self.items_updated += 1
            job = existing_instance
        else:
            job = Job.objects.create(
                title=validated_item["title"],
                company=company,
                external_id=validated_item.get("external_id", ""),
                application_url=validated_item["application_url"],
                **defaults
            )
            self.items_created += 1

        # Link skills if provided
        for sk_name in validated_item.get("skills", []):
            skill, _ = Skill.objects.get_or_create(name=sk_name.strip())
            JobSkill.objects.get_or_create(job=job, skill=skill, defaults={"is_mandatory": True})

        return job

    def run_with_logging(self) -> ScrapingLog:
        """
        Executes collector pipeline and records run telemetry to ScrapingLog.
        """
        start_time = time.time()
        log = ScrapingLog.objects.create(source=self.source_instance, status="started")
        try:
            results = self.run()
            duration = time.time() - start_time
            log.status = "success"
            log.items_fetched = results["fetched"]
            log.items_created = results["created"]
            log.items_updated = results["updated"]
            log.items_skipped = results["skipped"]
            log.duration_seconds = round(duration, 2)
            log.save()

            self.source_instance.total_jobs_collected += results["created"]
            self.source_instance.last_checked_at = timezone.now()
            self.source_instance.status = "active"
            self.source_instance.save()
        except Exception as exc:
            duration = time.time() - start_time
            log.status = "failed"
            log.duration_seconds = round(duration, 2)
            log.error_message = str(exc)
            log.save()

            self.source_instance.error_count += 1
            self.source_instance.status = "failing" if self.source_instance.error_count > 3 else "degraded"
            self.source_instance.save()
            raise

        return log
