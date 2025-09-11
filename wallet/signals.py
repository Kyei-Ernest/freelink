from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Currency, Wallet

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Automatically create a wallet for each new user.
    Currency is determined by the user's country if possible.
    """

    COUNTRY_CURRENCY_MAP = {
        "GH": "GHS",
        "USA": "USD",
        "UK": "GBP",
        "NG": "NGN",
        # add more as needed
    }

    if created:
        # get currency code from user's country (fallback to USD)
        currency_code = COUNTRY_CURRENCY_MAP.get(instance.country, "USD")

        # fetch the Currency object
        default_currency = Currency.objects.filter(code=currency_code).first()

        # create wallet only if user doesn't already have one
        if not hasattr(instance, "wallet"):
            Wallet.objects.create(user=instance, currency=default_currency)
