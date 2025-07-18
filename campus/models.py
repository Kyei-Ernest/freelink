from django.db import models
from django.conf import settings

class CampusService(models.Model):
    university = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    # ----
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("ASSIGNED", "Assigned"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    contact_info = models.CharField(max_length=100, blank=True)
    attachment = models.FileField(upload_to="campus_attachments/", null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} @ {self.university}"