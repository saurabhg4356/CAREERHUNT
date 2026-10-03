"""
Company and employer models for CareerHunt.
"""
from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel


class Company(TimeStampedModel):
    """
    Represents an employer or hiring organization.
    """
    name = models.CharField(max_length=255, unique=True, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    website = models.URLField(max_length=500, blank=True)
    logo = models.ImageField(upload_to="companies/logos/", blank=True, null=True)
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    headquarters = models.CharField(max_length=150, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
