from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from transactions.models import Transaction
from clients.models import ClientProfile
from wallet.models import Wallet

User = get_user_model()

class Escrow(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='escrow',
        help_text="The transaction associated with this escrow"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Amount held in escrow"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('HELD', 'Held'),
            ('RELEASED', 'Released'),
            ('REFUNDED', 'Refunded')
        ],
        default='HELD',
        help_text="Escrow status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Escrow"
        verbose_name_plural = "Escrows"

    def clean(self):
        # Ensure transaction is PENDING
        if self.transaction.status != 'PENDING':
            raise ValidationError("Escrow can only be created for PENDING transactions.")
        # Ensure amount matches transaction amount
        if self.amount != self.transaction.amount:
            raise ValidationError("Escrow amount must match transaction amount.")
        # Validate client budget range
        budget_range = self.transaction.client.client_profile.budget_range
        if budget_range == 'LOW' and self.amount > 5000:
            raise ValidationError(f"Escrow amount {self.amount} exceeds client's LOW budget range ($0 - $5,000)")
        elif budget_range == 'MEDIUM' and self.amount > 20000:
            raise ValidationError(f"Escrow amount {self.amount} exceeds client's MEDIUM budget range ($5,001 - $20,000)")
        # Validate client wallet balance
        try:
            client_wallet = self.transaction.client.wallet
            if client_wallet.balance < self.amount:
                raise ValidationError("Insufficient funds in client's wallet.")
        except Wallet.DoesNotExist:
            raise ValidationError("Client must have a wallet.")

    def release(self):
        """Release funds to freelancer's wallet."""
        if self.status != 'HELD':
            raise ValidationError(f"Cannot release escrow in {self.status} status.")
        try:
            client_wallet = self.transaction.client.wallet
            freelancer_wallet = self.transaction.freelancer.wallet
            client_wallet.withdraw(self.amount)
            freelancer_wallet.deposit(self.amount)
            self.status = 'RELEASED'
            self.save()
        except Wallet.DoesNotExist:
            raise ValidationError("Both client and freelancer must have wallets.")

    def refund(self):
        """Refund funds to client's wallet."""
        if self.status != 'HELD':
            raise ValidationError(f"Cannot refund escrow in {self.status} status.")
        try:
            client_wallet = self.transaction.client.wallet
            client_wallet.deposit(self.amount)
            self.status = 'REFUNDED'
            self.save()
        except Wallet.DoesNotExist:
            raise ValidationError("Client must have a wallet.")

    def __str__(self):
        return f"Escrow for Transaction {self.transaction.id} (Amount: ${self.amount}, Status: {self.status})"