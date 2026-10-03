"""
Job, Internship, Taxonomy, and Skill models for CareerHunt.
"""
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from apps.core.models import TimeStampedModel
from apps.companies.models import Company
from apps.sources.models import JobSource


class Category(TimeStampedModel):
    """
    Career category (e.g., Software Engineering, Data Science, Product Management).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon identifier or SVG symbol")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Skill(TimeStampedModel):
    """
    Technical or professional skill tag (e.g. Python, Django, AWS, SQL).
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="skills")

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class JobQuerySet(models.QuerySet):
    """
    Custom QuerySet providing high-utility domain query filters.
    """
    def active(self):
        now = timezone.now()
        return self.filter(
            status__in=["active", "closing-soon"],
            application_deadline__gte=now,
        ) | self.filter(
            status__in=["active", "closing-soon"],
            application_deadline__isnull=True,
        )

    def upcoming(self):
        now = timezone.now()
        return self.filter(
            models.Q(status="upcoming") | models.Q(application_open_date__gt=now)
        )

    def closing_soon(self):
        now = timezone.now()
        three_days_later = now + timezone.timedelta(days=3)
        return self.filter(
            status__in=["active", "closing-soon"],
            application_deadline__gte=now,
            application_deadline__lte=three_days_later,
        )

    def internships(self):
        return self.filter(opportunity_type="internship")

    def freshers(self):
        return self.filter(experience_level="fresher")


class JobManager(models.Manager):
    """
    Manager delegating to JobQuerySet with default domain methods.
    """
    def get_queryset(self):
        return JobQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def upcoming(self):
        return self.get_queryset().upcoming()

    def closing_soon(self):
        return self.get_queryset().closing_soon()

    def internships(self):
        return self.get_queryset().internships()

    def freshers(self):
        return self.get_queryset().freshers()


class Job(TimeStampedModel):
    """
    Central opportunity model representing jobs, internships, graduate programs,
    and traineeships aggregated from verified sources.
    """
    OPPORTUNITY_TYPES = [
        ("internship", "Internship"),
        ("full-time", "Full-time"),
        ("part-time", "Part-time"),
        ("apprenticeship", "Apprenticeship"),
        ("graduate-program", "Graduate Program"),
        ("trainee", "Trainee"),
        ("contract", "Contract"),
    ]

    EXPERIENCE_LEVELS = [
        ("fresher", "Fresher"),
        ("0-1", "0-1 years"),
        ("1-2", "1-2 years"),
        ("2+", "2+ years"),
    ]

    REMOTE_TYPES = [
        ("on-site", "On-site"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
    ]

    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("active", "Active"),
        ("closing-soon", "Closing Soon"),
        ("expired", "Expired"),
        ("closed", "Closed"),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ("verified", "Verified"),
        ("pending-review", "Pending Review"),
        ("reported", "Reported"),
        ("unverified", "Unverified"),
    ]

    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs")
    source = models.ForeignKey(JobSource, on_delete=models.PROTECT, related_name="jobs")
    
    external_id = models.CharField(max_length=255, blank=True, db_index=True)
    source_url = models.URLField(max_length=1000)
    application_url = models.URLField(max_length=1000, db_index=True)

    description = models.TextField()
    requirements = models.TextField(blank=True)

    opportunity_type = models.CharField(max_length=30, choices=OPPORTUNITY_TYPES, default="internship", db_index=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default="fresher", db_index=True)
    remote_type = models.CharField(max_length=20, choices=REMOTE_TYPES, default="on-site", db_index=True)
    location_name = models.CharField(max_length=150, db_index=True)

    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default="INR")
    is_salary_disclosed = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", db_index=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default="verified", db_index=True)

    posted_at = models.DateTimeField(default=timezone.now, db_index=True)
    application_open_date = models.DateTimeField(null=True, blank=True, db_index=True)
    application_deadline = models.DateTimeField(null=True, blank=True, db_index=True)
    last_checked_at = models.DateTimeField(default=timezone.now)

    skills = models.ManyToManyField(Skill, through="JobSkill", related_name="jobs", blank=True)

    objects = JobManager()

    class Meta:
        verbose_name = "Opportunity"
        verbose_name_plural = "Opportunities"
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["status", "opportunity_type", "experience_level"]),
            models.Index(fields=["status", "application_deadline"]),
            models.Index(fields=["company", "title"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.title}")
            unique_slug = base_slug
            num = 1
            while Job.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        
        self.update_status_based_on_dates()
        super().save(*args, **kwargs)

    def update_status_based_on_dates(self):
        """
        Dynamically adjusts status based on application opening and deadline.
        """
        now = timezone.now()
        if self.application_open_date and self.application_open_date > now:
            self.status = "upcoming"
        elif self.application_deadline and self.application_deadline < now:
            self.status = "expired"
        elif self.application_deadline and 0 <= (self.application_deadline - now).total_seconds() <= 3 * 86400:
            if self.status != "closed":
                self.status = "closing-soon"
        elif self.status in ["upcoming", "closing-soon", "expired"]:
            self.status = "active"

    @property
    def is_closing_soon(self) -> bool:
        if not self.application_deadline:
            return False
        remaining = self.application_deadline - timezone.now()
        return 0 <= remaining.total_seconds() <= 3 * 86400

    @property
    def days_until_deadline(self) -> int:
        if not self.application_deadline:
            return -1
        delta = self.application_deadline - timezone.now()
        days = (self.application_deadline.date() - timezone.now().date()).days
        return max(0, days)

    @property
    def days_until_opening(self) -> int:
        if not self.application_open_date:
            return 0
        days = (self.application_open_date.date() - timezone.now().date()).days
        return max(0, days)

    def deadline_display(self) -> str:
        """
        Human-readable remaining time text.
        """
        if not self.application_deadline:
            return "Ongoing / Rolling"
        now = timezone.now()
        if self.application_deadline < now:
            return "Expired"
        delta = self.application_deadline - now
        days = (self.application_deadline.date() - now.date()).days
        hours = max(1, delta.seconds // 3600)
        if days == 0:
            return f"Closing today ({hours}h remaining)"
        elif days == 1:
            return "Closing tomorrow"
        elif days <= 3:
            return f"{days} days remaining (Closing soon)"
        return f"{days} days remaining"

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class JobSkill(TimeStampedModel):
    """
    Through model linking Job to Skill with requirement level.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="skill_jobs")
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Job Skill"
        verbose_name_plural = "Job Skills"
        unique_together = ("job", "skill")

    def __str__(self):
        return f"{self.job.title} - {self.skill.name} ({'Required' if self.is_mandatory else 'Preferred'})"
