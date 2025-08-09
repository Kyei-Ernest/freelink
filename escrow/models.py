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
            ('REFUNDED', 'Refunded'),
            ('DISPUTED', 'Disputed')
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
        if self.transaction.status != 'PENDING':
            raise ValidationError("Escrow can only be created for PENDING transactions.")
        if self.amount != self.transaction.amount:
            raise ValidationError("Escrow amount must match transaction amount.")
        budget_range = self.transaction.client.client_profile.budget_range
        if budget_range == 'LOW' and self.amount > 5000:
            raise ValidationError(f"Escrow amount {self.amount} exceeds client's LOW budget range ($0 - $5,000)")
        elif budget_range == 'MEDIUM' and self.amount > 20000:
            raise ValidationError(f"Escrow amount {self.amount} exceeds client's MEDIUM budget range ($5,001 - $20,000)")
        try:
            client_wallet = self.transaction.client.wallet
            if client_wallet.balance < self.amount:
                raise ValidationError("Insufficient funds in client's wallet.")
        except Wallet.DoesNotExist:
            raise ValidationError("Client must have a wallet.")

    def release(self):
        if self.status != 'HELD' and self.status != 'DISPUTED':
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
        if self.status != 'HELD' and self.status != 'DISPUTED':
            raise ValidationError(f"Cannot refund escrow in {self.status} status.")
        try:
            client_wallet = self.transaction.client.wallet
            client_wallet.deposit(self.amount)
            self.status = 'REFUNDED'
            self.save()
        except Wallet.DoesNotExist:
            raise ValidationError("Client must have a wallet.")

    def dispute(self, user, reason):
        if self.status != 'HELD':
            raise ValidationError(f"Cannot dispute escrow in {self.status} status.")
        if user != self.transaction.client and user != self.transaction.freelancer:
            raise ValidationError("Only the client or freelancer can raise a dispute.")
        self.status = 'DISPUTED'
        self.save()
        EscrowDispute.objects.create(
            escrow=self,
            raised_by=user,
            reason=reason
        )

    def __str__():
        return f"Escrow for Transaction {self.transaction.id} (Amount: ${self.amount}, Status: {self.status})"

class EscrowDispute(models.Model):
    escrow = models.ForeignKey(
        Escrow,
        on_delete=models.CASCADE,
        related_name='disputes',
        help_text="The escrow associated with this dispute"
    )
    raised_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='raised_disputes',
        help_text="User who raised the dispute"
    )
    reason = models.TextField(
        max_length=1000,
        help_text="Reason for the dispute"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('OPEN', 'Open'),
            ('RESOLVED', 'Resolved'),
            ('CANCELLED', 'Cancelled')
        ],
        default='OPEN',
        help_text="Dispute status"
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_disputes',
        limit_choices_to={'is_staff': True},
        help_text="Admin who resolved the dispute"
    )
    resolution_notes = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Notes on dispute resolution"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Escrow Dispute"
        verbose_name_plural = "Escrow Disputes"

    def clean(self):
        if self.raised_by != self.escrow.transaction.client and self.raised_by != self.escrow.transaction.freelancer:
            raise ValidationError("Only the client or freelancer can raise a dispute.")
        if self.escrow.status != 'DISPUTED':
            raise ValidationError("Dispute can only be raised for escrows in DISPUTED status.")

    def resolve(self, admin, resolution, notes=""):
        if not admin.is_staff:
            raise ValidationError("Only admins can resolve disputes.")
        if self.status != 'OPEN':
            raise ValidationError(f"Cannot resolve dispute in {self.status} status.")
        if resolution not in ['RELEASE', 'REFUND']:
            raise ValidationError("Resolution must be 'RELEASE' or 'REFUND'.")
        self.status = 'RESOLVED'
        self.resolved_by = admin
        self.resolution_notes = notes
        self.save()
        if resolution == 'RELEASE':
            self.escrow.release()
        elif resolution == 'REFUND':
            self.escrow.refund()

    def cancel(self, user):
        if user != self.raised_by:
            raise ValidationError("Only the user who raised the dispute can cancel it.")
        if self.status != 'OPEN':
            raise ValidationError(f"Cannot cancel dispute in {self.status} status.")
        self.status = 'CANCELLED'
        self.escrow.status = 'HELD'
        self.escrow.save()
        self.save()

    def __str__(self):
        return f"Dispute for Escrow {self.escrow.id} raised by {self.raised_by.username} (Status: {self.status})"