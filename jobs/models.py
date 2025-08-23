from django.db import models
from django.conf import settings


class Job(models.Model):
    JOB_STATUS = (
        ('available', 'Available'),
        ('pending', 'Pending'),          # At least one proposal is under review
        ('in_progress', 'In Progress'),  # A proposal has been accepted
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs_posted',
        limit_choices_to={'is_client': True}  # Ensure only clients can post
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='jobs_taken',
        null=True,
        blank=True,
        limit_choices_to={'is_freelancer': True}  # Assigned freelancer
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Estimated duration in days")
    deadline = models.DateTimeField(null=True, blank=True)
    skills_required = models.ManyToManyField("Skill", blank=True, related_name="jobs")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=JOB_STATUS, default='available')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Skill(models.Model):
    """Reusable skill model for tagging jobs."""
    name = models.CharField(max_length=50, unique=True)
    # approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

