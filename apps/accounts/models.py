"""
Candidate user profile, education, and skill models for CareerHunt.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.models import TimeStampedModel
from apps.jobs.models import Skill


class UserProfile(TimeStampedModel):
    """
    Extended candidate profile storing background, education, and career preferences.
    """
    EXPERIENCE_LEVELS = [
        ("fresher", "Fresher / Student"),
        ("0-1", "0-1 years"),
        ("1-2", "1-2 years"),
        ("2+", "2+ years"),
    ]

    WORK_MODES = [
        ("any", "Any / Flexible"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
        ("on-site", "On-site"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    headline = models.CharField(max_length=255, blank=True, help_text="e.g. Aspiring Backend Developer | Final Year CS Student")
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)

    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default="fresher")
    preferred_work_mode = models.CharField(max_length=20, choices=WORK_MODES, default="any")
    
    # Store list of selected strings, e.g. ["internship", "full-time"]
    preferred_job_types = models.JSONField(default=list, blank=True)
    # Store list of preferred cities, e.g. ["Bangalore", "Pune", "Remote"]
    preferred_locations = models.JSONField(default=list, blank=True)

    expected_salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    resume = models.FileField(upload_to="resumes/%Y/%m/", null=True, blank=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """
    Ensure every User instance automatically has an associated UserProfile.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()


class UserEducation(TimeStampedModel):
    """
    Educational credentials (Degree, College, Graduation Year).
    """
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="educations")
    degree = models.CharField(max_length=150, help_text="e.g. B.Tech in Computer Science")
    institution = models.CharField(max_length=255, help_text="College or University Name")
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField(help_text="Year of graduation or expected completion")
    grade_or_cgpa = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "User Education"
        verbose_name_plural = "User Educations"
        ordering = ["-end_year"]

    def __str__(self):
        return f"{self.degree} from {self.institution} ({self.end_year})"


class UserSkill(TimeStampedModel):
    """
    Skills possessed by a candidate with self-assessed proficiency.
    """
    PROFICIENCY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="user_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="skilled_candidates")
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default="intermediate")

    class Meta:
        verbose_name = "User Skill"
        verbose_name_plural = "User Skills"
        unique_together = ("profile", "skill")

    def __str__(self):
        return f"{self.profile.user.username} - {self.skill.name} ({self.proficiency})"
