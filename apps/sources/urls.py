"""
URL configuration for apps.sources.
"""
from django.urls import path
from .views import SourceListView, SourceDetailView

app_name = "sources"

urlpatterns = [
    path("", SourceListView.as_view(), name="source_list"),
    path("<int:pk>/", SourceDetailView.as_view(), name="source_detail"),
]
