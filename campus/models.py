from django.db import models
from django.conf import settings

class CampusService(models.Model):
    university = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.university}"