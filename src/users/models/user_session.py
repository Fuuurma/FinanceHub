from django.db import models

from users.models.user import User
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from django.utils import timezone


class UserSession(UUIDModel, TimestampedModel):
    """Active user session tracking"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="Associated user",
    )
    access_token = models.CharField(
        max_length=500, db_index=True, help_text="Access token"
    )
    refresh_token = models.CharField(
        max_length=500, unique=True, db_index=True, help_text="Refresh token"
    )
    expires_at = models.DateTimeField(
        db_index=True, help_text="When refresh token expires"
    )
    is_revoked = models.BooleanField(
        default=False, db_index=True, help_text="Whether session has been revoked"
    )
    revoked_at = models.DateTimeField(
        null=True, blank=True, help_text="When session was revoked"
    )

    # Device Information
    ip_address = models.GenericIPAddressField(help_text="IP address of the session")
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent",
    )
    device_type = models.CharField(
        max_length=50, blank=True, help_text="Device type (mobile, desktop, tablet)"
    )
    device_name = models.CharField(max_length=200, blank=True, help_text="Device name")
    browser = models.CharField(max_length=100, blank=True, help_text="Browser name")
    browser_version = models.CharField(
        max_length=50, blank=True, help_text="Browser version"
    )
    os = models.CharField(max_length=100, blank=True, help_text="Operating system")
    os_version = models.CharField(max_length=50, blank=True, help_text="OS version")

    # Location
    country = models.CharField(max_length=2, blank=True, help_text="Country code")
    city = models.CharField(max_length=100, blank=True, help_text="City name")

    # Activity
    last_activity_at = models.DateTimeField(
        auto_now=True, help_text="Last activity timestamp"
    )

    class Meta:
        db_table = "user_sessions"
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        indexes = [
            models.Index(fields=["user", "is_revoked"]),
            models.Index(fields=["refresh_token", "is_revoked"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

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
