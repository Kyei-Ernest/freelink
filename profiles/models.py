from django.db import models
from django.conf import settings


class Profile(models.Model):
    """
    Unified profile for both freelancers and profiles.
    Extra fields can be role-specific but live in one place.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    # Common fields
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True, null=True)

    # Freelancer-specific
    skills = models.JSONField(default=list, blank=True)  # e.g. ["Python", "Django", "UI Design"]
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)

    # Client-specific
    company_name = models.CharField(max_length=255, blank=True)
    company_description = models.TextField(blank=True)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_freelancer(self):
        return self.user.is_freelancer

    def is_client(self):
        return self.user.is_client

    def __str__(self):
        return f"{self.user.full_name} - {'Freelancer' if self.user.is_freelancer else 'Client'}"
