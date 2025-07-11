from django.db import models
from django.conf import settings
from jobs.models import Job

class Escrow(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='escrow_client')
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='escrow_freelancer')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_released = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
