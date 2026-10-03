"""
Recommendation and Skill Gap Analysis views for CareerHunt.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.jobs.models import Job
from .engine import compute_match_score


@login_required
def recommendation_list(request):
    """
    Ranks active opportunities specifically tailored to the logged-in candidate's
    skills, experience level, preferred work modes, and locations.
    """
    profile = request.user.profile
    active_jobs = Job.objects.select_related("company", "source", "category").prefetch_related("job_skills__skill").active()

    scored_jobs = []
    for job in active_jobs:
        score_data = compute_match_score(profile, job)
        scored_jobs.append({
            "job": job,
            "score": score_data,
        })

    # Sort descending by match percentage
    scored_jobs.sort(key=lambda item: item["score"]["match_percentage"], reverse=True)

    return render(request, "recommendations/recommendations.html", {
        "scored_jobs": scored_jobs,
        "candidate_skills_count": profile.user_skills.count(),
    })


@login_required
def skill_gap_detail(request, slug):
    """
    Detailed side-by-side skill gap comparison for a specific opportunity.
    """
    job = get_object_or_404(Job.objects.select_related("company", "source").prefetch_related("job_skills__skill"), slug=slug)
    score_data = compute_match_score(request.user.profile, job)

    return render(request, "recommendations/skill_gap_detail.html", {
        "job": job,
        "score": score_data,
    })
