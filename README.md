# CareerHunt

> **"Discover verified job and internship opportunities from identifiable sources."**

CareerHunt is a production-oriented Job & Internship Discovery and Opportunity Aggregation Platform specifically designed for undergraduate students, fresh graduates, and entry-level job seekers.

---

## 🌟 Key Capabilities
- **Identifiable Provenance:** Every single opportunity clearly displays its original source, source type, verification status, and direct application destination.
- **Dedicated Opportunity Types:** Internships, Full-time, Apprenticeships, Graduate Programs, and Trainee roles.
- **Freshness & Deadline Intelligence:** Automatic tracking of opening dates, countdowns for upcoming openings, and remaining deadline alerts.
- **Faceted Search & Filtering:** Filter by keyword, skills, location, work mode (On-site, Remote, Hybrid), experience level, and deadline windows.
- **Transparent Recommendation Engine:** Rule-based CareerHunt Match Score (%) with detailed skill gap analysis.
- **Application Tracker:** Personal tracking workflow (Saved, Applied, Interview, Offer, Rejected) with notes and follow-ups.
- **Pluggable Data Collectors:** Standardized, polite ingestion architecture for authorized APIs, RSS/Atom feeds, and permitted sources.
- **Deduplication Engine:** Multi-tiered deterministic matching prevents duplicate listings across sources.
- **Trust & Reporting System:** Direct reporting mechanism for suspicious or expired listings with admin triage.

---

## 🏗️ Architecture & Technology Stack
- **Backend:** Python 3.13, Django 5.1+, Django REST Framework
- **Frontend:** HTML5, CSS3, Tailwind CSS & Bootstrap utility design system, Vanilla JS
- **Database:** SQLite (local development) / PostgreSQL (production)
- **Data Ingestion:** Requests, BeautifulSoup4, Feedparser
- **Testing:** Pytest, Django Test Framework

For in-depth architectural and technical design, refer to the documentation:
- [Architecture & System Design](file:///c:/CAREERHUNT/docs/ARCHITECTURE.md)
- [Requirements Specification](file:///c:/CAREERHUNT/docs/REQUIREMENTS.md)
- [Database Schema & ERD](file:///c:/CAREERHUNT/docs/DATABASE.md)
- [Development Roadmap](file:///c:/CAREERHUNT/docs/ROADMAP.md)
- [Dependencies & Environment](file:///c:/CAREERHUNT/docs/DEPENDENCIES.md)
- [Setup & Quickstart](file:///c:/CAREERHUNT/docs/SETUP.md)

---

## 🚀 Quickstart (Development)

### 1. Prerequisites
- Python 3.13+
- Git

### 2. Setup Virtual Environment
```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows Command Prompt
.venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

### 5. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 📋 Project Status
- **Current Stage:** Stage 1 — Project Setup & Base Architecture (In Progress)
- Refer to [CHANGELOG.md](file:///c:/CAREERHUNT/CHANGELOG.md) for incremental release history.
