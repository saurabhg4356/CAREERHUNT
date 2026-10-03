# CareerHunt — Platform Feature Matrix

CareerHunt is built from the ground up for students, freshers, and entry-level job seekers with verified opportunity authenticity and full source provenance.

---

## 1. Public Discovery & Search (Guest & Candidate)
- **Faceted Job Search**: Filter simultaneously across Opportunity Type (Internship, Full-time, etc.), Experience Level (Fresher, 0-1, 1-2, 2+), Remote Workplace Mode (Remote, Hybrid, On-site), City/Location, and Career Category.
- **Multi-Keyword Search**: Case-insensitive substring and tokenized search across job title, description text, company name, location, and required skills.
- **Dedicated Portals**:
  - `/jobs/internships/`: Curated internships for undergraduates and fresh graduates.
  - `/jobs/upcoming/`: Pipeline of campus and corporate programs opening in future weeks with days countdown.
- **Authentic Provenance Cards**: Every listing card visibly identifies the verifying origin source, last checked timestamp, deadline countdown, and a direct link to the employer's official destination application portal.
- **Employer Directory**: Dedicated profiles for companies showcasing industry, location, verified credentials, and active job listings.
- **Source Transparency Directory**: Public directory at `/sources/` listing all verified data feeds and collectors with health telemetry.

---

## 2. Candidate Tools & Workflows (Authenticated)
- **Candidate Profiles**: Personal headline, contact information, career preferences, target roles, preferred cities, and salary expectations.
- **Education Credentials**: Academic history with institution, degree, start/end graduation years, and CGPA/grade tracking.
- **Skill Inventory**: Skill taxonomy mapping with self-assessed proficiency levels (Beginner, Intermediate, Advanced).
- **Opportunity Bookmarking**: 1-click save/unsave toggle with instant AJAX feedback and a dedicated Saved Jobs dashboard.
- **Application Tracker Pipeline**: Visual kanban-style application tracker managing opportunities across 7 lifecycle stages (`Applied`, `Assessment`, `Interview`, `Offer`, `Rejected`, `Saved`, `Withdrawn`), complete with interview schedules and personal notes.
- **CareerHunt Match Score Engine**: Transparent, rule-based algorithmic scoring (0–100%) showing exact percentage breakdown:
  - Skill coverage (45% weight)
  - Experience alignment (25% weight)
  - Preferred workplace mode (15% weight)
  - Target location match (15% weight)
- **Skill Gap Analysis**: Side-by-side comparison identifying exactly which required skills the candidate possesses versus skills they need to learn for a specific opportunity.
- **Resume Parsing & Entity Extraction**: Paste resume text or upload a document to automatically identify technical skills matching the database taxonomy, estimate candidate experience, view instant opportunity match scores, and import extracted skills directly into the profile with one click.
- **Opportunity Search Alerts**: Automated alerts tracking user-defined keyword, location, and opportunity type filters with daily/weekly cadence.
- **Notification Inbox**: Alerts candidates when saved opportunities are approaching deadline or when new matching roles are aggregated.
- **Listing Issue Reports**: Candidates can report fraudulent, expired, or suspicious listings directly from any opportunity page.

---

## 3. Administrative & Staff Moderation (Staff Only)
- **Moderation & Telemetry Dashboard (`/dashboard/`)**:
  - Live system metric cards (Total Opportunities, Active Listings, Verified Employers, Registered Candidates, Pending Reports).
  - Opportunity distribution breakdowns by type and experience level.
  - Collector pipeline health telemetry table showing source status, last checked timestamps, items collected, and error counts.
  - Pending crowdsourced listing report queue with 1-click status resolution.
  - Top 10 most demanded industry skills in active listings to guide educational curriculum.

---

## 4. API & Integration Layer
- **DRF REST API v1**: Complete endpoints under `/api/v1/` for jobs, employers, sources, skills, categories, saved jobs, applications, alerts, and reports.
- **Throttling & Rate-Limiting**: IP-based and user-based throttling preventing scraping abuse.
- **Direct Link Guarantee**: Every API payload exposes the authentic `application_url` and `source_url`.
