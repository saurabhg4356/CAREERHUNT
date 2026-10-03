# CareerHunt — System Architecture & Design

## 1. Architectural Philosophy
CareerHunt is designed with a **modular monolith** architecture using Python 3.13, Django 5.1+, and Django REST Framework. The system prioritizes:
- **Separation of Concerns:** Clear application boundaries (`accounts`, `jobs`, `companies`, `sources`, `applications`, `recommendations`, `notifications`, `reports`, `dashboard`, `api`, `core`).
- **Data Provenance & Traceability:** Every opportunity links back to its verified source with clear status, timestamp, and unaltered destination URL.
- **Pluggable Ingestion Pipeline:** Decoupled collectors (`collectors/`) with standardized stages (`fetch -> parse -> normalize -> validate -> deduplicate -> save`).
- **Dual Presentation Layer:** Server-rendered responsive HTML views with Tailwind/Bootstrap utilities for primary web users, coupled with a RESTful API for programmatic access and frontend interactivity.

---

## 2. High-Level System Architecture Diagram

```mermaid
graph TD
    subgraph Clients
        WebBrowser["Web Browser (Responsive UI)"]
        APIClient["API Clients / Future Mobile"]
    end

    subgraph Presentation & Routing
        WebSvr["Web Server / WSGI / ASGI"]
        Middleware["Django Middleware (CSRF, Auth, Security, Logging)"]
        Router["URL Routing"]
    end

    subgraph Applications Layer
        AppCore["apps.core (Base Models, Helpers)"]
        AppAuth["apps.accounts (Auth & Profiles)"]
        AppJobs["apps.jobs (Jobs, Skills, Taxonomy)"]
        AppComp["apps.companies (Company Profiles)"]
        AppSrc["apps.sources (Job Sources & Verification)"]
        AppApps["apps.applications (Application Tracker)"]
        AppRec["apps.recommendations (Rule-based Match Engine)"]
        AppNotif["apps.notifications (In-app Alerts)"]
        AppRep["apps.reports (User Listing Reports)"]
        AppDash["apps.dashboard (Admin Analytics & Metrics)"]
        AppAPI["apps.api (REST Framework Endpoints)"]
    end

    subgraph Data Collection Subsystem
        CollectorRunner["Collector Orchestrator / Management Commands"]
        CollectorBase["collectors.base.BaseCollector"]
        APICollector["collectors.api (Official APIs)"]
        RSSCollector["collectors.rss (RSS/Atom Feeds)"]
        WebCollector["collectors.web (Permitted Public Extraction)"]
        ValDedupe["Validation & Deduplication Engine"]
    end

    subgraph Persistence & Storage
        DB[("PostgreSQL / SQLite Database")]
        StaticMedia[("Static & Media Storage")]
        AuditLogs[("Collector & System Logs")]
    end

    WebBrowser --> WebSvr
    APIClient --> WebSvr
    WebSvr --> Middleware
    Middleware --> Router
    Router --> Applications Layer

    CollectorRunner --> CollectorBase
    CollectorBase --> APICollector
    CollectorBase --> RSSCollector
    CollectorBase --> WebCollector
    APICollector --> ValDedupe
    RSSCollector --> ValDedupe
    WebCollector --> ValDedupe
    ValDedupe --> AppJobs
    ValDedupe --> AppSrc

    Applications Layer --> DB
    Applications Layer --> StaticMedia
    CollectorRunner --> AuditLogs
```

---

## 3. Directory & Module Structure

```text
c:\CAREERHUNT/
│
├── .venv/                         # Python virtual environment
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── manage.py                      # Django CLI management entry point
├── requirements.txt               # Pinned project dependencies
├── README.md                      # Primary project readme
├── CHANGELOG.md                   # Chronological project changelog
│
├── config/                        # Project configuration root
│   ├── __init__.py
│   ├── asgi.py                    # ASGI deployment entry point
│   ├── wsgi.py                    # WSGI deployment entry point
│   ├── urls.py                    # Master URL routing table
│   └── settings/                  # Environment-specific settings
│       ├── __init__.py
│       ├── base.py                # Shared base settings
│       ├── local.py               # Development settings (SQLite/debug)
│       └── production.py          # Production settings (PostgreSQL/hardened security)
│
├── apps/                          # Modular Django application domain packages
│   ├── __init__.py
│   ├── core/                      # Abstract base models, timestamps, utility helpers
│   ├── accounts/                  # User, UserProfile, Education, Skills, Preferences
│   ├── jobs/                      # Job, Category, Skill, JobSkill, SavedJob
│   ├── companies/                 # Company entity, industry, verified status
│   ├── sources/                   # JobSource, ScrapingLog / CollectorLog
│   ├── applications/              # Application, ApplicationStatus, Notes
│   ├── recommendations/           # CareerHunt Match Engine, Skill Gap Analysis
│   ├── notifications/             # In-App Notification, JobAlert
│   ├── reports/                   # Listing Report entity, Admin resolution
│   ├── dashboard/                 # Admin Dashboard views, analytics & telemetry
│   └── api/                       # DRF Serializers, ViewSets, API Routing
│
├── collectors/                    # Standalone, pluggable data collection subsystem
│   ├── __init__.py
│   ├── base.py                    # Abstract BaseCollector class with lifecycle hooks
│   ├── pipeline.py                # Standardization, normalization, deduplication pipeline
│   ├── api/                       # Collectors consuming REST/JSON endpoints
│   ├── rss/                       # Collectors consuming RSS/Atom XML feeds
│   └── web/                       # Permitted, polite public extractors
│
├── templates/                     # Global HTML templates
│   ├── base.html                  # Master layout with navbar, footer, toast container
│   ├── includes/                  # Partials (navbar, footer, job_card, alerts, pagination)
│   ├── errors/                    # Friendly 404, 500, 403 pages
│   ├── accounts/                  # Profile, login, registration, preferences
│   ├── jobs/                      # Listing, detail, upcoming, search, filter
│   ├── applications/              # Application tracker board/table
│   ├── recommendations/           # Match cards and skill gap breakdowns
│   └── dashboard/                 # Admin charts, source health, report queues
│
├── static/                        # Static assets
│   ├── css/                       # Custom design system & tailwind/bootstrap utilities
│   ├── js/                        # Interactive client scripts (filtering, search, toasts)
│   └── images/                    # Logos, badges, fallback illustrations
│
├── media/                         # Uploaded files (company logos, resumes if permitted)
├── tests/                         # End-to-end and integration test suites
└── docs/                          # Architecture, DB, API, and Deployment documentation
```

---

## 4. Ingestion & Collector Pipeline

Every collector implements `collectors.base.BaseCollector` and follows a deterministic lifecycle:

```text
[ Trigger: Management Command / Celery Task ]
                   │
                   ▼
       1. fetch()  ──► Retrieves raw payload (JSON, XML, or HTML) with timeout & retries
                   │
                   ▼
       2. parse()  ──► Extracts raw dictionary items from raw payload
                   │
                   ▼
   3. normalize()  ──► Standardizes dates, cleans strings, maps categories, currency
                   │
                   ▼
    4. validate()  ──► Enforces non-null title, valid application URL, minimum fields
                   │
                   ▼
  5. deduplicate() ──► Checks existing external_id, application_url, and (company, title)
                   │
                   ▼
        6. save()  ──► Atomically inserts/updates Job & JobSource records
                   │
                   ▼
      7. log_run() ──► Writes execution telemetry to ScrapingLog
```

---

## 5. Security Architecture
1. **Zero Secret Leaks:** All sensitive credentials loaded exclusively via environment variables (`django-environ`).
2. **Defensive Input Handling:** Every user input cleaned and escaped. Search terms parameterized via Django ORM.
3. **No Destination Masking:** Job application links point directly to the verifiable employer or official board URL.
4. **Controlled Data Ingestion:** Collectors reject unverified sources, invalid schemes, and sanitize raw HTML descriptions to avoid stored XSS.
