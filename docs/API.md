# CareerHunt — REST API Specification (v1)

CareerHunt provides a comprehensive, production-grade RESTful API built on Django REST Framework (DRF).

Base Endpoint:
```
/api/v1/
```

Authentication:
- Session Authentication (`Cookie`-based via login)
- Token / Basic Authentication supported for API integrations
- Rate Limiting: 100 req/min (Anonymous), 1000 req/min (Authenticated)

---

## 1. Opportunities (`/api/v1/jobs/`)

### `GET /api/v1/jobs/`
Retrieves a paginated list of verified active opportunities.

#### Query Parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | String | Multi-keyword search across title, description, skills, and company name. |
| `opportunity_type` | String | Filter by type: `internship`, `full-time`, `part-time`, `apprenticeship`, `graduate-program`. |
| `experience_level` | String | Filter by experience: `fresher`, `0-1`, `1-2`, `2+`. |
| `remote_type` | String | Filter by workplace mode: `remote`, `on-site`, `hybrid`. |
| `category__slug` | String | Filter by career category slug. |
| `company__slug` | String | Filter by hiring employer slug. |
| `ordering` | String | Sort by `posted_at`, `-posted_at`, `application_deadline`, `salary_max`. |
| `page` | Integer | Page number (default page size: 15). |

#### Example Response:
```json
{
  "count": 42,
  "next": "/api/v1/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 14,
      "title": "Junior Python Backend Developer",
      "slug": "junior-python-backend-developer",
      "company": {
        "id": 3,
        "name": "CloudScale Systems",
        "slug": "cloudscale-systems",
        "website": "https://cloudscale.example.com",
        "industry": "Cloud Infrastructure",
        "headquarters": "Bangalore, India",
        "is_verified": true
      },
      "source": {
        "id": 2,
        "name": "Official Careers Portal",
        "source_type": "official_company",
        "source_url": "https://cloudscale.example.com/careers"
      },
      "source_url": "https://cloudscale.example.com/careers/jr-backend",
      "application_url": "https://cloudscale.example.com/careers/jr-backend/apply",
      "opportunity_type": "full-time",
      "experience_level": "fresher",
      "remote_type": "remote",
      "location_name": "Bangalore, India",
      "salary_min": "450000.00",
      "salary_max": "750000.00",
      "salary_currency": "INR",
      "is_salary_disclosed": true,
      "status": "active",
      "verification_status": "verified",
      "deadline_display": "5 days remaining",
      "skills": [
        {"id": 1, "name": "Python", "slug": "python", "category_name": "Software Engineering"},
        {"id": 4, "name": "Django", "slug": "django", "category_name": "Software Engineering"}
      ]
    }
  ]
}
```

### `GET /api/v1/jobs/<id>/`
Retrieves detailed opportunity information, including complete descriptions, requirements, and provenance audit metadata.

### `GET /api/v1/jobs/internships/`
Shortcut endpoint returning active student and fresher internships only.

### `GET /api/v1/jobs/freshers/`
Shortcut endpoint returning roles tailored for entry-level candidates and fresh graduates.

### `GET /api/v1/jobs/closing_soon/`
Shortcut endpoint returning verified opportunities closing within the next 3 days.

---

## 2. Employers (`/api/v1/companies/`)

### `GET /api/v1/companies/`
Lists verified employers and hiring organizations.

#### Example Response:
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Google",
      "slug": "google",
      "website": "https://careers.google.com",
      "industry": "Internet & Software",
      "headquarters": "Mountain View, CA",
      "is_verified": true,
      "jobs_count": 8
    }
  ]
}
```

### `GET /api/v1/companies/<slug>/`
Retrieves company profile, background, and open opportunity metrics.

---

## 3. Provenance Sources (`/api/v1/sources/`)

### `GET /api/v1/sources/`
Public registry of all verifiable aggregation sources, feed origins, and audit health logs.

#### Fields:
- `id`: Integer
- `name`: Source name
- `source_type`: `official_company`, `government`, `authorized_api`, `rss_feed`, `job_board`
- `source_url`: Verifiable web origin
- `status`: `active`, `degraded`, `failing`, `inactive`
- `total_jobs_collected`: Integer count

---

## 4. Skills & Categories (`/api/v1/skills/`, `/api/v1/categories/`)

### `GET /api/v1/skills/`
Lists standard skills from the CareerHunt taxonomy with search and category relationships.

### `GET /api/v1/categories/`
Lists standard career disciplines (Software Engineering, Data Science, Product, etc.).

---

## 5. Candidate Saved Opportunities (`/api/v1/saved-jobs/`)
*Requires authentication.*

- `GET /api/v1/saved-jobs/`: Lists candidate bookmarked jobs.
- `POST /api/v1/saved-jobs/`: Saves a job. Payload: `{"job_id": 14}`.
- `DELETE /api/v1/saved-jobs/<id>/`: Removes saved bookmark.

---

## 6. Candidate Application Tracker (`/api/v1/applications/`)
*Requires authentication.*

- `GET /api/v1/applications/`: Lists candidate tracked applications with statuses and interview dates.
- `POST /api/v1/applications/`: Adds tracking record.
  ```json
  {
    "job_id": 14,
    "status": "applied",
    "applied_date": "2026-10-03",
    "notes": "Submitted referral application."
  }
  ```
- `PATCH /api/v1/applications/<id>/`: Updates tracking status (`applied`, `assessment`, `interview`, `offer`, `rejected`), notes, or interview dates.
- `DELETE /api/v1/applications/<id>/`: Removes application tracker entry.

---

## 7. Opportunity Alerts (`/api/v1/alerts/`)
*Requires authentication.*

- `GET /api/v1/alerts/`: Lists active search alerts.
- `POST /api/v1/alerts/`: Creates automated job alert.
  ```json
  {
    "name": "Remote Django Internships",
    "keywords": "Django, Python",
    "location": "Remote",
    "opportunity_type": "internship",
    "frequency": "daily"
  }
  ```

---

## 8. Listing Reports (`/api/v1/reports/`)
*Requires authentication.*

- `POST /api/v1/reports/`: Reports suspicious, expired, or fraudulent listings for admin moderation.
  ```json
  {
    "job": 14,
    "reason": "expired_opportunity",
    "details": "Application link on official portal shows job closed."
  }
  ```
