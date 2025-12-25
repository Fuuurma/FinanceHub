from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models.user_manager import UserManager
from utils.helpers.get_defaults_user import (
    get_default_account_type,
    get_default_user_status,
)
from utils.helpers.soft_delete_model import SoftDeleteModel

from django.core.validators import EmailValidator

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class User(
    AbstractBaseUser, PermissionsMixin, UUIDModel, TimestampedModel, SoftDeleteModel
):
    """Custom User model with email as username"""

    # Basic Information
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        db_index=True,
        help_text="User's email address (used for login)",
    )
    username = models.CharField(
        max_length=150, unique=True, db_index=True, help_text="Unique username"
    )
    first_name = models.CharField(
        max_length=150, blank=True, help_text="User's first name"
    )
    last_name = models.CharField(
        max_length=150, blank=True, help_text="User's last name"
    )

    # Status & Type
    # Status & Type → use strings
    status = models.ForeignKey(
        "UserStatus",
        on_delete=models.PROTECT,
        related_name="users",
        default=get_default_user_status,
        help_text="Current account status",
    )
    account_type = models.ForeignKey(
        "AccountType",
        on_delete=models.PROTECT,
        related_name="users",
        default=get_default_account_type,
        help_text="Account type/tier",
    )

    # Roles
    roles = models.ManyToManyField(
        "Role",
        related_name="users",
        blank=True,
        help_text="User's assigned roles",
    )

    # Verification & Security
    is_email_verified = models.BooleanField(
        default=False, help_text="Whether email has been verified"
    )
    email_verified_at = models.DateTimeField(
        null=True, blank=True, help_text="When email was verified"
    )
    is_phone_verified = models.BooleanField(
        default=False, help_text="Whether phone has been verified"
    )
    phone_verified_at = models.DateTimeField(
        null=True, blank=True, help_text="When phone was verified"
    )
    two_factor_enabled = models.BooleanField(
        default=False, help_text="Whether 2FA is enabled"
    )
    two_factor_secret = models.CharField(
        max_length=32, blank=True, help_text="2FA secret key (encrypted)"
    )

    # Account Security
    failed_login_attempts = models.IntegerField(
        default=0, help_text="Number of consecutive failed login attempts"
    )
    account_locked_until = models.DateTimeField(
        null=True, blank=True, help_text="Account locked until this time"
    )
    password_changed_at = models.DateTimeField(
        auto_now_add=True, help_text="When password was last changed"
    )
    must_change_password = models.BooleanField(
        default=False, help_text="Whether user must change password on next login"
    )

    # Login Tracking
    last_login_at = models.DateTimeField(
        null=True, blank=True, help_text="Last successful login time"
    )
    last_login_ip = models.GenericIPAddressField(
        null=True, blank=True, help_text="Last login IP address"
    )
    last_activity_at = models.DateTimeField(
        null=True, blank=True, help_text="Last activity timestamp"
    )

    # Django Admin
    is_staff = models.BooleanField(
        default=False, help_text="Whether user can access admin site"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether user account is active"
    )

    # Subscription
    subscription_started_at = models.DateTimeField(
        null=True, blank=True, help_text="When subscription started"
    )
    subscription_expires_at = models.DateTimeField(
        null=True, blank=True, help_text="When subscription expires"
    )
    trial_ends_at = models.DateTimeField(
        null=True, blank=True, help_text="When trial period ends"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Additional user metadata"
    )
    preferences = models.JSONField(
        default=dict, blank=True, help_text="User preferences"
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["username", "is_active"]),
            models.Index(fields=["status", "is_active"]),
            models.Index(fields=["account_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["last_login_at"]),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self):
        """Return user's first name"""
        return self.first_name or self.username

    @property
    def is_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False

    @property
    def is_subscription_active(self):
        """Check if subscription is active"""
        if self.subscription_expires_at:
            return timezone.now() < self.subscription_expires_at
        return False

    @property
    def is_trial_active(self):
        """Check if trial is active"""
        if self.trial_ends_at:
            return timezone.now() < self.trial_ends_at
        return False

    def has_permission(self, permission_code: str) -> bool:
        """Check if user has a specific permission through their roles"""
        if self.is_superuser:
            return True

        return self.roles.filter(
            permissions__code=permission_code,
            permissions__is_active=True,
            is_active=True,
        ).exists()

    def get_permissions(self):
        """Get all permissions for this user"""
        from users.models.permission import Permission

        if self.is_superuser:
            return Permission.objects.filter(is_active=True)

        return Permission.objects.filter(
            roles__users=self, roles__is_active=True, is_active=True
        ).distinct()
