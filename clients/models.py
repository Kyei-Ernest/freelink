from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class ClientProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='client_profile',
        limit_choices_to={'is_client': True}
    )
    company_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the client's company or organization"
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Industry or sector (e.g., Technology, Healthcare)"
    )
    project_types = models.CharField(
        max_length=200,
        blank=True,
        help_text="Preferred project types (e.g., Web Development, Mobile Apps)"
    )
    budget_range = models.CharField(
        max_length=50,
        choices=[
            ('LOW', '₵0 - ₵5,000'),
            ('MEDIUM', '₵5,001 - ₵20,000'),
            ('HIGH', '₵20,001+')
        ],
        default='LOW',
        help_text="Typical project budget range"
    )
    preferred_communication = models.CharField(
        max_length=50,
        choices=[
            ('EMAIL', 'Email'),
            ('PHONE', 'Phone'),
            ('VIDEO_CALL', 'Video Call'),
            ('CHAT', 'Chat')
        ],
        default='EMAIL',
        help_text="Preferred communication method"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"

    def clean(self):
        # Ensure the associated user is a client
        if not self.user.is_client:
            raise ValidationError("Only users with is_client=True can have a client profile.")

    def __str__(self):
        return f"Client Profile for {self.user.username}"

    def get_project_types_list(self):
        """Helper method to return project types as a list."""
        return [ptype.strip() for ptype in self.project_types.split(',') if ptype.strip()]