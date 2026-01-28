import uuid
from django.db import models
from django.utils import timezone
from users.models.user import User


class AlertType(models.TextChoices):
    PRICE_ABOVE = 'price_above', 'Price Above'
    PRICE_BELOW = 'price_below', 'Price Below'
    PERCENTAGE_CHANGE = 'percentage_change', 'Percentage Change'
    RSI_OVERBOUGHT = 'rsi_overbought', 'RSI Overbought'
    RSI_OVERSOLD = 'rsi_oversold', 'RSI Oversold'
    MACD_CROSSOVER = 'macd_crossover', 'MACD Crossover'
    MA_CROSSOVER = 'ma_crossover', 'Moving Average Crossover'
    VOLUME_SPIKE = 'volume_spike', 'Volume Spike'
    BOLLINGER_BREACH = 'bollinger_breach', 'Bollinger Band Breach'
    PATTERN_COMPLETION = 'pattern_completion', 'Pattern Completion'


class AlertStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    PAUSED = 'paused', 'Paused'
    TRIGGERED = 'triggered', 'Triggered'
    EXPIRED = 'expired', 'Expired'
    DELETED = 'deleted', 'Deleted'


class DeliveryChannel(models.TextChoices):
    WEBSOCKET = 'websocket', 'WebSocket'
    EMAIL = 'email', 'Email'
    PUSH = 'push', 'Push Notification'


class Alert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    alert_type = models.CharField(max_length=50, choices=AlertType.choices)
    symbol = models.CharField(max_length=20)
    
    condition_value = models.DecimalField(max_digits=20, decimal_places=8)
    condition_operator = models.CharField(max_length=10, default='>=')
    
    status = models.CharField(max_length=20, choices=AlertStatus.choices, default=AlertStatus.ACTIVE)
    
    priority = models.IntegerField(default=5)
    
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    triggered_count = models.IntegerField(default=0)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    
    delivery_channels = models.JSONField(default=list, blank=True)
    
    cooldown_seconds = models.IntegerField(default=300)
    last_notified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'investments_alert'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['symbol', 'status']),
            models.Index(fields=['alert_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.symbol} - {self.alert_type})"
    
    @property
    def is_valid(self) -> bool:
        if self.status != AlertStatus.ACTIVE:
            return False
        
        now = timezone.now()
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if now < self.valid_from:
            return False
        
        return True
    
    def should_trigger(self, current_value: float) -> bool:
        if not self.is_valid:
            return False
        
        value = float(self.condition_value)
        
        if self.condition_operator == '>=':
            return current_value >= value
        elif self.condition_operator == '>':
            return current_value > value
        elif self.condition_operator == '<=':
            return current_value <= value
        elif self.condition_operator == '<':
            return current_value < value
        elif self.condition_operator == '==':
            return current_value == value
        
        return False
    
    def can_notify(self) -> bool:
        if not self.is_valid:
            return False
        
        if not self.last_notified_at:
            return True
        
        cooldown = timezone.timedelta(seconds=self.cooldown_seconds)
        return timezone.now() >= self.last_notified_at + cooldown
    
    def trigger(self):
        self.triggered_count += 1
        self.last_triggered_at = timezone.now()
        self.last_notified_at = timezone.now()
        self.save(update_fields=['triggered_count', 'last_triggered_at', 'last_notified_at', 'updated_at'])


class AlertHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='history')
    
    triggered_at = models.DateTimeField(default=timezone.now)
    trigger_value = models.DecimalField(max_digits=20, decimal_places=8)
    
    condition_met = models.BooleanField()
    notification_sent = models.BooleanField(default=False)
    notification_channels = models.JSONField(default=list, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'investments_alert_history'
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['alert', 'triggered_at']),
        ]
    
    def __str__(self):
        return f"Alert {self.alert.name} triggered at {self.triggered_at}"


class AlertNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_history = models.ForeignKey(AlertHistory, on_delete=models.CASCADE, related_name='notifications')
    
    channel = models.CharField(max_length=20, choices=DeliveryChannel.choices)
    
    status = models.CharField(max_length=20, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'investments_alert_notification'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification {self.id} via {self.channel}"


class AlertTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_templates')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    alert_type = models.CharField(max_length=50, choices=AlertType.choices)
    symbol_pattern = models.CharField(max_length=200, blank=True)
    
    condition_template = models.JSONField()
    default_value = models.DecimalField(max_digits=20, decimal_places=8)
    
    default_priority = models.IntegerField(default=5)
    default_cooldown = models.IntegerField(default=300)
    default_channels = models.JSONField(default=list)
    
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'investments_alert_template'
    
    def __str__(self):
        return f"{self.name} ({self.alert_type})"
