"""
CareerHunt Transparent Recommendation Engine & Skill Gap Analysis.
Provides rule-based, deterministic match scoring without black-box claims.
Formula:
CareerHunt Match Score = (0.50 * Skill) + (0.20 * Location) + (0.20 * Experience) + (0.10 * Type)
"""
from typing import Dict, Any, List
from apps.accounts.models import UserProfile
from apps.jobs.models import Job


def compute_match_score(profile: UserProfile, job: Job) -> Dict[str, Any]:
    """
    Computes transparent CareerHunt Match Score (%) and skill gap breakdown.
    """
    # 1. Skill Match Calculation (50% weight)
    candidate_skills = {
        s.lower() for s in profile.user_skills.values_list("skill__name", flat=True)
    }
    job_skills_qs = job.skills.all()
    job_skills_list = [s.name for s in job_skills_qs]
    job_skills_lower = {s.lower() for s in job_skills_list}

    matched_skills = []
    missing_skills = []
    for s_name in job_skills_list:
        if s_name.lower() in candidate_skills:
            matched_skills.append(s_name)
        else:
            missing_skills.append(s_name)

    if not job_skills_list:
        skill_score = 80.0
    else:
        skill_score = (len(matched_skills) / len(job_skills_list)) * 100.0

    # 2. Location & Remote Mode Match (20% weight)
    loc_score = 30.0
    job_loc = (job.location_name or "").lower()
    user_loc = (profile.location or "").lower()
    preferred_locs = [pl.lower() for pl in profile.preferred_locations or []]

    if job.remote_type == "remote" and profile.preferred_work_mode in ["remote", "any"]:
        loc_score = 100.0
    elif any(pl in job_loc for pl in preferred_locs if pl):
        loc_score = 100.0
    elif user_loc and user_loc in job_loc:
        loc_score = 100.0
    elif job.remote_type == "remote":
        loc_score = 90.0
    elif profile.preferred_work_mode in ["any", "hybrid"]:
        loc_score = 75.0

    # 3. Experience Level Match (20% weight)
    exp_score = 40.0
    if profile.experience_level == job.experience_level:
        exp_score = 100.0
    elif profile.experience_level == "fresher" and job.experience_level == "0-1":
        exp_score = 80.0
    elif profile.experience_level == "0-1" and job.experience_level == "fresher":
        exp_score = 90.0

    # 4. Opportunity Type Match (10% weight)
    type_score = 50.0
    preferred_types = profile.preferred_job_types or []
    if not preferred_types:
        type_score = 85.0
    elif job.opportunity_type in preferred_types:
        type_score = 100.0

    # Weighted Overall Match Score
    total_score = (
        (0.50 * skill_score) +
        (0.20 * loc_score) +
        (0.20 * exp_score) +
        (0.10 * type_score)
    )

    return {
        "match_percentage": int(round(total_score)),
        "skill_match": int(round(skill_score)),
        "location_match": int(round(loc_score)),
        "experience_match": int(round(exp_score)),
        "type_match": int(round(type_score)),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
