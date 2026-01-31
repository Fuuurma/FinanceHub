"""
Alert Models
Alert definitions and notification tracking.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Alert(models.Model):
    """Alert definitions for price movements, portfolio changes, etc."""

    ALERT_TYPE_CHOICES = [
        ('price_above', 'Price Above'),
        ('price_below', 'Price Below'),
        ('percent_change', 'Percent Change'),
        ('volume_above', 'Volume Above'),
        ('news_mention', 'News Mention'),
        ('portfolio_change', 'Portfolio Value Change'),
        ('volatility', 'Volatility Alert'),
        ('rsi', 'RSI Level'),
        ('earning_above', 'Earnings Above Estimate'),
        ('earning_below', 'Earnings Below Estimate'),
        ('dividend', 'Dividend Announced'),
        ('custom', 'Custom Condition'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('triggered', 'Triggered'),
        ('expired', 'Expired'),
        ('deleted', 'Deleted'),
    ]

    FREQUENCY_CHOICES = [
        ('once', 'One Time'),
        ('always', 'Every Time'),
        ('hourly', 'Hourly Max'),
        ('daily', 'Daily Max'),
        ('weekly', 'Weekly Max'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')

    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    name = models.CharField(max_length=200)

    asset = models.ForeignKey(
        'Asset', on_delete=models.CASCADE, null=True, blank=True, related_name='alerts'
    )
    portfolio = models.ForeignKey(
        'Portfolio', on_delete=models.CASCADE, null=True, blank=True, related_name='alerts'
    )

    condition_value = models.DecimalField(max_digits=20, decimal_places=4)
    condition_operator = models.CharField(max_length=5, default='>=')
    condition_secondary_value = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True
    )

    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once')
    expires_at = models.DateTimeField(null=True, blank=True)

    send_email = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_in_app = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)

    custom_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['asset', 'status']),
            models.Index(fields=['user', 'alert_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.alert_type}) - {self.user.username}"

    @property
    def is_expired(self):
        if self.expires_at and self.expires_at < timezone.now():
            return True
        return False

    @property
    def can_trigger(self):
        if self.status != 'active':
            return False
        if self.is_expired:
            return False
        return True


class AlertTrigger(models.Model):
    """History of triggered alerts."""

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='triggers')

    triggered_at = models.DateTimeField(auto_now_add=True)
    trigger_value = models.DecimalField(max_digits=20, decimal_places=4)
    asset_price = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    asset_name = models.CharField(max_length=200, blank=True)

    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    email_error = models.TextField(blank=True)

    push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    push_error = models.TextField(blank=True)

    sms_sent = models.BooleanField(default=False)
    sms_sent_at = models.DateTimeField(null=True, blank=True)
    sms_error = models.TextField(blank=True)

    in_app_sent = models.BooleanField(default=False)
    in_app_sent_at = models.DateTimeField(null=True, blank=True)

    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    dismissed = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['alert', 'triggered_at']),
            models.Index(fields=['viewed', 'dismissed']),
        ]

    def __str__(self):
        return f"Triggered {self.alert.name} at {self.triggered_at}"


class NotificationPreference(models.Model):
    """User notification preferences."""

    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_preferences')

    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    alert_type = models.CharField(max_length=30, choices=Alert.ALERT_TYPE_CHOICES)
    enabled = models.BooleanField(default=True)
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'channel', 'alert_type']

    def __str__(self):
        return f"{self.user.username} - {self.channel} for {self.alert_type}"


class Notification(models.Model):
    """In-app notifications."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    message = models.TextField()

    related_asset = models.ForeignKey(
        'Asset', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications'
    )
    related_alert_trigger = models.ForeignKey(
        AlertTrigger, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications'
    )

    priority = models.CharField(max_length=20, default='normal')
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read', 'created_at']),
            models.Index(fields=['notification_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
