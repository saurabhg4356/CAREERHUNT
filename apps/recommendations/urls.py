"""
URL configuration for apps.recommendations.
"""
from django.urls import path
from .views import recommendation_list, skill_gap_detail

app_name = "recommendations"

urlpatterns = [
    path("", recommendation_list, name="list"),
    path("skill-gap/<slug:slug>/", skill_gap_detail, name="skill_gap"),
]
