"""
Core views for CareerHunt.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    Landing page view displaying hero search, featured opportunities,
    and platform value propositions.
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Dynamic context populated in subsequent stages as models come online
        context["featured_jobs"] = []
        context["upcoming_jobs"] = []
        context["closing_soon_jobs"] = []
        context["popular_skills"] = [
            "Python", "Django", "Java", "React", "JavaScript",
            "SQL", "AWS", "Docker", "Machine Learning"
        ]
        context["popular_locations"] = [
            "Bangalore", "Mumbai", "Pune", "Hyderabad", "Delhi NCR", "Remote"
        ]
        return context


def health_check(request):
    """
    Health check endpoint returning system status and database connectivity.
    """
    from django.db import connection
    db_status = "healthy"
    try:
        connection.ensure_connection()
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return JsonResponse({
        "status": "ok" if db_status == "healthy" else "degraded",
        "service": "CareerHunt Core",
        "database": db_status,
        "version": "1.0.0",
    })


def custom_404(request, exception=None):
    """Custom 404 error handler."""
    return render(request, "errors/404.html", status=404)


def custom_500(request):
    """Custom 500 error handler."""
    return render(request, "errors/500.html", status=500)


def custom_403(request, exception=None):
    """Custom 403 error handler."""
    return render(request, "errors/403.html", status=403)
