from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class LoginHistory(UUIDModel, TimestampedModel):
    """Login attempt history"""

    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"

    LOGIN_STATUS_CHOICES = [
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
        (BLOCKED, "Blocked"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="login_history",
        null=True,
        blank=True,
        help_text="Associated user (null for failed attempts)",
    )
    email = models.EmailField(db_index=True, help_text="Email used for login attempt")
    status = models.CharField(
        max_length=20,
        choices=LOGIN_STATUS_CHOICES,
        db_index=True,
        help_text="Login attempt status",
    )
    failure_reason = models.CharField(
        max_length=200, blank=True, help_text="Reason for failure"
    )

    # Request Information
    ip_address = models.GenericIPAddressField(help_text="IP address of login attempt")
    user_agent = models.TextField(blank=True, help_text="Browser user agent")
    device_type = models.CharField(max_length=50, blank=True, help_text="Device type")

    # Location
    country = models.CharField(max_length=2, blank=True, help_text="Country code")
    city = models.CharField(max_length=100, blank=True, help_text="City name")

    # Two-Factor
    two_factor_used = models.BooleanField(
        default=False, help_text="Whether 2FA was used"
    )

    class Meta:
        db_table = "login_history"
        verbose_name = "Login History"
        verbose_name_plural = "Login History"
        indexes = [
            models.Index(fields=["user", "status", "created_at"]),
            models.Index(fields=["email", "created_at"]),
            models.Index(fields=["ip_address", "created_at"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.status.title()} login for {self.email}"
