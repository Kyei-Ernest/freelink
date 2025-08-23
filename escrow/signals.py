"""from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

#from jobs.models import Job
from .models import Escrow
from wallet.models import Wallet
from notifications.utils import send_email_notification, create_notification

@receiver(post_save, sender=Job)
def auto_release_escrow(sender, instance, **kwargs):
    if instance.is_completed:
        try:
            escrow = Escrow.objects.get(job=instance, is_released=False)

            # Add funds to freelancer's wallet
            freelancer_wallet = Wallet.objects.get(user=escrow.freelancer)
            freelancer_wallet.balance += escrow.amount
            freelancer_wallet.save()

            # Mark escrow as released
            escrow.is_released = True
            escrow.released_at = timezone.now()
            escrow.save()

            # Send email
            send_email_notification(
                "Escrow Auto-Released",
                f"Job '{instance.title}' is marked complete and funds have been auto-released.",
                [escrow.freelancer.email, escrow.client.email]
            )

            # Create notifications
            create_notification(escrow.freelancer, "Payment Released", f"Funds for job '{instance.title}' have been released.")
            create_notification(escrow.client, "Job Completed", f"Job '{instance.title}' was completed and escrow was released.")

        except Escrow.DoesNotExist:
            pass  # Optionally: log this
"""