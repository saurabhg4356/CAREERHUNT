"""
Application Tracker views for CareerHunt candidates.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View
from django.utils import timezone
from .models import Application
from apps.jobs.models import Job


@login_required
def application_dashboard(request):
    """
    Candidate application tracker board displaying applied, interviewing,
    and offer statuses with dates and personal notes.
    """
    user_apps = Application.objects.filter(user=request.user).select_related("job", "job__company", "job__source")
    
    # Categorize by status for dashboard cards
    status_counts = {
        "applied": user_apps.filter(status="applied").count(),
        "assessment": user_apps.filter(status="assessment").count(),
        "interview": user_apps.filter(status="interview").count(),
        "offer": user_apps.filter(status="offer").count(),
        "rejected": user_apps.filter(status="rejected").count(),
        "total": user_apps.count(),
    }

    upcoming_interviews = user_apps.filter(
        interview_date__isnull=False,
        interview_date__gte=timezone.now()
    ).order_by("interview_date")

    return render(request, "applications/tracker.html", {
        "applications": user_apps,
        "status_counts": status_counts,
        "upcoming_interviews": upcoming_interviews,
        "status_choices": Application.STATUS_CHOICES,
    })


@login_required
def track_job_view(request, job_id):
    """
    Directly adds an opportunity to the candidate's application tracker.
    """
    job = get_object_or_404(Job, pk=job_id)
    if request.method == "POST":
        status = request.POST.get("status", "applied")
        notes = request.POST.get("notes", "")
        applied_date = request.POST.get("applied_date") or timezone.now().date()
        
        app, created = Application.objects.get_or_create(
            user=request.user,
            job=job,
            defaults={
                "status": status,
                "notes": notes,
                "applied_date": applied_date,
            }
        )
        if not created:
            app.status = status
            if notes:
                app.notes = notes
            app.save()
            messages.info(request, f"Updated tracking status for {job.title}.")
        else:
            messages.success(request, f"Now tracking application for {job.title}!")

    return redirect("applications:dashboard")


@login_required
def update_application_view(request, pk):
    """
    Updates status, interview schedule, and personal notes.
    """
    app = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        notes = request.POST.get("notes", "")
        interview_date = request.POST.get("interview_date")
        
        if new_status in dict(Application.STATUS_CHOICES):
            app.status = new_status
        app.notes = notes
        if interview_date:
            app.interview_date = interview_date
        app.save()
        messages.success(request, f"Updated application status for {app.job.title}.")

    return redirect("applications:dashboard")


@login_required
def delete_application_view(request, pk):
    """
    Removes tracking record.
    """
    app = get_object_or_404(Application, pk=pk, user=request.user)
    job_title = app.job.title
    app.delete()
    messages.info(request, f"Removed {job_title} from your application tracker.")
    return redirect("applications:dashboard")
