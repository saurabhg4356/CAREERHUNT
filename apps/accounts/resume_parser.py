"""
Resume Analysis and Skill Entity Extraction for CareerHunt.
Extracts candidate skills, education keywords, and experience indicators from resume text.
"""
import re
from typing import Dict, Any, List, Set
from apps.jobs.models import Skill, Job


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extracts known technical and professional skills present in the resume text
    by matching against the CareerHunt skill taxonomy.
    """
    if not text:
        return []

    text_lower = text.lower()
    all_db_skills = Skill.objects.all()

    matched_skills = []
    for skill in all_db_skills:
        skill_name = skill.name
        # Match as whole word / token (e.g. 'c++' or 'python' or 'sql')
        escaped = re.escape(skill_name.lower())
        pattern = rf"(?:\b|\A){escaped}(?:\b|\Z)"
        if re.search(pattern, text_lower):
            matched_skills.append(skill_name)

    return sorted(list(set(matched_skills)))


def analyze_resume_text(text: str) -> Dict[str, Any]:
    """
    Analyzes resume text to discover technical skills, estimated education,
    and returns top matching opportunities.
    """
    detected_skills = extract_skills_from_text(text)
    
    # Infer experience level
    exp_level = "fresher"
    text_lower = text.lower()
    if re.search(r"\b(2\+|3\+|4\+|5\+)\s*(?:years|yrs)", text_lower):
        exp_level = "2+"
    elif re.search(r"\b(1|2)\s*(?:years|yrs)", text_lower):
        exp_level = "1-2"
    elif re.search(r"\b(intern|internship|fresher|graduate|student|b\.?tech|bca|mca)\b", text_lower):
        exp_level = "fresher"

    # Find top matching opportunities
    active_jobs = Job.objects.select_related("company", "source").prefetch_related("job_skills__skill").active()

    matches = []
    detected_set = {s.lower() for s in detected_skills}

    for job in active_jobs:
        job_skills = [s.name for s in job.skills.all()]
        matched = [s for s in job_skills if s.lower() in detected_set]
        missing = [s for s in job_skills if s.lower() not in detected_set]
        
        if job_skills:
            score = int(round((len(matched) / len(job_skills)) * 100))
        else:
            score = 75

        matches.append({
            "job": job,
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
        })

    matches.sort(key=lambda m: m["match_score"], reverse=True)

    return {
        "detected_skills": detected_skills,
        "estimated_experience": exp_level,
        "matching_opportunities": matches[:6],
    }
