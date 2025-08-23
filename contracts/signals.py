from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contract

@receiver(post_save, sender=Contract)
def notify_contract_parties(sender, instance, created, **kwargs):
    if created or instance.status in ['pending_acceptance', 'active', 'in_review', 'completed', 'disputed', 'cancelled']:
        # Placeholder for notification logic (e.g., email, in-app notification)
        action = 'created' if created else instance.status
        print(f"Notify {instance.client.email} and {instance.freelancer.email}: Contract {instance.id} {action}")
