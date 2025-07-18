from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Wallet(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wallet',
        limit_choices_to={'is_verified': True},
        help_text="The user owning this wallet"
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        help_text="Current balance in USD"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"

    def clean(self):
        # Ensure user is verified
        if not self.user.is_verified:
            raise ValidationError("Only verified users can have a wallet.")
        # Ensure user is either a client or freelancer
        if not (self.user.is_client or self.user.is_freelancer):
            raise ValidationError("User must be a client or freelancer to have a wallet.")

    def __str__(self):
        return f"Wallet for {self.user.username} (Balance: ${self.balance})"

    def deposit(self, amount):
        """Add funds to the wallet."""
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive.")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        """Withdraw funds from the wallet."""
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValidationError("Insufficient funds for withdrawal.")
        self.balance -= amount
        self.save()