from django.db import models
from django.conf import settings
from django.utils import timezone

class Job(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('AWAITING_REVIEW', 'Awaiting Review'),
        ('COMPLETED', 'Completed'),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    def __str__(self):
        return f"{self.title} ({self.client.username})"

    def is_overdue(self):
        return self.deadline < timezone.now().date() and self.status != 'COMPLETED'

    class Meta:
        ordering = ['-created_at']


class JobApplication(models.Model):
    job = models.ForeignKey(Job, related_name="applications", on_delete=models.CASCADE)
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover_letter = models.TextField()
    is_selected = models.BooleanField(default=False)
    applied_at = models.DateTimeField(auto_now_add=True)
    selected_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.freelancer.username} - {self.job.title}"

