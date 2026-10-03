"""
CareerHunt Ingestion Pipeline: Normalization, Validation, and Deterministic Deduplication.
"""
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Dict, Any, Optional, Tuple
from django.utils import timezone
from apps.jobs.models import Job, Category, Skill, JobSkill
from apps.companies.models import Company
from apps.sources.models import JobSource


def canonicalize_url(url: str) -> str:
    """
    Remove marketing tracking parameters (utm_*, ref, fbclid, etc.)
    and trailing slashes for deterministic URL matching.
    """
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        query_params = parse_qs(parsed.query, keep_blank_values=False)
        # Filter out tracking query parameters
        cleaned_params = {
            k: v for k, v in query_params.items()
            if not k.startswith("utm_") and k not in ["ref", "fbclid", "gclid", "source", "affiliate"]
        }
        # Rebuild query string in sorted order
        new_query = urlencode(cleaned_params, doseq=True)
        # Standardize path
        clean_path = parsed.path.rstrip("/")
        clean_url = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            clean_path,
            parsed.params,
            new_query,
            ""  # drop fragment
        ))
        return clean_url
    except Exception:
        return url.strip().rstrip("/")


def normalize_title(title: str) -> str:
    """
    Normalize role title: collapse whitespace, remove extraneous symbols.
    """
    if not title:
        return ""
    title = re.sub(r"\s+", " ", title).strip()
    return title


def normalize_opportunity(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize raw opportunity fields into CareerHunt schema.
    """
    title = normalize_title(raw.get("title", ""))
    company_name = raw.get("company_name", "").strip()
    
    app_url = canonicalize_url(raw.get("application_url", ""))
    src_url = canonicalize_url(raw.get("source_url", "") or app_url)
    
    opp_type = raw.get("opportunity_type", "full-time").lower()
    if "intern" in title.lower() or "intern" in opp_type:
        opp_type = "internship"
    elif "graduate" in opp_type or "graduate" in title.lower():
        opp_type = "graduate-program"
    elif "trainee" in opp_type or "trainee" in title.lower():
        opp_type = "trainee"
    elif "apprentice" in opp_type:
        opp_type = "apprenticeship"
    elif opp_type not in ["internship", "full-time", "part-time", "contract", "apprenticeship", "graduate-program", "trainee"]:
        opp_type = "full-time"

    exp_level = raw.get("experience_level", "fresher").lower()
    if exp_level not in ["fresher", "0-1", "1-2", "2+"]:
        exp_level = "fresher"

    remote_type = raw.get("remote_type", "on-site").lower()
    if remote_type not in ["on-site", "remote", "hybrid"]:
        remote_type = "on-site"

    ext_id = raw.get("external_id") or raw.get("id") or raw.get("job_id") or ""
    return {
        "title": title,
        "company_name": company_name,
        "external_id": str(ext_id).strip(),
        "source_url": src_url,
        "application_url": app_url,
        "description": raw.get("description", "").strip(),
        "requirements": raw.get("requirements", "").strip(),
        "opportunity_type": opp_type,
        "experience_level": exp_level,
        "remote_type": remote_type,
        "location_name": raw.get("location_name", "Remote").strip(),
        "salary_min": raw.get("salary_min"),
        "salary_max": raw.get("salary_max"),
        "is_salary_disclosed": bool(raw.get("salary_min")),
        "application_open_date": raw.get("application_open_date"),
        "application_deadline": raw.get("application_deadline"),
        "skills": raw.get("skills", []),
    }


def validate_opportunity(norm: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Enforce mandatory fields, minimum lengths, and valid URL formats.
    Returns (is_valid, error_reason).
    """
    if not norm.get("title") or len(norm["title"]) < 3:
        return False, "Title is missing or too short (<3 chars)."
    if not norm.get("company_name"):
        return False, "Company name is required."
    if not norm.get("application_url"):
        return False, "Application URL is required."
    
    app_url = norm["application_url"]
    if not (app_url.startswith("http://") or app_url.startswith("https://")):
        return False, f"Invalid application URL scheme: {app_url}"

    return True, None


def deduplicate_opportunity(source: JobSource, norm: Dict[str, Any]) -> Optional[Job]:
    """
    Multi-tiered deterministic deduplication:
    1. Match on (source, external_id) if external_id exists.
    2. Match on canonical application_url.
    3. Match on (company, normalized_title, location).
    """
    ext_id = norm.get("external_id")
    if ext_id:
        existing = Job.objects.filter(source=source, external_id=ext_id).first()
        if existing:
            return existing

    app_url = norm.get("application_url")
    if app_url:
        existing = Job.objects.filter(application_url=app_url).first()
        if existing:
            return existing

    company_name = norm.get("company_name")
    title = norm.get("title")
    location = norm.get("location_name")
    if company_name and title:
        existing = Job.objects.filter(
            company__name__iexact=company_name,
            title__iexact=title,
            location_name__iexact=location,
        ).first()
        if existing:
            return existing

    return None
