from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Currency, Wallet


@receiver(post_save, sender=get_user_model())
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        # Create a wallet for the user with default currency if Currency exists
        default_currency = None
        try:
            default_currency = Currency.objects.first()
        except Exception:
            default_currency = None

        Wallet.objects.create(user=instance, currency=default_currency)