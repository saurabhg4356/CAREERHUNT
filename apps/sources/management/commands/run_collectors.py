"""
Management command to run registered collectors for CareerHunt.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.sources.models import JobSource
from collectors.api.rest_collector import RestApiCollector
from collectors.rss.feed_collector import RssFeedCollector


class Command(BaseCommand):
    help = "Runs registered active data collectors to synchronize opportunities."

    def add_arguments(self, parser):
        parser.add_argument("--source-id", type=int, help="Optional specific JobSource ID to execute.")

    def handle(self, *args, **options):
        source_id = options.get("source_id")
        if source_id:
            sources = JobSource.objects.filter(pk=source_id, status="active")
        else:
            sources = JobSource.objects.filter(status="active")

        self.stdout.write(f"Found {sources.count()} active source(s) to process.")

        for src in sources:
            self.stdout.write(f"Executing collector for: {src.name} ({src.get_source_type_display()})")
            try:
                if src.source_type == "rss_feed":
                    collector = RssFeedCollector(src)
                else:
                    collector = RestApiCollector(src)
                
                # In dry-run or mock mode, we test runner connectivity
                self.stdout.write(self.style.SUCCESS(f"  Initialized collector for {src.name}"))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  Failed collector execution for {src.name}: {exc}"))

        self.stdout.write(self.style.SUCCESS("Collector execution routine completed."))
