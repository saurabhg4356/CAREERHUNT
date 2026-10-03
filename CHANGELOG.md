# Changelog — CareerHunt

All notable changes to the CareerHunt platform are documented in this file.

---

## [1.0.0] - 2026-10-03 (Stages 1 – 20 Complete)

### Added
- **Core Architecture (Stage 1)**: Modular Django 5.2+ architecture with split settings (`base.py`, `local.py`, `production.py`), WhiteNoise static file integration, health check endpoint at `/health/`, and custom error handlers (`404.html`, `500.html`, `403.html`).
- **Database & Schema Design (Stage 2)**: Core domain models (`Company`, `JobSource`, `ScrapingLog`, `Category`, `Skill`, `Job`, `JobSkill`) with composite indexing, dynamic status updates (`active`, `upcoming`, `closing-soon`, `expired`), and custom `JobQuerySet`.
- **Candidate Accounts & Profiles (Stage 3)**: User registration, authentication, candidate profile creation signal, education credentials management, and skill taxonomy assignment.
- **Job Exploration & Company Directory (Stages 4, 5, 6)**: Multi-keyword search, faceted filtering (opportunity type, experience level, remote mode, location, category, deadline window), query-preserving pagination, direct destination links, and company profile views.
- **Collector Architecture & Deduplication (Stages 7, 8, 9)**: Provenance-preserving collector pipeline with URL canonicalization (stripping tracking parameters), deterministic 3-tier deduplication, `RestApiCollector`, `RssFeedCollector`, `run_collectors` management command, and `/sources/` public directory.
- **Candidate Productivity Tools (Stages 10, 11, 12)**:
  - 1-click opportunity bookmarking with `/jobs/saved/` dashboard.
  - Kanban-style visual Application Tracker (`/applications/`) across 7 lifecycle stages (`Applied`, `Assessment`, `Interview`, `Offer`, `Rejected`, `Saved`, `Withdrawn`).
  - Transparent rule-based CareerHunt Match Score (%) engine and side-by-side skill gap comparison.
- **Notifications, Alerts & Moderation (Stages 13, 14, 15)**: In-app notification center, search alerts, crowdsourced listing issue reporting, and staff-only Admin Telemetry & Moderation Dashboard (`/dashboard/`).
- **Resume Parsing & Entity Extraction (Stage 16)**: Resume text and document extraction, taxonomy matching, experience estimation, opportunity fit scoring, and 1-click skill import into candidate profile.
- **REST API Layer (Stage 17)**: Full DRF REST API v1 (`/api/v1/jobs/`, `/companies/`, `/sources/`, `/skills/`, `/categories/`, `/saved-jobs/`, `/applications/`, `/alerts/`, `/reports/`) with pagination, filtering, and search.
- **Security Hardening (Stage 18)**: HTTP security headers (`X-Frame-Options: DENY`, `nosniff`), CSRF verification on all state-changing endpoints, strict candidate data isolation preventing IDOR, and staff RBAC enforcement.
- **Performance Optimization (Stage 19)**: Query profiling, complete N+1 query elimination via `select_related` and `prefetch_related("skills")`, and composite database indexes.
- **Production Readiness & Documentation (Stage 20)**: Static asset collection verified via WhiteNoise (`156 static files`), comprehensive documentation (`API.md`, `SECURITY.md`, `SCRAPING.md`, `TESTING.md`, `FEATURES.md`), and automated test suite with 52/52 passing tests.
