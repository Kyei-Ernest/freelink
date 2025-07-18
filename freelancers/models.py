from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class FreelancerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='freelancer_profile',
        limit_choices_to={'is_freelancer': True}
    )
    bio = models.TextField(max_length=1000, blank=True, help_text="A short description of the freelancer")
    skills = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated list of skills (e.g., Python, Django, JavaScript)"
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True,
        help_text="Hourly rate in USD"
    )
    portfolio_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Link to portfolio or personal website"
    )
    availability = models.CharField(
        max_length=50,
        choices=[
            ('FULL_TIME', 'Full Time'),
            ('PART_TIME', 'Part Time'),
            ('NOT_AVAILABLE', 'Not Available')
        ],
        default='NOT_AVAILABLE',
        help_text="Current availability status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Freelancer Profile"
        verbose_name_plural = "Freelancer Profiles"

    def clean(self):
        # Ensure the associated user is a freelancer
        if not self.user.is_freelancer:
            raise ValidationError("Only users with is_freelancer=True can have a freelancer profile.")

    def __str__(self):
        return f"Freelancer Profile for {self.user.username}"

    def get_skills_list(self):
        """Helper method to return skills as a list."""
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]