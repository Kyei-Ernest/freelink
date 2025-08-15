from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from profiles.models import Profile

from django.contrib.auth import get_user_model
from .utils import send_verification_email

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create a Profile when a new User is created.
    Update the existing Profile when a User is updated.
    """
    if created:
        # Create only if it doesn't exist already
        Profile.objects.get_or_create(user=instance)
    else:
        try:
            instance.profile.save()
        except ObjectDoesNotExist:
            Profile.objects.create(user=instance)



User = get_user_model()

@receiver(post_save, sender=User)
def send_verification_on_signup(sender, instance, created, **kwargs):
    """
    Sends verification email when a new user is created.
    """
    if created:
        send_verification_email(instance)

