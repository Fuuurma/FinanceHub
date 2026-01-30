# C-020: Advanced Alerts & Notifications System

**Priority:** P0 - CRITICAL  
**Assigned to:** Backend Coder  
**Estimated Time:** 14-18 hours  
**Dependencies:** C-008 (API Rate Limiting & Caching)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive alerts and notifications system for price movements, portfolio changes, news events, and market conditions.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 10.1 - Customization):**

- Alerts (price, % change, volume, news)
- Breaking news alerts
- Multiple notification channels (email, push, in-app, SMS)
- Alert history and management
- Alert templates and presets
- Conditional alerts (complex logic)

---

## ✅ CURRENT STATE

**What exists:**
- Basic data models for assets and portfolios
- Price tracking infrastructure
- News aggregation service

**What's missing:**
- Alert creation and management system
- Notification delivery system
- Multi-channel support (email, push, SMS)
- Alert condition monitoring engine
- Alert history and tracking

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (3-4 hours)

**Create `apps/backend/src/investments/models/alerts.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from .portfolio import Portfolio
from .asset import Asset

User = get_user_model()

class Alert(models.Model):
    """Alert definitions"""
    
    ALERT_TYPE_CHOICES = [
        ('price_above', 'Price Above'),
        ('price_below', 'Price Below'),
        ('percent_change', 'Percent Change'),
        ('volume_above', 'Volume Above'),
        ('news_mention', 'News Mention'),
        ('portfolio_change', 'Portfolio Value Change'),
        ('volatility', 'Volatility Alert'),
        ('rsi', 'RSI Level'),
        ('custom', 'Custom Condition'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('triggered', 'Triggered'),
        ('expired', 'Expired'),
    ]
    
    FREQUENCY_CHOICES = [
        ('once', 'One Time'),
        ('always', 'Every Time'),
        ('daily', 'Daily Max'),
        ('weekly', 'Weekly Max'),
    ]
    
    # Alert definition
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Target
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True)
    
    # Conditions
    condition_value = models.DecimalField(max_digits=20, decimal_places=4)  # e.g., $100, 5%
    condition_operator = models.CharField(max_length=5)  # >, <, >=, <=, ==
    condition_secondary_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    
    # Settings
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once')
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Notification channels
    send_email = models.BooleanField(default=True)
    send_push = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    send_in_app = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    
    # Message
    custom_message = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['asset', 'status']),
        ]

class AlertTrigger(models.Model):
    """History of triggered alerts"""
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='triggers')
    triggered_at = models.DateTimeField(auto_now_add=True)
    
    # What triggered it
    trigger_value = models.DecimalField(max_digits=20, decimal_places=4)
    asset_price = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    
    # Delivery status
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True)
    push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True)
    sms_sent = models.BooleanField(default=False)
    sms_sent_at = models.DateTimeField(null=True)
    
    # User action
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True)
    dismissed = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(null=True)
    
    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['alert', '-triggered_at']),
        ]

class NotificationPreference(models.Model):
    """User notification preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Email settings
    email_enabled = models.BooleanField(default=True)
    email_price_alerts = models.BooleanField(default=True)
    email_news_alerts = models.BooleanField(default=True)
    email_portfolio_alerts = models.BooleanField(default=True)
    email_digest = models.BooleanField(default=False)
    email_digest_frequency = models.CharField(max_length=20, default='daily')  # daily, weekly
    
    # Push settings
    push_enabled = models.BooleanField(default=True)
    push_price_alerts = models.BooleanField(default=True)
    push_news_alerts = models.BooleanField(default=True)
    push_portfolio_alerts = models.BooleanField(default=True)
    
    # SMS settings
    sms_enabled = models.BooleanField(default=False)
    sms_price_alerts = models.BooleanField(default=False)
    sms_only_critical = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
```

---

### **Phase 2: Alert Monitoring Service** (5-6 hours)

**Create `apps/backend/src/investments/services/alert_service.py`:**

```python
from typing import List, Dict
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from investments.models import Alert, AlertTrigger, Asset, PortfolioPosition
from investments.services.notification_service import NotificationService

class AlertMonitoringService:
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def check_price_alerts(self, asset_id: int, current_price: Decimal) -> List[AlertTrigger]:
        """
        Check all price alerts for an asset
        Returns list of triggered alerts
        """
        alerts = Alert.objects.filter(
            asset_id=asset_id,
            status='active',
            alert_type__in=['price_above', 'price_below']
        ).select_related('user')
        
        triggered = []
        
        for alert in alerts:
            should_trigger = False
            trigger_value = current_price
            
            if alert.alert_type == 'price_above':
                should_trigger = current_price >= alert.condition_value
            elif alert.alert_type == 'price_below':
                should_trigger = current_price <= alert.condition_value
            
            # Check frequency
            if should_trigger:
                if not self._should_trigger_alert(alert):
                    continue
                
                # Create trigger record
                trigger = AlertTrigger.objects.create(
                    alert=alert,
                    trigger_value=current_price,
                    asset_price=current_price
                )
                
                # Send notifications
                self._send_alert_notifications(alert, trigger)
                
                # Update alert
                alert.last_triggered_at = timezone.now()
                alert.trigger_count += 1
                
                # Handle frequency
                if alert.frequency == 'once':
                    alert.status = 'triggered'
                
                alert.save()
                
                triggered.append(trigger)
        
        return triggered
    
    def check_percent_change_alerts(self, asset_id: int, old_price: Decimal, new_price: Decimal) -> List[AlertTrigger]:
        """Check percent change alerts"""
        percent_change = ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
        
        alerts = Alert.objects.filter(
            asset_id=asset_id,
            status='active',
            alert_type='percent_change'
        )
        
        triggered = []
        
        for alert in alerts:
            should_trigger = False
            
            if alert.condition_operator == '>=':
                should_trigger = abs(percent_change) >= alert.condition_value
            elif alert.condition_operator == '>':
                should_trigger = abs(percent_change) > alert.condition_value
            
            if should_trigger and self._should_trigger_alert(alert):
                trigger = AlertTrigger.objects.create(
                    alert=alert,
                    trigger_value=Decimal(str(percent_change)),
                    asset_price=new_price
                )
                
                self._send_alert_notifications(alert, trigger)
                alert.last_triggered_at = timezone.now()
                alert.trigger_count += 1
                
                if alert.frequency == 'once':
                    alert.status = 'triggered'
                
                alert.save()
                triggered.append(trigger)
        
        return triggered
    
    def check_portfolio_value_alerts(self, portfolio_id: int, current_value: Decimal) -> List[AlertTrigger]:
        """Check portfolio value change alerts"""
        alerts = Alert.objects.filter(
            portfolio_id=portfolio_id,
            status='active',
            alert_type='portfolio_change'
        )
        
        triggered = []
        
        for alert in alerts:
            should_trigger = False
            
            if alert.condition_operator == '>=':
                should_trigger = current_value >= alert.condition_value
            elif alert.condition_operator == '<=':
                should_trigger = current_value <= alert.condition_value
            elif alert.condition_operator == '>':
                should_trigger = current_value > alert.condition_value
            elif alert.condition_operator == '<':
                should_trigger = current_value < alert.condition_value
            
            if should_trigger and self._should_trigger_alert(alert):
                trigger = AlertTrigger.objects.create(
                    alert=alert,
                    trigger_value=current_value
                )
                
                self._send_alert_notifications(alert, trigger)
                alert.last_triggered_at = timezone.now()
                alert.trigger_count += 1
                
                if alert.frequency == 'once':
                    alert.status = 'triggered'
                
                alert.save()
                triggered.append(trigger)
        
        return triggered
    
    def check_volume_alerts(self, asset_id: int, current_volume: int) -> List[AlertTrigger]:
        """Check volume alerts"""
        alerts = Alert.objects.filter(
            asset_id=asset_id,
            status='active',
            alert_type='volume_above'
        )
        
        triggered = []
        
        for alert in alerts:
            if current_volume >= alert.condition_value and self._should_trigger_alert(alert):
                trigger = AlertTrigger.objects.create(
                    alert=alert,
                    trigger_value=Decimal(str(current_volume))
                )
                
                self._send_alert_notifications(alert, trigger)
                alert.last_triggered_at = timezone.now()
                alert.trigger_count += 1
                
                if alert.frequency == 'once':
                    alert.status = 'triggered'
                
                alert.save()
                triggered.append(trigger)
        
        return triggered
    
    def _should_trigger_alert(self, alert: Alert) -> bool:
        """Check if alert should trigger based on frequency and quiet hours"""
        # Check quiet hours
        if alert.send_in_app:
            try:
                prefs = NotificationPreference.objects.get(user=alert.user)
                if prefs.quiet_hours_enabled:
                    current_time = timezone.now().astimezone(prefs.timezone)
                    if prefs.quiet_hours_start <= current_time.time() <= prefs.quiet_hours_end:
                        return False
            except NotificationPreference.DoesNotExist:
                pass
        
        # Check frequency
        if alert.frequency == 'once':
            return alert.trigger_count == 0
        elif alert.frequency == 'always':
            return True
        elif alert.frequency == 'daily':
            # Check if already triggered today
            today = timezone.now().date()
            return not AlertTrigger.objects.filter(
                alert=alert,
                triggered_at__date=today
            ).exists()
        elif alert.frequency == 'weekly':
            # Check if already triggered this week
            week_ago = timezone.now() - timedelta(days=7)
            return not AlertTrigger.objects.filter(
                alert=alert,
                triggered_at__gte=week_ago
            ).exists()
        
        return True
    
    def _send_alert_notifications(self, alert: Alert, trigger: AlertTrigger):
        """Send notifications through enabled channels"""
        message = self._generate_alert_message(alert, trigger)
        
        # Email
        if alert.send_email:
            try:
                self.notification_service.send_email(
                    user=alert.user,
                    subject=f"Alert Triggered: {alert.get_alert_type_display()}",
                    message=message,
                    alert_id=alert.id
                )
                trigger.email_sent = True
                trigger.email_sent_at = timezone.now()
            except Exception as e:
                print(f"Failed to send email: {e}")
        
        # Push notification
        if alert.send_push:
            try:
                self.notification_service.send_push(
                    user=alert.user,
                    title="Alert Triggered",
                    body=message,
                    alert_id=alert.id
                )
                trigger.push_sent = True
                trigger.push_sent_at = timezone.now()
            except Exception as e:
                print(f"Failed to send push: {e}")
        
        # SMS
        if alert.send_sms:
            try:
                self.notification_service.send_sms(
                    user=alert.user,
                    message=message
                )
                trigger.sms_sent = True
                trigger.sms_sent_at = timezone.now()
            except Exception as e:
                print(f"Failed to send SMS: {e}")
        
        trigger.save()
    
    def _generate_alert_message(self, alert: Alert, trigger: AlertTrigger) -> str:
        """Generate alert message"""
        if alert.custom_message:
            return alert.custom_message
        
        asset_symbol = alert.asset.symbol if alert.asset else "Portfolio"
        
        message = f"Alert: {alert.get_alert_type_display()}\n"
        message += f"Asset: {asset_symbol}\n"
        message += f"Condition: {alert.condition_operator} {alert.condition_value}\n"
        message += f"Current Value: {trigger.trigger_value}\n"
        message += f"Triggered at: {trigger.triggered_at}"
        
        return message
```

---

### **Phase 3: Notification Service** (3-4 hours)

**Create `apps/backend/src/investments/services/notification_service.py`:**

```python
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from decouple import config
import firebase_admin
from firebase_admin import messaging

class NotificationService:
    
    def __init__(self):
        # Initialize Twilio
        if config('TWILIO_ACCOUNT_SID', default=None):
            self.twilio_client = Client(
                config('TWILIO_ACCOUNT_SID'),
                config('TWILIO_AUTH_TOKEN')
            )
        else:
            self.twilio_client = None
        
        # Initialize Firebase (for push notifications)
        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app()
        except:
            pass
    
    def send_email(self, user, subject: str, message: str, alert_id: int = None):
        """Send email notification"""
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
    
    def send_push(self, user, title: str, body: str, alert_id: int = None):
        """Send push notification via Firebase"""
        # Get user's FCM tokens
        from investments.models import UserDevice
        tokens = UserDevice.objects.filter(user=user, active=True).values_list('fcm_token', flat=True)
        
        for token in tokens:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    token=token
                )
                messaging.send(message)
            except Exception as e:
                print(f"Failed to send push to {token}: {e}")
    
    def send_sms(self, user, message: str):
        """Send SMS notification via Twilio"""
        if not self.twilio_client:
            return
        
        phone_number = user.profile.phone_number
        if not phone_number:
            return
        
        try:
            self.twilio_client.messages.create(
                body=message,
                from_=config('TWILIO_PHONE_NUMBER'),
                to=phone_number
            )
        except Exception as e:
            print(f"Failed to send SMS: {e}")
```

---

### **Phase 4: API Endpoints** (2-3 hours)

**Create `apps/backend/src/api/alerts.py`:**

```python
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from investments.models import Alert, AlertTrigger, NotificationPreference
from investments.services.alert_service import AlertMonitoringService

router = Router(tags=['alerts'])

class AlertCreateSchema(Schema):
    alert_type: str
    asset_id: int = None
    portfolio_id: int = None
    condition_value: float
    condition_operator: str
    frequency: str = 'once'
    send_email: bool = True
    send_push: bool = False
    send_sms: bool = False
    custom_message: str = None

@router.post("/alerts")
def create_alert(request, data: AlertCreateSchema):
    """Create new alert"""
    alert = Alert.objects.create(
        user=request.auth,
        **data.dict()
    )
    return {"id": alert.id, "status": "created"}

@router.get("/alerts")
def list_alerts(request):
    """List user's alerts"""
    alerts = Alert.objects.filter(user=request.auth).select_related('asset', 'portfolio')
    return [{
        "id": a.id,
        "type": a.alert_type,
        "asset": a.asset.symbol if a.asset else None,
        "condition": f"{a.condition_operator} {a.condition_value}",
        "status": a.status,
        "created_at": a.created_at,
        "trigger_count": a.trigger_count
    } for a in alerts]

@router.get("/alerts/{alert_id}/triggers")
def alert_triggers(request, alert_id: int):
    """Get alert trigger history"""
    alert = get_object_or_404(Alert, id=alert_id, user=request.auth)
    triggers = alert.triggers.all()[:50]
    return [{
        "triggered_at": t.triggered_at,
        "trigger_value": t.trigger_value,
        "email_sent": t.email_sent,
        "push_sent": t.push_sent
    } for t in triggers]

@router.put("/alerts/{alert_id}/pause")
def pause_alert(request, alert_id: int):
    """Pause alert"""
    alert = get_object_or_404(Alert, id=alert_id, user=request.auth)
    alert.status = 'paused'
    alert.save()
    return {"status": "paused"}

@router.delete("/alerts/{alert_id}")
def delete_alert(request, alert_id: int):
    """Delete alert"""
    alert = get_object_or_404(Alert, id=alert_id, user=request.auth)
    alert.delete()
    return {"status": "deleted"}

@router.get("/notifications/preferences")
def get_preferences(request):
    """Get notification preferences"""
    prefs, _ = NotificationPreference.objects.get_or_create(user=request.auth)
    return {
        "email_enabled": prefs.email_enabled,
        "push_enabled": prefs.push_enabled,
        "sms_enabled": prefs.sms_enabled,
        "quiet_hours_enabled": prefs.quiet_hours_enabled
    }

@router.put("/notifications/preferences")
def update_preferences(request, data: dict):
    """Update notification preferences"""
    prefs, _ = NotificationPreference.objects.get_or_create(user=request.auth)
    for key, value in data.items():
        setattr(prefs, key, value)
    prefs.save()
    return {"status": "updated"}
```

---

### **Phase 5: Dramatiq Tasks for Monitoring** (1-2 hours)

**Create `apps/backend/src/investments/tasks/alert_tasks.py`:**

```python
import dramatiq
from investments.services.alert_service import AlertMonitoringService

@dramatiq.actor
def check_price_alerts(asset_id: int, price: float):
    """Check price alerts for asset"""
    service = AlertMonitoringService()
    service.check_price_alerts(asset_id, price)

@dramatiq.actor
def check_volume_alerts(asset_id: int, volume: int):
    """Check volume alerts for asset"""
    service = AlertMonitoringService()
    service.check_volume_alerts(asset_id, volume)

@dramatiq.actor
def check_portfolio_alerts(portfolio_id: int, value: float):
    """Check portfolio value alerts"""
    service = AlertMonitoringService()
    service.check_portfolio_value_alerts(portfolio_id, value)
```

---

## 📋 DELIVERABLES

- [ ] Alert, AlertTrigger, NotificationPreference models
- [ ] AlertMonitoringService with 5 check methods
- [ ] NotificationService with email, push, SMS support
- [ ] 7 API endpoints for alert management
- [ ] Dramatiq tasks for async monitoring
- [ ] Database migrations
- [ ] Unit tests
- [ ] API documentation

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Price alerts trigger when asset crosses threshold
- [ ] Percent change alerts trigger on specified % movement
- [ ] Volume alerts trigger on high volume
- [ ] Portfolio value alerts trigger on value changes
- [ ] Notifications sent via email, push, and SMS
- [ ] Alert frequency controls work (once, always, daily, weekly)
- [ ] Quiet hours respected
- [ ] Alert history tracked and viewable
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Alert processing time <500ms
- Notification delivery rate >95%
- Support for 1000+ concurrent alerts
- Alert triggers processed within 5 seconds of price change

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/020-alerts-notifications-system.md
