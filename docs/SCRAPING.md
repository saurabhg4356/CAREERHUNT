# CareerHunt — Collector Architecture & Data Ingestion Specification

## Philosophy & Guiding Rules
CareerHunt aggregates employment and internship opportunities specifically for students and freshers. To ensure absolute platform trustworthiness:
1. **Never hide the original destination URL**: Candidates must always have direct, transparent access to the actual employer application page.
2. **Preserve provenance**: Every opportunity must identify its origin source, source type, timestamp of collection, and verification status.
3. **Respect source robots.txt and politeness**: Crawlers identify themselves using `COLLECTOR_USER_AGENT` (`CareerHuntBot/1.0 (+https://careerhunt.example.com/bot)`), obey timeout settings, and observe concurrency limits.

---

## 1. Ingestion Pipeline (`collectors/pipeline.py`)

Every ingested opportunity item passes through a 4-tier deterministic pipeline:

```
Raw Data Ingestion
      │
      ▼
1. URL Canonicalization & Normalization
   - Lowercase scheme and domain
   - Strip marketing parameters (utm_*, ref, gclid, fbclid)
   - Remove fragments (#...) and normalize trailing slashes
      │
      ▼
2. Schema Validation
   - Required fields: title, company_name, source_url, application_url
   - Choice validation: opportunity_type, experience_level, remote_type
      │
      ▼
3. Deterministic Deduplication
   - Tier 1: Canonical Application URL match
   - Tier 2: (Company ID, External ID) composite match
   - Tier 3: (Company ID, normalized lowercase title) match
      │
      ▼
4. Database Persistence & Skill Association
   - Get or create Company & Source
   - Match extracted skill tokens against DB taxonomy
   - Link JobSkill relationships (mandatory vs optional)
   - Record ScrapingLog telemetry
```

---

## 2. Collector Classes

### `BaseCollector` (`collectors/base.py`)
Abstract base class defining the standard interface for all opportunity adapters:
- `fetch_raw()`: Fetches raw content with timeouts and exponential backoff retry.
- `parse_items(raw_data)`: Extracts structured item dictionaries.
- `run()`: Executes ingestion, records execution duration, error counts, and creates an audit `ScrapingLog` record.

### `RestApiCollector` (`collectors/api/base_api.py`)
Handles JSON-based web APIs:
- Configurable headers, bearer tokens, or query parameters.
- Automatic pagination traversal until exhaustion or threshold limit.

### `RssFeedCollector` (`collectors/rss/feed_collector.py`)
Handles RSS 2.0 and Atom feeds:
- Parses feed entries using `feedparser`.
- Extracts publication timestamps, summary descriptions, and direct links.

---

## 3. Running Data Collectors

Execute collectors via the Django management command:
```bash
# Run all active collectors
python manage.py run_collectors

# Run a specific collector by name
python manage.py run_collectors --source="Official Acme Careers"
```
Telemetry logs and error reports are viewable live in the Staff Telemetry Dashboard at `/dashboard/`.
