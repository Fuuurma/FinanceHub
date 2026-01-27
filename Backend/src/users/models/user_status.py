from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class UserStatus(UUIDModel, TimestampedModel):
    """User account status model"""
    
    # Status codes
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    PENDING = 'pending'
    LOCKED = 'locked'
    BANNED = 'banned'
    
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique status code"
    )
    name = models.CharField(
        max_length=100,
        help_text="Human-readable status name"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of this status"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether users with this status can access the system"
    )
    can_login = models.BooleanField(
        default=True,
        help_text="Whether users with this status can log in"
    )
    color = models.CharField(
        max_length=7,
        default='#000000',
        help_text="Hex color for UI display"
    )
    priority = models.IntegerField(
        default=0,
        help_text="Display priority (higher = more important)"
    )

    class Meta:
        db_table = 'user_statuses'
        verbose_name = 'User Status'
        verbose_name_plural = 'User Statuses'
        ordering = ['-priority', 'name']

    def __str__(self):
        return self.name