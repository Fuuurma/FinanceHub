from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models.user import User
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel

class UserProfile(UUIDModel, TimestampedModel):
    """Extended user profile information"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Associated user"
    )
    
    # Personal Information
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number"
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Date of birth"
    )
    gender = models.CharField(
        max_length=20,
        blank=True,
        help_text="Gender"
    )
    
    # Address
    address_line1 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Address line 1"
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Address line 2"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text="State/Province"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Postal/ZIP code"
    )
    country = models.CharField(
        max_length=2,
        blank=True,
        help_text="Country code (ISO 3166-1 alpha-2)"
    )
    
    # Professional
    company = models.CharField(
        max_length=200,
        blank=True,
        help_text="Company name"
    )
    job_title = models.CharField(
        max_length=150,
        blank=True,
        help_text="Job title"
    )
    
    # Profile
    bio = models.TextField(
        blank=True,
        help_text="User biography"
    )
    avatar = models.URLField(
        blank=True,
        help_text="Avatar URL"
    )
    website = models.URLField(
        blank=True,
        help_text="Personal website"
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text="User's timezone"
    )
    language = models.CharField(
        max_length=10,
        default='en',
        help_text="Preferred language code"
    )
    
    # Social Links
    social_links = models.JSONField(
        default=dict,
        blank=True,
        help_text="Social media links"
    )
    
    # Notifications
    notification_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Notification preferences"
    )
    
    # Privacy
    is_profile_public = models.BooleanField(
        default=False,
        help_text="Whether profile is publicly visible"
    )
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.email}"