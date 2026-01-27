from django.db import models
from investments.models.api_key import APIKey
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel

class APIKeyUsageLog(UUIDModel, TimestampedModel):
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        related_name="usage_logs"
    )
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10, default="GET")
    status_code = models.PositiveIntegerField()
    success = models.BooleanField()
    response_time_ms = models.PositiveIntegerField()
    error_type = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    request_params = models.JSONField(default=dict, blank=True)
    response_size_bytes = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = "api_key_usage_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["api_key", "-created_at"]),
            models.Index(fields=["api_key", "success"]),
            models.Index(fields=["-created_at"]),
        ]
    
    def __str__(self):
        return f"{self.api_key} - {self.endpoint} ({'OK' if self.success else 'FAIL'})"
