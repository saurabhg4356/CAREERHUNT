"""
RSS and Atom Syndication Feed Collector for CareerHunt.
Consumes standard career feeds, job board RSS, and notification channels.
"""
import time
import feedparser
from datetime import datetime
from typing import Any, Dict, List, Optional
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


class RssFeedCollector(BaseCollector):
    """
    Syndication feed collector processing RSS 2.0 and Atom feeds.
    """

    def __init__(self, source_instance: JobSource, feed_url: Optional[str] = None):
        super().__init__(
            source_name=source_instance.name,
            source_type=source_instance.source_type,
            source_url=feed_url or source_instance.source_url,
        )
        self.source_instance = source_instance

    def fetch(self) -> Any:
        feed = feedparser.parse(self.source_url)
        if getattr(feed, "bozo", 0) and not feed.entries:
            raise ValueError(f"Failed to parse syndication feed from {self.source_url}: {getattr(feed, 'bozo_exception', 'Unknown')}")
        return feed

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        items = []
        for entry in getattr(raw_data, "entries", []):
            title = entry.get("title", "")
            link = entry.get("link", "")
            description = entry.get("summary", "") or entry.get("description", "")
            
            # Extract author/company if present, otherwise default to source name
            company_name = entry.get("author") or self.source_name.split()[0]
            
            # Parse published date
            published_dt = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_dt = timezone.make_aware(
                    datetime(*entry.published_parsed[:6])
                )

            items.append({
                "title": title,
                "company_name": company_name,
                "external_id": entry.get("id") or link,
                "source_url": link,
                "application_url": link,
                "description": description,
                "location_name": "Remote",
                "posted_at": published_dt or timezone.now(),
            })
        return items

    def normalize(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        return normalize_opportunity(raw_item)

    def validate(self, normalized_item: Dict[str, Any]) -> bool:
        valid, _ = validate_opportunity(normalized_item)
        return valid

    def deduplicate(self, validated_item: Dict[str, Any]) -> Optional[Job]:
        return deduplicate_opportunity(self.source_instance, validated_item)

    def save(self, validated_item: Dict[str, Any], existing_instance: Optional[Job] = None) -> Job:
        company, _ = Company.objects.get_or_create(
            name=validated_item["company_name"],
            defaults={"is_verified": self.source_instance.is_verified}
        )

        defaults = {
            "source": self.source_instance,
            "category": None,
            "description": validated_item["description"] or f"Opportunity at {company.name}",
            "opportunity_type": validated_item["opportunity_type"],
            "experience_level": validated_item["experience_level"],
            "remote_type": validated_item["remote_type"],
            "location_name": validated_item["location_name"],
            "source_url": validated_item["source_url"],
            "verification_status": "verified" if self.source_instance.is_verified else "unverified",
            "last_checked_at": timezone.now(),
        }

        if existing_instance:
            for k, v in defaults.items():
                setattr(existing_instance, k, v)
            existing_instance.save()
            self.items_updated += 1
            return existing_instance
        else:
            job = Job.objects.create(
                title=validated_item["title"],
                company=company,
                external_id=validated_item.get("external_id", ""),
                application_url=validated_item["application_url"],
                **defaults
            )
            self.items_created += 1
            return job

    def run_with_logging(self) -> ScrapingLog:
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
            self.source_instance.save()
            raise

        return log
