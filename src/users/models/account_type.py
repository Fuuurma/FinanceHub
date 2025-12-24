from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class AccountType(UUIDModel, TimestampedModel):
    """Account type model (Individual, Business, Premium, etc.)"""
    
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique account type code"
    )
    name = models.CharField(
        max_length=100,
        help_text="Human-readable type name"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of this account type"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this account type is available"
    )
    features = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON object containing feature flags"
    )
    limits = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON object containing usage limits"
    )
    price_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Monthly subscription price"
    )
    price_yearly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Yearly subscription price"
    )
    trial_days = models.IntegerField(
        default=0,
        help_text="Number of trial days for this account type"
    )
    priority = models.IntegerField(
        default=0,
        help_text="Display priority"
    )

    class Meta:
        db_table = 'account_types'
        verbose_name = 'Account Type'
        verbose_name_plural = 'Account Types'
        ordering = ['-priority', 'name']

    def __str__(self):
        return self.name