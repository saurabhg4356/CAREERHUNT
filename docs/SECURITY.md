# CareerHunt — Security Architecture & Hardening Guide

## Overview
CareerHunt handles candidate educational backgrounds, job application histories, and verified employer provenance. Security is embedded at every layer to protect candidate privacy and platform integrity.

---

## 1. Authentication & Authorization

### Session & Cookie Security
- `SESSION_COOKIE_HTTPONLY = True`: Prevents client-side scripts from accessing session tokens.
- `CSRF_COOKIE_HTTPONLY = True` & `CsrfViewMiddleware`: Enforces CSRF token validation on every state-changing HTTP method (`POST`, `PUT`, `PATCH`, `DELETE`).
- `X_FRAME_OPTIONS = "DENY"`: Defends against Clickjacking and iframe embedding attacks.
- `SECURE_CONTENT_TYPE_NOSNIFF = True`: Prevents browser MIME-sniffing exploits.

### Role-Based Access Controls (RBAC)
- **Anonymous Guests**: Allowed read-only access to active opportunity listings, company profiles, source provenance, and skill taxonomy.
- **Candidates**: Authenticated users who manage their personal profile, education credentials, skills, resume matching, saved bookmarks, and application tracking pipeline.
- **Staff / Moderators**: Superusers and staff members who access the admin moderation console at `/dashboard/` to investigate user listing reports, audit scraping telemetry, and resolve anomalies.

### Insecure Direct Object Reference (IDOR) Mitigation
Candidate objects are strictly scoped to the authenticated user across all endpoints:
- Applications: `Application.objects.filter(user=request.user, pk=pk)`
- Saved Jobs: `SavedJob.objects.filter(user=request.user, pk=pk)`
- Education: `UserEducation.objects.filter(profile=request.user.profile, pk=pk)`
- Skills: `UserSkill.objects.filter(profile=request.user.profile, pk=pk)`
Attempted access by another user returns an HTTP `404 Not Found`, completely leaking no object existence or state.

---

## 2. Injection & Input Sanitization

### SQL Injection Prevention
- All database interactions use Django's Object-Relational Mapper (ORM) with parameterized queries and bound variables.
- No raw string interpolation or untrusted format strings are allowed in SQL execution.

### Cross-Site Scripting (XSS) Prevention
- Django's template engine automatically HTML-escapes all variable output.
- HTML auto-escaping is never bypassed on user-supplied content.
- Markdown and text content are rendered using safe, text-only filters.

---

## 3. Data Ingestion & Collector Security

- **Direct Destination Links**: Every ingested opportunity preserves and exposes the exact destination link without redirection wrapping, obfuscation, or opaque tracking wrappers.
- **Canonicalization**: Tracking parameters (`utm_*`, `ref`, `fbclid`, `gclid`) are stripped deterministically to prevent cache poisoning and duplicate exploitation.
- **Rate-Limiting & Throttling**: REST API endpoints enforce rate-limiting via DRF Throttles (`100/min` for anonymous clients, `1000/min` for authenticated users) to prevent automated scraping abuse.

---

## 4. Production Deployment Checklist

When deploying CareerHunt to production:
1. `DEBUG = False`: Never run in production with debug mode enabled.
2. `SECRET_KEY`: Set via environment variable from `.env` with at least 50 cryptographically secure pseudo-random characters.
3. `ALLOWED_HOSTS`: Explicitly set to the production domains.
4. `SECURE_SSL_REDIRECT = True`: Enforce TLS 1.3 encryption across all requests.
5. `SECURE_HSTS_SECONDS = 31536000`: Enforce HTTP Strict Transport Security.
6. `SESSION_COOKIE_SECURE = True` & `CSRF_COOKIE_SECURE = True`: Transmit cookies solely via HTTPS.
