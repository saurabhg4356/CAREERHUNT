# CareerHunt — Requirements Specification Document

## 1. Project Overview
**CareerHunt** is a modern, production-grade Job & Internship Discovery and Opportunity Aggregation Platform.
**Tagline:** *"Discover verified job and internship opportunities from identifiable sources."*

### 1.1 Target Audience
- Undergraduate and postgraduate students seeking internships or graduate programs.
- Fresh graduates and entry-level job seekers (0–2 years experience).
- Fresher job seekers looking for authentic, verified openings.
- Job seekers seeking legitimate opportunities with clear attribution and provenance.

### 1.2 Core Value Proposition
CareerHunt aggregates opportunities from identifiable sources (official career pages, approved feeds, official government portals, authorized APIs, and direct company boards). It standardizes, validates, and deduplicates listings, tracks freshness/deadlines, and provides rich search, filtering, bookmarking, application tracking, transparent rule-based recommendations, and report mechanisms.
**Core Policy:** CareerHunt *never* guarantees a listing is 100% genuine without proof; instead, every opportunity displays clear provenance:
- Source Name & Entity Type
- Source URL
- Application Destination URL (never hidden or hijacked)
- Verification Status and Last Checked Timestamp
- Application Opening Date and Deadline (where available)

---

## 2. Functional Requirements

### 2.1 User & Authentication System
- **Registration & Login:** Secure authentication using Django auth system with session-based and token/session API auth.
- **Role-based Access Control:**
  - `Candidate/User`: Standard discovery, profile management, saved jobs, application tracker, alerts, notifications, reports.
  - `Administrator`: Complete system oversight, source verification, collector logs review, user reports resolution, listing management, analytics.
- **Candidate Profile:**
  - Personal Information: Full name, email, phone, location, bio.
  - Education: Degree, college/university, graduation year, CGPA/percentage (optional).
  - Career Preferences: Preferred job types (Internship, Full-time, etc.), preferred work modes (On-site, Remote, Hybrid), preferred locations, expected salary range.
  - Skills: Categorized skill tags (with proficiency level).
  - Experience Level: Fresher, 0-1 years, 1-2 years, 2+ years.

### 2.2 Opportunity Management (Job & Internship)
- **Data Model Attributes:**
  - Title, company, description, opportunity type, employment type, experience level.
  - Location, remote type (On-site, Remote, Hybrid).
  - Salary range (min, max, currency, period).
  - Skills required (many-to-many relationship).
  - Provenance: Source, source URL, application URL, external source ID.
  - Lifecycle: `posted_at`, `application_open_date`, `application_deadline`, `status` (`Upcoming`, `Active`, `Closing Soon`, `Expired`, `Closed`).
  - Verification: `verification_status` (`Verified`, `Pending Review`, `Reported`, `Unverified`), `last_checked_at`.
- **Upcoming Opportunities:** Dedicated section for opportunities with future opening dates (`application_open_date > today`), displaying days countdown until opening.
- **Deadline & Expiry Engine:** Dynamic deadline calculations (`Closing today`, `X days remaining`), automated status transitions to `Closing Soon` (< 3 days) and `Expired` (past deadline) without deleting historical records.

### 2.3 Search & Filtering System
- **Full-Text & Multi-Field Search:** Multi-keyword search across job title, company name, skills, description, location, and category.
- **Faceted Filters:**
  - Opportunity Type: Internship, Full-time, Part-time, Apprenticeship, Graduate Program, Trainee, Contract.
  - Experience Level: Fresher, 0-1 years, 1-2 years, 2+ years.
  - Location & Remote Mode: On-site, Hybrid, Remote (with city-level filtering).
  - Skills: Filter by one or multiple required skills.
  - Freshness/Date Posted: Today, Last 3 days, Last 7 days, Last 30 days.
  - Deadline Window: Closing today, Closing this week, Closing this month.
- **Pagination:** Clean, server-side pagination with query parameter retention.

### 2.4 Data Collection & Collector Architecture
- **Multi-Source Support:**
  - Official APIs (e.g. authorized job board APIs, public feeds).
  - RSS / Atom feeds (e.g. career portals, developer boards).
  - Permitted structured extraction (adhering strictly to robots.txt and terms of service; no bypass of CAPTCHAs, logins, or anti-bot shields).
  - Manual verified entry by platform administrators.
- **Standardized Pipeline:** `fetch() -> parse() -> normalize() -> validate() -> deduplicate() -> save()`.
- **Collector Monitoring:** Detailed audit logging per collector run (`ScrapingLog` / `CollectorLog`), recording status, run duration, items fetched, items created, items updated, errors encountered.

### 2.5 Validation & Deduplication Engine
- **Validation:** Enforces minimum mandatory fields (title, company, application URL, source attribution), sanitizes HTML content, checks URL formats.
- **Deduplication Strategy:** Multi-tiered deterministic matching:
  1. Primary: Exact match on `(source, external_id)`.
  2. Secondary: Normalized `application_url` canonical match.
  3. Tertiary: Exact tuple match `(company_id, normalized_title, location)`.

### 2.6 User Features
- **Saved Jobs:** Toggle bookmarking, view saved listings with active status and deadline alerts.
- **Application Tracker (Kanban / Table):** Track application statuses (`Saved`, `Applied`, `Assessment`, `Interview`, `Offer`, `Rejected`, `Withdrawn`) with personal notes, application date, interview date, and follow-up deadlines.
- **Job Alerts:** Custom alert rules based on keywords, preferred location, job type, and experience level.
- **In-App Notifications:** Alerts for deadline approaching on saved jobs, new matching opportunities, status reminders.
- **Transparent Recommendation Engine:**
  - Computes **CareerHunt Match Score (%)** using explicit, rule-based weighted formula:
    - Skill Match (50% weight)
    - Experience Match (20% weight)
    - Location & Remote Preference Match (20% weight)
    - Job Type Match (10% weight)
  - Detailed Skill Gap Analysis: Shows which required skills the candidate matches vs missing skills.
- **Reporting System:** Users can report suspicious, expired, or inaccurate listings (e.g., fee demands, deceptive links). Admins investigate and resolve reports with direct listing deactivation.

### 2.7 Administration & Source Monitoring
- Dedicated administrative dashboard with high-level system metrics:
  - Total/Active Users, Total/Active Opportunities, Internships, Upcoming Opportunities, Closing Soon, Expired Opportunities.
  - Collector health status, error rates, last successful/failed runs.
  - User reports queue with one-click review, resolution, or listing takedown.
  - Visual charts: Opportunity influx over time, distribution by type, top demanded skills, and source distribution.

### 2.8 REST API
- Built with Django REST Framework (DRF):
  - Job list & details with filtering, search, and ordering.
  - Company list & details.
  - Skill taxonomy endpoints.
  - User saved jobs, application tracker, and alerts endpoints.
  - Recommendations endpoint.
- OpenAPI / Swagger documentation support.

---

## 3. Non-Functional Requirements

### 3.1 Security & Compliance
- Full Django CSRF protection on state-modifying requests.
- Secure password hashing (Argon2 / PBKDF2).
- SQL Injection protection via Django ORM parameterized queries.
- XSS prevention via Django auto-escaping templates and input sanitization.
- Strict input validation on all forms, API serializers, and collector payloads.
- Environment variables isolation (`.env`) for secrets, API keys, and credentials; zero hardcoded secrets.
- Proper Content Security Policy (CSP), HTTP Strict Transport Security (HSTS), and secure cookie flags in production.

### 3.2 Performance & Scalability
- Optimized database indexing on frequently filtered fields (`status`, `opportunity_type`, `experience_level`, `posted_at`, `application_deadline`, `remote_type`).
- Relational query optimization: `select_related` on foreign keys (Company, Category, Source) and `prefetch_related` on M2M relations (Skills).
- Server-side pagination capping per-page allocations.
- Caching layer integration ready (Redis/Database cache) for static taxonomies and aggregated metrics.

### 3.3 Reliability & Error Handling
- Friendly, user-facing error pages (`404.html`, `500.html`, `403.html`).
- Never leak raw stack traces or internal environment variables to users.
- Comprehensive structured logging for authentication, collector runs, database exceptions, and administrative actions.

### 3.4 Responsive Design & Usability
- Primary styling powered by modern CSS3 with Tailwind CSS utility architecture and Bootstrap component patterns.
- Fully responsive across mobile (<640px), tablet (640px-1024px), and desktop (>1024px) viewports.
- WCAG 2.1 AA accessible contrast ratios, focus states, and semantic HTML5 elements.
