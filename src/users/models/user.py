from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

from users.models.role import Role
from users.models.user_manager import UserManager
from utils.helpers.soft_delete_model import SoftDeleteModel





# new 





class User(AbstractBaseUser, PermissionsMixin, UUIDModel, TimestampedModel, SoftDeleteModel):
    """Custom User model with email as username"""
    
    # Basic Information
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        db_index=True,
        help_text="User's email address (used for login)"
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        help_text="Unique username"
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="User's first name"
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="User's last name"
    )
    
    # Status & Type
    status = models.ForeignKey(
        UserStatus,
        on_delete=models.PROTECT,
        related_name='users',
        help_text="Current account status"
    )
    account_type = models.ForeignKey(
        AccountType,
        on_delete=models.PROTECT,
        related_name='users',
        help_text="Account type/tier"
    )
    
    # Roles & Permissions
    roles = models.ManyToManyField(
        Role,
        related_name='users',
        blank=True,
        help_text="User's assigned roles"
    )
    
    # Verification & Security
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Whether email has been verified"
    )
    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When email was verified"
    )
    is_phone_verified = models.BooleanField(
        default=False,
        help_text="Whether phone has been verified"
    )
    phone_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When phone was verified"
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        help_text="Whether 2FA is enabled"
    )
    two_factor_secret = models.CharField(
        max_length=32,
        blank=True,
        help_text="2FA secret key (encrypted)"
    )
    
    # Account Security
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    account_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account locked until this time"
    )
    password_changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When password was last changed"
    )
    must_change_password = models.BooleanField(
        default=False,
        help_text="Whether user must change password on next login"
    )
    
    # Login Tracking
    last_login_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful login time"
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Last login IP address"
    )
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last activity timestamp"
    )
    
    # Django Admin
    is_staff = models.BooleanField(
        default=False,
        help_text="Whether user can access admin site"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether user account is active"
    )
    
    # Subscription
    subscription_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When subscription started"
    )
    subscription_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When subscription expires"
    )
    trial_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When trial period ends"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional user metadata"
    )
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User preferences"
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['username', 'is_active']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['account_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['last_login_at']),
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
            is_active=True
        ).exists()
    
    def get_permissions(self):
        """Get all permissions for this user"""
        if self.is_superuser:
            from .role import Permission
            return Permission.objects.filter(is_active=True)
        
        from .role import Permission
        return Permission.objects.filter(
            roles__users=self,
            roles__is_active=True,
            is_active=True
        ).distinct()


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


# apps/users/models/session.py
"""User session and login history models"""
from django.db import models
from .base import UUIDModel, TimestampedModel
from .user import User


class UserSession(UUIDModel, TimestampedModel):
    """Active user session tracking"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="Associated user"
    )
    access_token = models.CharField(
        max_length=500,
        db_index=True,
        help_text="Access token"
    )
    refresh_token = models.CharField(
        max_length=500,
        unique=True,
        db_index=True,
        help_text="Refresh token"
    )
    expires_at = models.DateTimeField(
        db_index=True,
        help_text="When refresh token expires"
    )
    is_revoked = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether session has been revoked"
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When session was revoked"
    )
    
    # Device Information
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the session"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent"
    )
    device_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Device type (mobile, desktop, tablet)"
    )
    device_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Device name"
    )
    browser = models.CharField(
        max_length=100,
        blank=True,
        help_text="Browser name"
    )
    browser_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Browser version"
    )
    os = models.CharField(
        max_length=100,
        blank=True,
        help_text="Operating system"
    )
    os_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="OS version"
    )
    
    # Location
    country = models.CharField(
        max_length=2,
        blank=True,
        help_text="Country code"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City name"
    )
    
    # Activity
    last_activity_at = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        indexes = [
            models.Index(fields=['user', 'is_revoked']),
            models.Index(fields=['refresh_token', 'is_revoked']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session for {self.user.email}"
    
    @property
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() >= self.expires_at
    
    @property
    def is_valid(self):
        """Check if session is valid"""
        return not self.is_revoked and not self.is_expired


class LoginHistory(UUIDModel, TimestampedModel):
    """Login attempt history"""
    
    SUCCESS = 'success'
    FAILED = 'failed'
    BLOCKED = 'blocked'
    
    LOGIN_STATUS_CHOICES = [
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
        (BLOCKED, 'Blocked'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history',
        null=True,
        blank=True,
        help_text="Associated user (null for failed attempts)"
    )
    email = models.EmailField(
        db_index=True,
        help_text="Email used for login attempt"
    )
    status = models.CharField(
        max_length=20,
        choices=LOGIN_STATUS_CHOICES,
        db_index=True,
        help_text="Login attempt status"
    )
    failure_reason = models.CharField(
        max_length=200,
        blank=True,
        help_text="Reason for failure"
    )
    
    # Request Information
    ip_address = models.GenericIPAddressField(
        help_text="IP address of login attempt"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent"
    )
    device_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Device type"
    )
    
    # Location
    country = models.CharField(
        max_length=2,
        blank=True,
        help_text="Country code"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City name"
    )
    
    # Two-Factor
    two_factor_used = models.BooleanField(
        default=False,
        help_text="Whether 2FA was used"
    )
    
    class Meta:
        db_table = 'login_history'
        verbose_name = 'Login History'
        verbose_name_plural = 'Login History'
        indexes = [
            models.Index(fields=['user', 'status', 'created_at']),
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.status.title()} login for {self.email}"