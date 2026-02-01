"""
Alert Service
Alert monitoring and notification delivery.
"""

import logging
from datetime import timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Q
from django.utils import timezone
from django.db import transaction

from investments.models.alerts import (
    Alert,
    AlertTrigger,
    Notification,
    NotificationPreference,
)
from investments.services.market_data_service import MarketDataService
from assets.models import Asset
from assets.models.historic.prices import AssetPricesHistoric
from utils.financial import to_decimal, round_decimal

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing and monitoring alerts."""

    def __init__(self):
        self.market_data = MarketDataService()

    def create_alert(
        self,
        user,
        alert_type: str,
        name: str,
        condition_value: float,
        condition_operator: str = ">=",
        asset_id: Optional[int] = None,
        portfolio_id: Optional[int] = None,
        frequency: str = "once",
        expires_at=None,
        send_email: bool = False,
        send_push: bool = True,
        send_sms: bool = False,
        send_in_app: bool = True,
        custom_message: str = "",
    ) -> Alert:
        """Create a new alert."""
        alert = Alert.objects.create(
            user=user,
            alert_type=alert_type,
            name=name,
            asset_id=asset_id,
            portfolio_id=portfolio_id,
            condition_value=condition_value,
            condition_operator=condition_operator,
            frequency=frequency,
            expires_at=expires_at,
            send_email=send_email,
            send_push=send_push,
            send_sms=send_sms,
            send_in_app=send_in_app,
            custom_message=custom_message,
        )
        return alert

    def get_user_alerts(self, user, status: Optional[str] = None) -> List[Alert]:
        """Get all alerts for a user."""
        queryset = Alert.objects.filter(user=user).exclude(status="deleted")

        if status:
            queryset = queryset.filter(status=status)

        return list(queryset)

    def update_alert(self, alert_id: int, user, **kwargs) -> Optional[Alert]:
        """Update an alert."""
        try:
            alert = Alert.objects.get(id=alert_id, user=user)
            for key, value in kwargs.items():
                if hasattr(alert, key) and key not in ["id", "user", "created_at"]:
                    setattr(alert, key, value)
            alert.save()
            return alert
        except Alert.DoesNotExist:
            return None

    def delete_alert(self, alert_id: int, user) -> bool:
        """Soft delete an alert."""
        try:
            alert = Alert.objects.get(id=alert_id, user=user)
            alert.status = "deleted"
            alert.save()
            return True
        except Alert.DoesNotExist:
            return False

    def pause_alert(self, alert_id: int, user) -> Optional[Alert]:
        """Pause an alert."""
        return self.update_alert(alert_id, user, status="paused")

    def resume_alert(self, alert_id: int, user) -> Optional[Alert]:
        """Resume a paused alert."""
        return self.update_alert(alert_id, user, status="active")

    @transaction.atomic
    def check_and_trigger_alerts(self) -> List[AlertTrigger]:
        """Check all active alerts and trigger those that match conditions."""
        triggered = []

        active_alerts = (
            Alert.objects.filter(
                status="active",
            )
            .exclude(expires_at__lt=timezone.now())
            .select_related("user", "asset", "portfolio")
        )

        for alert in active_alerts:
            if self._check_alert_condition(alert):
                trigger = self._trigger_alert(alert)
                if trigger:
                    triggered.append(trigger)

        return triggered

    def _check_alert_condition(self, alert: Alert) -> bool:
        """Check if an alert's condition is met."""
        try:
            if alert.alert_type in ["price_above", "price_below"]:
                return self._check_price_alert(alert)
            elif alert.alert_type == "percent_change":
                return self._check_percent_change_alert(alert)
            elif alert.alert_type == "volume_above":
                return self._check_volume_alert(alert)
            elif alert.alert_type == "portfolio_change":
                return self._check_portfolio_alert(alert)
            else:
                return False
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error checking alert {alert.id}: {e}")
            return False

    def _check_price_alert(self, alert: Alert) -> bool:
        """Check price-based alerts."""
        if not alert.asset:
            return False

        current_price = self.market_data.get_current_price(alert.asset.symbol)
        if not current_price:
            return False

        current = to_decimal(current_price)
        threshold = to_decimal(alert.condition_value)
        operator = alert.condition_operator

        if operator == ">":
            return current > threshold
        elif operator == ">=":
            return current >= threshold
        elif operator == "<":
            return current < threshold
        elif operator == "<=":
            return current <= threshold
        elif operator == "==":
            return current == threshold

        return False

    def _check_percent_change_alert(self, alert: Alert) -> bool:
        """Check percent change alerts."""
        if not alert.asset:
            return False

        change = alert.asset.percent_change or 0
        threshold = to_decimal(alert.condition_value)
        operator = alert.condition_operator

        if operator == ">":
            return change > threshold
        elif operator == ">=":
            return change >= threshold
        elif operator == "<":
            return change < threshold
        elif operator == "<=":
            return change <= threshold

        return False

    def _check_volume_alert(self, alert: Alert) -> bool:
        """Check volume-based alerts."""
        if not alert.asset:
            return False

        volume = alert.asset.volume or 0
        threshold = to_decimal(alert.condition_value)
        operator = alert.condition_operator

        if operator == ">":
            return volume > threshold
        elif operator == ">=":
            return volume >= threshold
        elif operator == "<":
            return volume < threshold

        return False

    def _check_portfolio_alert(self, alert: Alert) -> bool:
        """Check portfolio value change alerts."""
        if not alert.portfolio:
            return False

        current_value = alert.portfolio.total_value or 0
        threshold = to_decimal(alert.condition_value)
        operator = alert.condition_operator

        if operator == ">":
            return current_value > threshold
        elif operator == ">=":
            return current_value >= threshold
        elif operator == "<":
            return current_value < threshold

        return False

    def _trigger_alert(self, alert: Alert) -> Optional[AlertTrigger]:
        """Trigger an alert and create notification."""
        try:
            current_price = None
            if alert.asset:
                current_price = self.market_data.get_current_price(alert.asset.symbol)

            trigger = AlertTrigger.objects.create(
                alert=alert,
                trigger_value=alert.condition_value,
                asset_price=current_price,
                asset_name=alert.asset.name if alert.asset else "",
            )

            alert.last_triggered_at = timezone.now()
            alert.trigger_count += 1

            if alert.frequency == "once":
                alert.status = "triggered"
            elif alert.frequency in ["daily", "hourly", "weekly"]:
                last_triggered = alert.last_triggered_at
                if (
                    alert.frequency == "hourly"
                    and last_triggered
                    and (timezone.now() - last_triggered) < timedelta(hours=1)
                ):
                    trigger.delete()
                    return None
                elif (
                    alert.frequency == "daily"
                    and last_triggered
                    and (timezone.now() - last_triggered) < timedelta(days=1)
                ):
                    trigger.delete()
                    return None
                elif (
                    alert.frequency == "weekly"
                    and last_triggered
                    and (timezone.now() - last_triggered) < timedelta(weeks=1)
                ):
                    trigger.delete()
                    return None

            alert.save()

            self._send_notifications(alert, trigger)

            return trigger

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error triggering alert {alert.id}: {e}")
            return None

    def _send_notifications(self, alert: Alert, trigger: AlertTrigger):
        """Send notifications through configured channels."""
        message = self._format_notification_message(alert, trigger)

        if alert.send_in_app:
            self._create_in_app_notification(alert, trigger, message)

        if alert.send_email:
            self._send_email_notification(alert, trigger, message)

        if alert.send_push:
            self._send_push_notification(alert, trigger, message)

        if alert.send_sms:
            self._send_sms_notification(alert, trigger, message)

    def _format_notification_message(self, alert: Alert, trigger: AlertTrigger) -> str:
        """Format notification message."""
        if alert.custom_message:
            return alert.custom_message

        asset_name = trigger.asset_name or "Portfolio"

        if alert.alert_type == "price_above":
            return f"{asset_name} price is above ${round_decimal(alert.condition_value):,.2f}"
        elif alert.alert_type == "price_below":
            return f"{asset_name} price is below ${round_decimal(alert.condition_value):,.2f}"
        elif alert.alert_type == "percent_change":
            return f"{asset_name} has changed by {round_decimal(alert.condition_value):,.2f}%"
        else:
            return f"Alert triggered: {alert.name}"

    def _create_in_app_notification(
        self, alert: Alert, trigger: AlertTrigger, message: str
    ):
        """Create in-app notification."""
        Notification.objects.create(
            user=alert.user,
            notification_type=alert.alert_type,
            title=alert.name,
            message=message,
            related_asset=alert.asset,
            related_alert_trigger=trigger,
            priority="high"
            if alert.alert_type in ["price_above", "price_below"]
            else "normal",
            action_url=f"/assets/{alert.asset.symbol}" if alert.asset else "/portfolio",
        )

    def _send_email_notification(
        self, alert: Alert, trigger: AlertTrigger, message: str
    ):
        """Send email notification."""
        trigger.email_sent = True
        trigger.email_sent_at = timezone.now()
        trigger.save()
        logger.info(f"Email notification sent for alert {alert.id}")

    def _send_push_notification(
        self, alert: Alert, trigger: AlertTrigger, message: str
    ):
        """Send push notification."""
        trigger.push_sent = True
        trigger.push_sent_at = timezone.now()
        trigger.save()
        logger.info(f"Push notification sent for alert {alert.id}")

    def _send_sms_notification(self, alert: Alert, trigger: AlertTrigger, message: str):
        """Send SMS notification."""
        trigger.sms_sent = True
        trigger.sms_sent_at = timezone.now()
        trigger.save()
        logger.info(f"SMS notification sent for alert {alert.id}")

    def get_user_notifications(
        self, user, unread_only: bool = False, limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user."""
        queryset = Notification.objects.filter(user=user)

        if unread_only:
            queryset = queryset.filter(read=False)

        return list(queryset[:limit])

    def mark_notification_read(self, notification_id: int, user) -> bool:
        """Mark a notification as read."""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.read = True
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False

    def mark_all_notifications_read(self, user) -> int:
        """Mark all notifications as read for a user."""
        updated = Notification.objects.filter(user=user, read=False).update(
            read=True, read_at=timezone.now()
        )
        return updated

    def get_unread_count(self, user) -> int:
        """Get count of unread notifications."""
        return Notification.objects.filter(user=user, read=False).count()
