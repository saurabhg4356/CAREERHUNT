"""
Authentication and Profile views for CareerHunt candidates.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View, CreateView
from django.urls import reverse_lazy, reverse
from .forms import (
    CandidateRegistrationForm,
    CandidateLoginForm,
    UserProfileUpdateForm,
    UserEducationForm,
)
from .models import UserProfile, UserEducation, UserSkill
from apps.jobs.models import Skill


class RegisterView(View):
    """Handles candidate registration."""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("core:home")
        form = CandidateRegistrationForm()
        return render(request, "accounts/register.html", {"form": form})

    def post(self, request):
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CareerHunt, {user.first_name}! Your profile is ready.")
            return redirect("accounts:profile")
        return render(request, "accounts/register.html", {"form": form})


class LoginView(View):
    """Handles candidate sign-in."""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("core:home")
        form = CandidateLoginForm()
        return render(request, "accounts/login.html", {"form": form})

    def post(self, request):
        form = CandidateLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get("next") or "core:home"
            return redirect(next_url)
        return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """Signs candidate out and redirects to home."""
    logout(request)
    messages.info(request, "You have been successfully signed out.")
    return redirect("core:home")


@login_required
def profile_view(request):
    """
    Candidate profile management: view details, update preferences,
    manage education and skills.
    """
    profile = request.user.profile
    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile and preferences have been updated.")
            return redirect("accounts:profile")
    else:
        form = UserProfileUpdateForm(instance=profile)

    education_form = UserEducationForm()
    available_skills = Skill.objects.exclude(id__in=profile.user_skills.values_list("skill_id", flat=True))

    return render(request, "accounts/profile.html", {
        "form": form,
        "profile": profile,
        "education_form": education_form,
        "available_skills": available_skills,
    })


@login_required
def add_education_view(request):
    """Add education record to candidate profile."""
    if request.method == "POST":
        form = UserEducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.profile = request.user.profile
            education.save()
            messages.success(request, "Education credential added.")
        else:
            messages.error(request, "Please enter valid education details.")
    return redirect("accounts:profile")


@login_required
def delete_education_view(request, pk):
    """Delete an education credential."""
    education = get_object_or_404(UserEducation, pk=pk, profile=request.user.profile)
    education.delete()
    messages.info(request, "Education entry removed.")
    return redirect("accounts:profile")


@login_required
def add_skill_view(request):
    """Add a skill to the candidate's profile."""
    if request.method == "POST":
        skill_id = request.POST.get("skill_id")
        proficiency = request.POST.get("proficiency", "intermediate")
        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
            UserSkill.objects.get_or_create(
                profile=request.user.profile,
                skill=skill,
                defaults={"proficiency": proficiency},
            )
            messages.success(request, f"Added {skill.name} to your skills.")
    return redirect("accounts:profile")


@login_required
def remove_skill_view(request, pk):
    """Remove a skill from the candidate's profile."""
    user_skill = get_object_or_404(UserSkill, pk=pk, profile=request.user.profile)
    skill_name = user_skill.skill.name
    user_skill.delete()
    messages.info(request, f"Removed {skill_name} from your profile.")
    return redirect("accounts:profile")
