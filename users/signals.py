from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from freelancers.models import FreelancerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_freelancer_profile(sender, instance, created, **kwargs):
    if created and instance.is_freelancer:
        FreelancerProfile.objects.create(user=instance)