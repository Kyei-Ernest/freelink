from django.db import models
from django.conf import settings

class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True)
    company_website = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.user.username