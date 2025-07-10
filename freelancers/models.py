from django.db import models
from django.conf import settings

class Skill(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class FreelancerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    campus_verified = models.BooleanField(default=False)
    student_id_card = models.ImageField(upload_to='id_cards/', null=True, blank=True)