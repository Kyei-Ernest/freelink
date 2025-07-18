from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from clients.models import ClientProfile

User = get_user_model()

class Transaction(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client_transactions',
        limit_choices_to={'is_client': True, 'is_verified': True},
        help_text="The client making the payment"
    )
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='freelancer_transactions',
        limit_choices_to={'is_freelancer': True, 'is_verified': True},
        help_text="The freelancer receiving the payment"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Transaction amount in USD"
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Description of the transaction (e.g., project details)"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
            ('REFUNDED', 'Refunded')
        ],
        default='PENDING',
        help_text="Transaction status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def clean(self):
        if self.client == self.freelancer:
            raise ValidationError("Client and freelancer cannot be the same user.")
        if not (self.client.is_client and self.client.is_verified):
            raise ValidationError("Client must be a verified client.")
        if not (self.freelancer.is_freelancer and self.freelancer.is_verified):
            raise ValidationError("Freelancer must be a verified freelancer.")
        if not hasattr(self.client, 'client_profile'):
            raise ValidationError("Client must have a profile.")
        if not hasattr(self.freelancer, 'freelancer_profile'):
            raise ValidationError("Freelancer must have a profile.")
        # Validate amount against budget_range
        budget_range = self.client.client_profile.budget_range
        if budget_range == 'LOW' and self.amount > 5000:
            raise ValidationError(f"Transaction amount {self.amount} exceeds client's LOW budget range ($0 - $5,000)")
        elif budget_range == 'MEDIUM' and self.amount > 20000:
            raise ValidationError(f"Transaction amount {self.amount} exceeds client's MEDIUM budget range ($5,001 - $20,000)")
        # Check client wallet balance
        if hasattr(self.client, 'wallet') and self.amount > self.client.wallet.balance:
            raise ValidationError("Insufficient funds in client's wallet.")

    def __str__(self):
        return f"Transaction of {self.amount} from {self.client.username} to {self.freelancer.username} ({self.status})"