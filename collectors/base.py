"""
Base Collector Interface for CareerHunt.
Every collector must inherit from BaseCollector and implement the ingestion pipeline:
fetch() -> parse() -> normalize() -> validate() -> deduplicate() -> save()
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger("collectors")


class BaseCollector(ABC):
    """
    Abstract base class providing standard lifecycle and helper methods
    for all data collection sources (APIs, RSS feeds, permitted web extracts).
    """

    def __init__(self, source_name: str, source_type: str, source_url: str):
        self.source_name = source_name
        self.source_type = source_type
        self.source_url = source_url
        self.items_fetched = 0
        self.items_created = 0
        self.items_updated = 0
        self.items_skipped = 0

    @abstractmethod
    def fetch(self) -> Any:
        """
        Fetch raw payload from the target source.
        Returns raw response object (dict, string, xml, etc.).
        """
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Extract a list of raw opportunity dictionaries from the raw payload.
        """
        pass

    @abstractmethod
    def normalize(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize dictionary keys and values to CareerHunt standard schema.
        """
        pass

    @abstractmethod
    def validate(self, normalized_item: Dict[str, Any]) -> bool:
        """
        Validate whether the item has all required fields and correct formats.
        Returns True if valid, False otherwise.
        """
        pass

    @abstractmethod
    def deduplicate(self, validated_item: Dict[str, Any]) -> Optional[Any]:
        """
        Check if opportunity already exists in the database.
        Returns existing model instance if found, None otherwise.
        """
        pass

    @abstractmethod
    def save(self, validated_item: Dict[str, Any], existing_instance: Optional[Any] = None) -> Any:
        """
        Persist the opportunity in the database (create or update).
        """
        pass

    def run(self) -> Dict[str, int]:
        """
        Execute the full standard collection pipeline with telemetry.
        """
        logger.info(f"Starting collector for: {self.source_name} ({self.source_type})")
        try:
            raw_data = self.fetch()
            parsed_items = self.parse(raw_data)
            self.items_fetched = len(parsed_items)

            for item in parsed_items:
                try:
                    normalized = self.normalize(item)
                    if not self.validate(normalized):
                        self.items_skipped += 1
                        continue

                    existing = self.deduplicate(normalized)
                    self.save(normalized, existing_instance=existing)
                except Exception as item_err:
                    logger.warning(f"Error processing item in {self.source_name}: {item_err}")
                    self.items_skipped += 1

            logger.info(
                f"Completed collector run for {self.source_name}. "
                f"Fetched: {self.items_fetched}, Created: {self.items_created}, "
                f"Updated: {self.items_updated}, Skipped: {self.items_skipped}"
            )
        except Exception as exc:
            logger.error(f"Collector failure in {self.source_name}: {exc}", exc_info=True)
            raise

        return {
            "fetched": self.items_fetched,
            "created": self.items_created,
            "updated": self.items_updated,
            "skipped": self.items_skipped,
        }
