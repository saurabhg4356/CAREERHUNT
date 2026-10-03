"""
Notification and Alert management views for CareerHunt candidates.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification, JobAlert


@login_required
def notification_list_view(request):
    """
    Candidate notification inbox displaying alerts, status changes, and deadlines.
    """
    notifs = Notification.objects.filter(user=request.user).order_by("-created_at")
    unread_count = notifs.filter(is_read=False).count()

    if request.method == "POST":
        # Mark all as read
        notifs.filter(is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect("notifications:list")

    return render(request, "notifications/notification_list.html", {
        "notifications": notifs,
        "unread_count": unread_count,
    })


@login_required
def mark_read_view(request, pk):
    """
    Marks an individual notification as read and redirects to target URL if present.
    """
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    if notif.target_url:
        return redirect(notif.target_url)
    return redirect("notifications:list")


@login_required
def job_alerts_view(request):
    """
    Candidate job alerts configuration: list existing alerts and create new ones.
    """
    alerts = JobAlert.objects.filter(user=request.user)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        keywords = request.POST.get("keywords", "").strip()
        location = request.POST.get("location", "").strip()
        opp_type = request.POST.get("opportunity_type", "").strip()
        exp = request.POST.get("experience_level", "").strip()
        freq = request.POST.get("frequency", "daily")

        if name:
            JobAlert.objects.create(
                user=request.user,
                name=name,
                keywords=keywords,
                location=location,
                opportunity_type=opp_type,
                experience_level=exp,
                frequency=freq,
            )
            messages.success(request, f"Created alert '{name}'. You will receive notifications for matching openings.")
        else:
            messages.error(request, "Please provide an alert name.")
        return redirect("notifications:alerts")

    return render(request, "notifications/alerts.html", {
        "alerts": alerts,
    })


@login_required
def delete_alert_view(request, pk):
    """
    Deletes a candidate job alert rule.
    """
    alert = get_object_or_404(JobAlert, pk=pk, user=request.user)
    name = alert.name
    alert.delete()
    messages.info(request, f"Deleted alert '{name}'.")
    return redirect("notifications:alerts")
