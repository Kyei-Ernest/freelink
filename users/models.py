from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_freelancer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, unique=True)
    language_preference = models.CharField(max_length=10, default='en')
    is_verified = models.BooleanField(default=False)  # For email verification
    is_phone_verified = models.BooleanField(default=False)