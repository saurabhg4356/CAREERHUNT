"""
URL configuration for apps.accounts.
"""
from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    logout_view,
    profile_view,
    add_education_view,
    delete_education_view,
    add_skill_view,
    remove_skill_view,
    resume_matcher_view,
    import_resume_skills_view,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/education/add/", add_education_view, name="add_education"),
    path("profile/education/<int:pk>/delete/", delete_education_view, name="delete_education"),
    path("profile/skills/add/", add_skill_view, name="add_skill"),
    path("profile/skills/<int:pk>/remove/", remove_skill_view, name="remove_skill"),
    path("resume-matcher/", resume_matcher_view, name="resume_matcher"),
    path("resume-matcher/import-skills/", import_resume_skills_view, name="import_resume_skills"),
]
