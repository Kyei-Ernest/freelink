from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
import uuid

User = settings.AUTH_USER_MODEL

CONTRACT_STATUS_CHOICES = [
    ('draft', _('Draft')),
    ('pending_acceptance', _('Pending Acceptance')),
    ('active', _('Active')),
    ('in_review', _('In Review')),
    ('completed', _('Completed')),
    ('disputed', _('Disputed')),
    ('cancelled', _('Cancelled')),
]

# Escrow Status Choices
ESCROW_STATUS_CHOICES = [
    ('not_funded', _('Not Funded')),
    ('funded', _('Funded')),
    ('partially_funded', _('Partially Funded')),
    ('released', _('Released')),
    ('refunded', _('Refunded')),
]

# Dispute Status Choices
DISPUTE_STATUS_CHOICES = [
    ('open', _('Open')),
    ('under_review', _('Under Review')),
    ('resolved', _('Resolved')),
]

# Milestone Status Choices
MILESTONE_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('submitted', _('Submitted')),
    ('approved', _('Approved')),
    ('rejected', _('Rejected')),
    ('paid', _('Paid')),
]

class Contract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.OneToOneField(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='contract',
        unique=True
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contracts_as_client',
        limit_choices_to={'is_client': True}
    )
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contracts_as_freelancer',
        limit_choices_to={'is_freelancer': True}
    )
    terms = JSONField(default=dict)  # Structured terms for in-app display
    agreed_bid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS_CHOICES, default='draft')
    escrow_status = models.CharField(max_length=20, choices=ESCROW_STATUS_CHOICES, default='not_funded')
    escrow_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    expiry_date = models.DateTimeField(null=True, blank=True)  # For pending_acceptance auto-cancellation
    dispute_reason = models.TextField(null=True, blank=True)
    dispute_status = models.CharField(max_length=20, choices=DISPUTE_STATUS_CHOICES, null=True, blank=True)
    dispute_resolution = models.TextField(null=True, blank=True)
    client_rating = models.PositiveSmallIntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    freelancer_rating = models.PositiveSmallIntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    client_feedback = models.TextField(null=True, blank=True)
    freelancer_feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['job'], name='unique_job_contract')
        ]

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Contract: {self.job.title} ({self.client} ↔ {self.freelancer})"

class Milestone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='milestones')
    description = models.TextField()
    due_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=MILESTONE_STATUS_CHOICES, default='pending')
    submission_details = models.TextField(null=True, blank=True)
    approval_notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Milestone for Contract {self.contract.id} - {self.description[:50]}"

    class Meta:
        ordering = ['due_date']

class AuditTrail(models.Model):
    id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='audit_trails')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    action = models.CharField(max_length=100)
    details = JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audit {self.id} for Contract {self.contract.id} - {self.action}"

    class Meta:
        ordering = ['-timestamp']

class ContractDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='contract_documents/')
    description = models.CharField(max_length=255, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for Contract {self.contract.id} - {self.description or self.file.name}"
