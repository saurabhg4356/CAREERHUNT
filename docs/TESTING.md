# CareerHunt — Testing Architecture & Verification Guide

## Overview
CareerHunt includes a comprehensive automated test suite consisting of **52 unit, integration, and security test cases** covering every developmental stage from foundational setup to production security and query profiling.

---

## 1. Test Suite Breakdown by Stage

| Test File | Stages Covered | Test Count | Key Verification Objectives |
|-----------|----------------|------------|-----------------------------|
| `test_stage1_setup.py` | Stage 1 | 4 | Homepage loading, custom 404/500/403 handlers, health check endpoint. |
| `test_stage2_models.py` | Stage 2 | 5 | Company, JobSource, Job, JobSkill entities, custom QuerySets (`active`, `upcoming`, `closing_soon`, `internships`, `freshers`), deadline countdown calculations. |
| `test_stage3_auth.py` | Stage 3 | 6 | Candidate registration, login/logout, profile auto-creation signal, education CRUD, and skill management. |
| `test_stage4_5_6_jobs_search.py` | Stages 4, 5, 6 | 6 | Multi-keyword search, faceted filtering (type, exp, mode, location, category), sorting, pagination, provenance cards, direct application links, company profiles. |
| `test_stage7_8_9_collectors_dedupe.py` | Stages 7, 8, 9 | 5 | URL canonicalization (stripping UTM/ref params), normalization, multi-tier deduplication, collector pipeline execution, audit log creation, and source transparency directory. |
| `test_stage10_11_12_user_features.py` | Stages 10, 11, 12 | 4 | Bookmark toggle & saved jobs listing, application tracker lifecycle (applied, interview, offer, rejected), rule-based match score engine, and skill gap comparison. |
| `test_stage13_14_15_notifications_reports_dashboard.py` | Stages 13, 14, 15 | 4 | Notifications & mark as read, search alerts CRUD, crowdsourced listing report submission, staff-only admin telemetry dashboard and metrics. |
| `test_stage16_resume.py` | Stage 16 | 4 | Resume parsing, skill taxonomy extraction, experience estimation, resume matcher view, and 1-click skill import into candidate profile. |
| `test_stage17_api.py` | Stage 17 | 7 | DRF REST API v1 endpoints (`/api/v1/jobs/`, `/companies/`, `/sources/`, `/saved-jobs/`, `/applications/`, `/alerts/`, `/reports/`), serializer validations, permissions, and query filtering. |
| `test_stage18_19_security_performance.py` | Stages 18 & 19 | 7 | HTTP security headers (`X-Frame-Options: DENY`, `nosniff`), IDOR prevention on applications/education, unauthenticated protected route redirection, admin RBAC, model composite index verification, and query profiling (preventing N+1 queries). |
| **Total** | **Stages 1 – 20** | **52 tests** | **100% Passing** |

---

## 2. Running the Test Suite

### Run All Tests
```bash
# Using pytest
pytest

# Verbose output with timing
pytest -v --durations=10
```

### Run Tests for Specific Stages
```bash
# Run API tests
pytest tests/test_stage17_api.py

# Run Security & Performance tests
pytest tests/test_stage18_19_security_performance.py

# Run Search & Filtering tests
pytest tests/test_stage4_5_6_jobs_search.py
```

### Run with Django's Test Runner
```bash
python manage.py test tests
```
