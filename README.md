# CareerHunt

> **"Discover verified job and internship opportunities from identifiable sources."**

CareerHunt is a production-grade Job & Internship Discovery and Aggregation Platform architected specifically for undergraduate students, fresh graduates, and entry-level candidates.

---

## 🌟 Core Highlights & Capabilities

- **100% Identifiable Source Provenance**: Every opportunity visibly attributes its verifying origin source, source type, collection timestamp, and direct destination link to the employer's official careers portal.
- **Dedicated Student & Fresher Discovery**: Dedicated search filters and portals for student internships (`/jobs/internships/`) and upcoming openings with days countdowns (`/jobs/upcoming/`).
- **Faceted Multi-Keyword Search**: Live multi-faceted filtering across role types, experience level, remote modes, location names, and career categories with query-preserving pagination.
- **Transparent Match Score Engine**: Transparent, rule-based algorithmic scoring (0–100%) showing exact percentage breakdown:
  - Skill coverage (45% weight)
  - Experience alignment (25% weight)
  - Preferred workplace mode (15% weight)
  - Target location match (15% weight)
- **Side-by-Side Skill Gap Analysis**: Clear visual inventory of possessed versus missing skills for any target opportunity.
- **Resume Parsing & Entity Extraction**: Paste resume text or upload documents to discover technical skills matching the CareerHunt taxonomy, estimate experience level, and import detected skills with one click into candidate profiles.
- **Visual Application Tracker**: Kanban-style candidate tracker managing applications across 7 lifecycle stages (`Applied`, `Assessment`, `Interview`, `Offer`, `Rejected`, `Saved`, `Withdrawn`), complete with interview schedules and personal notes.
- **Pluggable Data Collectors & Deduplication**: Standardized collector architecture (`BaseCollector`, `RestApiCollector`, `RssFeedCollector`) with URL canonicalization (stripping tracking parameters) and deterministic 3-tier deduplication.
- **Trust & Moderation System**: Candidate crowdsourced listing report submission (`/reports/`) and staff-only Admin Telemetry & Moderation Dashboard (`/dashboard/`).
- **Complete REST API v1**: Built on Django REST Framework with full endpoints under `/api/v1/`, filtering, search, and rate limiting.

---

## 🏗️ Technology Stack

- **Backend**: Python 3.13, Django 5.2+, Django REST Framework 3.18+
- **Frontend**: Semantic HTML5, CSS3, Plus Jakarta Sans design system, Vanilla JS, WhiteNoise
- **Database**: SQLite (development) / PostgreSQL (production) with composite indexes
- **Ingestion**: Requests, BeautifulSoup4, Feedparser
- **Testing**: Pytest, pytest-django (52 automated tests, 100% green)

---

## 📚 Technical Documentation

Explore the comprehensive project documentation in [`docs/`](file:///c:/CAREERHUNT/docs/):
- 📘 [Requirements Specification (`docs/REQUIREMENTS.md`)](file:///c:/CAREERHUNT/docs/REQUIREMENTS.md)
- 🏛️ [System Architecture & Components (`docs/ARCHITECTURE.md`)](file:///c:/CAREERHUNT/docs/ARCHITECTURE.md)
- 🗄️ [Database Schema & ERD (`docs/DATABASE.md`)](file:///c:/CAREERHUNT/docs/DATABASE.md)
- 🔌 [REST API Specification (`docs/API.md`)](file:///c:/CAREERHUNT/docs/API.md)
- 🛡️ [Security Architecture & Hardening (`docs/SECURITY.md`)](file:///c:/CAREERHUNT/docs/SECURITY.md)
- 🕷️ [Collector Architecture & Deduplication (`docs/SCRAPING.md`)](file:///c:/CAREERHUNT/docs/SCRAPING.md)
- 🧪 [Testing Architecture & Coverage Matrix (`docs/TESTING.md`)](file:///c:/CAREERHUNT/docs/TESTING.md)
- ✨ [Platform Features Matrix (`docs/FEATURES.md`)](file:///c:/CAREERHUNT/docs/FEATURES.md)
- 🗺️ [Development Roadmap & Stage Audit (`docs/ROADMAP.md`)](file:///c:/CAREERHUNT/docs/ROADMAP.md)
- 📦 [Dependencies & Environment (`docs/DEPENDENCIES.md`)](file:///c:/CAREERHUNT/docs/DEPENDENCIES.md)
- 📋 [Release Changelog (`CHANGELOG.md`)](file:///c:/CAREERHUNT/CHANGELOG.md)

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.13+
- Git

### 2. Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/saurabhg4356/CAREERHUNT.git
cd CAREERHUNT

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

### 5. Apply Migrations & Seed Demo Data
```bash
python manage.py migrate
python manage.py seed_demo_data
```

### 6. Run Data Collectors (Optional)
```bash
python manage.py run_collectors
```

### 7. Run Test Suite
```bash
pytest
```
*Executes all 52 tests across Stages 1 through 20.*

### 8. Start Development Server
```bash
python manage.py runserver
```

Visit the application at:
- **Web App**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **REST API Browser**: [http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)
- **Admin Dashboard**: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/) (requires staff login)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 📊 Development Status: All 20 Stages Complete (100%)

All 20 stages have been implemented, tested, verified, and pushed to the official repository:
- ✅ **Stage 1**: Project Architecture & Setup
- ✅ **Stage 2**: Database Schema, Models & Composite Indexes
- ✅ **Stage 3**: Candidate Authentication, Profiles & Education
- ✅ **Stage 4**: Job, Internship & Company Management
- ✅ **Stage 5**: Frontend Layout & Plus Jakarta Sans Design System
- ✅ **Stage 6**: Multi-Keyword Search & Faceted Filtering
- ✅ **Stage 7**: Source Transparency & Health Status
- ✅ **Stage 8**: Extensible Collector Architecture (API & RSS)
- ✅ **Stage 9**: Canonicalization & 3-Tier Deduplication
- ✅ **Stage 10**: Saved Opportunities & Bookmarking
- ✅ **Stage 11**: Visual Application Tracker Pipeline
- ✅ **Stage 12**: Match Score Engine & Skill Gap Analysis
- ✅ **Stage 13**: Search Alerts & In-App Notification Center
- ✅ **Stage 14**: Crowdsourced Listing Issue Reports
- ✅ **Stage 15**: Staff Moderation & Telemetry Dashboard
- ✅ **Stage 16**: Resume Parsing & Entity Skill Extraction
- ✅ **Stage 17**: Django REST Framework API Layer (v1)
- ✅ **Stage 18**: Security Hardening & IDOR Prevention
- ✅ **Stage 19**: Query Profiling & N+1 Query Elimination
- ✅ **Stage 20**: Production Readiness, WhiteNoise & Full Documentation
