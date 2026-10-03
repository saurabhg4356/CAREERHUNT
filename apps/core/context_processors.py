"""
Global context processors for CareerHunt templates.
"""
from datetime import datetime


def global_context(request):
    """
    Context processor injecting platform-wide constants and helpers.
    """
    return {
        "PLATFORM_NAME": "CareerHunt",
        "PLATFORM_TAGLINE": "Discover verified job and internship opportunities from identifiable sources.",
        "CURRENT_YEAR": datetime.now().year,
    }
