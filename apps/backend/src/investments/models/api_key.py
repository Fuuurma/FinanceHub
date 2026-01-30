from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from investments.models.data_provider import DataProvider
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel

class APIKeyStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    RATE_LIMITED = "rate_limited", "Rate Limited"
    DISABLED = "disabled", "Disabled"
    EXPIRED = "expired", "Expired"

class APIKey(UUIDModel, TimestampedModel):
    provider = models.ForeignKey(
        DataProvider,
        on_delete=models.CASCADE,
        related_name="api_keys"
    )
    name = models.CharField(max_length=100)
    key_value = models.CharField(max_length=500)
    key_type = models.CharField(
        max_length=50,
        choices=[("free", "Free"), ("basic", "Basic"), ("pro", "Pro"), ("enterprise", "Enterprise")],
        default="free"
    )
    status = models.CharField(
        max_length=20,
        choices=APIKeyStatus.choices,
        default=APIKeyStatus.ACTIVE
    )
    rate_limit_per_minute = models.PositiveIntegerField(null=True, blank=True)
    rate_limit_daily = models.PositiveIntegerField(null=True, blank=True)
    priority = models.PositiveSmallIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    usage_today = models.PositiveIntegerField(default=0)
    usage_today_reset = models.DateTimeField(auto_now_add=True)
    usage_this_hour = models.PositiveIntegerField(default=0)
    usage_this_hour_reset = models.DateTimeField(auto_now_add=True)
    total_usage_lifetime = models.PositiveBigIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    consecutive_failures = models.PositiveSmallIntegerField(default=0)
    auto_recover_after_minutes = models.PositiveSmallIntegerField(default=60)
    max_consecutive_failures = models.PositiveSmallIntegerField(default=5)
    metadata = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = "api_keys"
        unique_together = ("provider", "name")
        ordering = ["provider", "priority", "id"]
        indexes = [
            models.Index(fields=["provider", "status", "priority"]),
            models.Index(fields=["status", "last_used_at"]),
            models.Index(fields=["provider", "last_used_at"]),
        ]
    
    def __str__(self):
        return f"{self.provider.name} - {self.name} ({self.status})"
    
    def is_available(self) -> bool:
        return self.status == APIKeyStatus.ACTIVE
    
    def increment_usage(self) -> None:
        from django.utils import timezone
        now = timezone.now()
        
        if (now - self.usage_today_reset).days >= 1:
            self.usage_today = 0
            self.usage_today_reset = now
        
        if (now - self.usage_this_hour_reset).seconds >= 3600:
            self.usage_this_hour = 0
            self.usage_this_hour_reset = now
        
        self.usage_today += 1
        self.usage_this_hour += 1
        self.total_usage_lifetime += 1
        self.last_used_at = now
        self.save(update_fields=[
            "usage_today", "usage_today_reset",
            "usage_this_hour", "usage_this_hour_reset",
            "total_usage_lifetime", "last_used_at"
        ])
    
    def record_success(self) -> None:
        from django.utils import timezone
        self.last_success_at = timezone.now()
        self.consecutive_failures = 0
        self.save(update_fields=["last_success_at", "consecutive_failures"])
    
    def record_failure(self, error_type: str = "unknown") -> None:
        from django.utils import timezone
        now = timezone.now()
        self.last_failure_at = now
        self.consecutive_failures += 1
        
        if self.consecutive_failures >= self.max_consecutive_failures:
            self.status = APIKeyStatus.DISABLED
        
        self.save(update_fields=["last_failure_at", "consecutive_failures", "status"])
    
    def mark_rate_limited(self) -> None:
        self.status = APIKeyStatus.RATE_LIMITED
        self.save(update_fields=["status"])
