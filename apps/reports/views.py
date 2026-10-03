"""
Opportunity report submission and moderation views for CareerHunt.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Report
from apps.jobs.models import Job


def submit_report_view(request, job_id):
    """
    Submits a user report against an opportunity listing.
    """
    job = get_object_or_404(Job, pk=job_id)

    if request.method == "POST":
        reason = request.POST.get("reason", "suspicious_link")
        details = request.POST.get("details", "").strip()

        if details:
            Report.objects.create(
                job=job,
                reported_by=request.user if request.user.is_authenticated else None,
                reason=reason,
                details=details,
                status="pending",
            )
            # Mark listing as reported
            job.verification_status = "reported"
            job.save()

            messages.success(request, "Thank you. Your report has been submitted to the moderation team.")
            return redirect("jobs:job_detail", slug=job.slug)
        else:
            messages.error(request, "Please provide details explaining the issue.")

    return render(request, "reports/submit_report.html", {
        "job": job,
        "reason_choices": Report.REASON_CHOICES,
    })


@user_passes_test(lambda u: u.is_staff)
def resolve_report_view(request, pk):
    """
    Staff moderation action: mark report as resolved or dismissed,
    with option to disable or reinstate the listing.
    """
    report = get_object_or_404(Report, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")  # 'resolve_disable', 'resolve_keep', 'dismiss'
        admin_notes = request.POST.get("admin_notes", "").strip()

        report.admin_notes = admin_notes
        report.reviewed_by = request.user
        report.resolved_at = timezone.now()

        if action == "resolve_disable":
            report.status = "resolved"
            report.job.status = "closed"
            report.job.verification_status = "reported"
            report.job.save()
            messages.success(request, f"Report resolved: {report.job.title} has been closed/deactivated.")
        elif action == "resolve_keep":
            report.status = "resolved"
            report.job.verification_status = "verified"
            report.job.save()
            messages.success(request, "Report resolved: listing retained.")
        elif action == "dismiss":
            report.status = "dismissed"
            report.job.verification_status = "verified"
            report.job.save()
            messages.info(request, "Report dismissed as invalid.")

        report.save()
    return redirect("dashboard:admin_dashboard")
