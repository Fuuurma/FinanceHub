import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from django.utils import timezone

from utils.helpers.logger.logger import get_logger
from utils.services.cache_manager import get_cache_manager
from utils.services.data_orchestrator import get_data_orchestrator
from utils.financial import to_decimal
from investments.models.alert import (
    Alert,
    AlertHistory,
    AlertNotification,
    AlertType,
    AlertStatus,
    DeliveryChannel,
)

logger = get_logger(__name__)


class AlertEngine:
    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.orchestrator = get_data_orchestrator()
        self.pending_alerts: Dict[str, List[Alert]] = {}
        self._lock = asyncio.Lock()

    async def check_all_alerts(self) -> List[Dict[str, Any]]:
        triggered_alerts = []

        try:
            alerts = await self._get_active_alerts()

            for alert in alerts:
                try:
                    should_trigger = await self._check_alert(alert)

                    if should_trigger and alert.can_notify():
                        await self._trigger_alert(alert)

                        triggered_alerts.append(
                            {
                                "alert_id": str(alert.id),
                                "name": alert.name,
                                "symbol": alert.symbol,
                                "alert_type": alert.alert_type,
                                "triggered_at": timezone.now().isoformat(),
                                "condition_value": str(alert.condition_value),
                            }
                        )

                        logger.info(f"Alert triggered: {alert.name} ({alert.symbol})")

                except Exception as e:
                    logger.error(f"Error checking alert {alert.id}: {e}")

        except Exception as e:
            logger.error(f"Error in check_all_alerts: {e}")

        return triggered_alerts

    async def _get_active_alerts(self) -> List[Alert]:
        try:
            now = timezone.now()

            cache_key = f"active_alerts_{now.strftime('%Y%m%d%H%M')}"
            cached_alerts = await self.cache_manager.get("alerts", cache_key)

            if cached_alerts:
                alerts = []
                for alert_data in cached_alerts:
                    alert = Alert(**alert_data)
                    alerts.append(alert)
                return alerts

            alerts = (
                Alert.objects.filter(status=AlertStatus.ACTIVE, valid_from__lte=now)
                .exclude(valid_until__isnull=False, valid_until__lt=now)
                .order_by("-priority")[:1000]
            )

            alerts_list = [
                {
                    "id": str(alert.id),
                    "user_id": alert.user_id,
                    "name": alert.name,
                    "description": alert.description,
                    "alert_type": alert.alert_type,
                    "symbol": alert.symbol,
                    "condition_value": float(alert.condition_value),
                    "condition_operator": alert.condition_operator,
                    "status": alert.status,
                    "priority": alert.priority,
                    "cooldown_seconds": alert.cooldown_seconds,
                    "delivery_channels": alert.delivery_channels,
                }
                for alert in alerts
            ]

            await self.cache_manager.set("alerts", cache_key, value=alerts_list, ttl=60)

            return [
                Alert(
                    id=alert["id"],
                    user_id=alert["user_id"],
                    name=alert["name"],
                    alert_type=alert["alert_type"],
                    symbol=alert["symbol"],
                    condition_value=Decimal(str(alert["condition_value"])),
                    condition_operator=alert["condition_operator"],
                    status=alert["status"],
                    priority=alert["priority"],
                    cooldown_seconds=alert["cooldown_seconds"],
                    delivery_channels=alert["delivery_channels"],
                )
                for alert in alerts_list
            ]

        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []

    async def _check_alert(self, alert: Alert) -> bool:
        try:
            if alert.alert_type in [AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW]:
                return await self._check_price_alert(alert)

            elif alert.alert_type == AlertType.PERCENTAGE_CHANGE:
                return await self._check_percentage_alert(alert)

            elif alert.alert_type in [AlertType.RSI_OVERBOUGHT, AlertType.RSI_OVERSOLD]:
                return await self._check_rsi_alert(alert)

            elif alert.alert_type == AlertType.MACD_CROSSOVER:
                return await self._check_macd_alert(alert)

            elif alert.alert_type == AlertType.VOLUME_SPIKE:
                return await self._check_volume_alert(alert)

            elif alert.alert_type == AlertType.BOLLINGER_BREACH:
                return await self._check_bollinger_alert(alert)

            else:
                logger.warning(f"Unknown alert type: {alert.alert_type}")
                return False

        except Exception as e:
            logger.error(f"Error checking alert {alert.id}: {e}")
            return False

    async def _check_price_alert(self, alert: Alert) -> bool:
        try:
            response = await self.orchestrator.get_market_data(
                data_type="crypto_price"
                if alert.symbol.upper() in ["BTC", "ETH", "SOL"]
                else "stock_price",
                symbol=alert.symbol,
            )

            if not response.data:
                return False

            price = to_decimal(response.data.get("price", 0))
            return alert.should_trigger(price)

        except Exception as e:
            logger.error(f"Error checking price alert: {e}")
            return False

    async def _check_percentage_alert(self, alert: Alert) -> bool:
        try:
            response = await self.orchestrator.get_market_data(
                data_type="crypto_historical"
                if alert.symbol.upper() in ["BTC", "ETH", "SOL"]
                else "stock_historical",
                symbol=alert.symbol,
                params={"days": 2},
            )

            if not response.data or len(response.data) < 2:
                return False

            data = (
                response.data
                if isinstance(response.data, list)
                else response.data.get("results", [])
            )

            if len(data) < 2:
                return False

            current_price = to_decimal(data[-1].get("close", 0))
            previous_price = to_decimal(data[-2].get("close", 0))

            if previous_price == 0:
                return False

            percent_change = ((current_price - previous_price) / previous_price) * 100
            return alert.should_trigger(percent_change)

        except Exception as e:
            logger.error(f"Error checking percentage alert: {e}")
            return False

    async def _check_rsi_alert(self, alert: Alert) -> bool:
        try:
            from utils.services.technical_indicators import get_technical_indicators

            response = await self.orchestrator.get_market_data(
                data_type="crypto_historical", symbol=alert.symbol, params={"days": 90}
            )

            if not response.data:
                return False

            data = response.data if isinstance(response.data, list) else []

            indicators = get_technical_indicators()
            rsi_data = await indicators.calculate_rsi(data, period=14)

            if not rsi_data:
                return False

            current_rsi = rsi_data[-1].get("rsi", 50)

            if alert.alert_type == AlertType.RSI_OVERBOUGHT:
                return current_rsi >= 70
            elif alert.alert_type == AlertType.RSI_OVERSOLD:
                return current_rsi <= 30

            return False

        except Exception as e:
            logger.error(f"Error checking RSI alert: {e}")
            return False

    async def _check_macd_alert(self, alert: Alert) -> bool:
        try:
            from utils.services.technical_indicators import get_technical_indicators

            response = await self.orchestrator.get_market_data(
                data_type="crypto_historical", symbol=alert.symbol, params={"days": 90}
            )

            if not response.data:
                return False

            data = response.data if isinstance(response.data, list) else []

            indicators = get_technical_indicators()
            macd_data = await indicators.calculate_macd(data)

            if not macd_data:
                return False

            current = macd_data[-1]

            if current.get("macd") is None or current.get("signal") is None:
                return False

            macd_val = to_decimal(current["macd"])
            signal_val = to_decimal(current["signal"])

            return alert.should_trigger(macd_val - signal_val)

        except Exception as e:
            logger.error(f"Error checking MACD alert: {e}")
            return False

    async def _check_volume_alert(self, alert: Alert) -> bool:
        try:
            response = await self.orchestrator.get_market_data(
                data_type="crypto_historical"
                if alert.symbol.upper() in ["BTC", "ETH", "SOL"]
                else "stock_historical",
                symbol=alert.symbol,
                params={"days": 30},
            )

            if not response.data:
                return False

            data = (
                response.data
                if isinstance(response.data, list)
                else response.data.get("results", [])
            )

            if len(data) < 14:
                return False

            volumes = [to_decimal(d.get("volume", 0)) for d in data[-14:]]
            avg_volume = sum(volumes) / len(volumes)
            current_volume = volumes[-1]

            threshold_multiplier = to_decimal(alert.condition_value)

            return current_volume >= (avg_volume * threshold_multiplier)

        except Exception as e:
            logger.error(f"Error checking volume alert: {e}")
            return False

    async def _check_bollinger_alert(self, alert: Alert) -> bool:
        try:
            from utils.services.technical_indicators import get_technical_indicators

            response = await self.orchestrator.get_market_data(
                data_type="crypto_historical", symbol=alert.symbol, params={"days": 90}
            )

            if not response.data:
                return False

            data = response.data if isinstance(response.data, list) else []

            indicators = get_technical_indicators()
            bollinger_data = await indicators.calculate_bollinger_bands(data)

            if not bollinger_data:
                return False

            current = bollinger_data[-1]
            close_price = to_decimal(current.get("close", 0))
            upper_band = to_decimal(current.get("upper_band", 0))
            lower_band = to_decimal(current.get("lower_band", 0))

            if alert.alert_type == AlertType.BOLLINGER_BREACH:
                if upper_band > 0 and close_price >= upper_band:
                    return True
                if lower_band > 0 and close_price <= lower_band:
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking Bollinger alert: {e}")
            return False

    async def _trigger_alert(self, alert: Alert):
        try:
            alert.trigger()

            history = AlertHistory.objects.create(
                alert=alert,
                trigger_value=alert.condition_value,
                condition_met=True,
                notification_sent=False,
                notification_channels=alert.delivery_channels,
            )

            for channel in alert.delivery_channels:
                try:
                    await self._send_notification(history, channel)
                except Exception as e:
                    logger.error(f"Error sending notification via {channel}: {e}")

            history.notification_sent = True
            history.save(update_fields=["notification_sent"])

        except Exception as e:
            logger.error(f"Error triggering alert {alert.id}: {e}")

    async def _send_notification(self, history: AlertHistory, channel: str):
        try:
            notification = AlertNotification.objects.create(
                alert_history=history, channel=channel, status="pending"
            )

            if channel == DeliveryChannel.WEBSOCKET:
                await self._send_websocket_notification(history, notification)
            elif channel == DeliveryChannel.EMAIL:
                await self._send_email_notification(history, notification)
            elif channel == DeliveryChannel.PUSH:
                await self._send_push_notification(history, notification)

            notification.status = "sent"
            notification.sent_at = timezone.now()
            notification.save(update_fields=["status", "sent_at"])

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            notification.status = "failed"
            notification.error_message = str(e)
            notification.save(update_fields=["status", "error_message"])

    async def _send_websocket_notification(
        self, history: AlertHistory, notification: AlertNotification
    ):
        try:
            from utils.services.realtime_stream_manager import (
                get_real_time_stream_manager,
            )

            stream_manager = get_real_time_stream_manager()

            alert_data = {
                "type": "alert",
                "alert_id": str(history.alert.id),
                "name": history.alert.name,
                "symbol": history.alert.symbol,
                "alert_type": history.alert.alert_type,
                "triggered_at": history.triggered_at.isoformat(),
                "trigger_value": str(history.trigger_value),
            }

            if history.alert.symbol in stream_manager.subscribers:
                for callback in stream_manager.subscribers[history.alert.symbol]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(alert_data)
                        else:
                            callback(alert_data)
                    except Exception as e:
                        logger.error(f"Error in WebSocket callback: {e}")

        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {e}")
            raise

    async def _send_email_notification(
        self, history: AlertHistory, notification: AlertNotification
    ):
        try:
            subject = f"Alert Triggered: {history.alert.name}"
            body = f"""
Alert: {history.alert.name}
Symbol: {history.alert.symbol}
Type: {history.alert.alert_type}
Triggered At: {history.triggered_at}
Condition Value: {history.trigger_value}

This is an automated message from FinanceHub.
            """

            notification.metadata = {"subject": subject, "body": body}
            notification.save(update_fields=["metadata"])

        except Exception as e:
            logger.error(f"Error preparing email notification: {e}")
            raise

    async def _send_push_notification(
        self, history: AlertHistory, notification: AlertNotification
    ):
        try:
            notification.metadata = {
                "title": f"Alert: {history.alert.name}",
                "body": f"{history.alert.symbol} - {history.alert.alert_type}",
                "icon": "alert",
            }
            notification.save(update_fields=["metadata"])

        except Exception as e:
            logger.error(f"Error preparing push notification: {e}")
            raise

    async def create_alert(
        self,
        user_id: str,
        name: str,
        alert_type: str,
        symbol: str,
        condition_value: float,
        condition_operator: str = ">=",
        delivery_channels: Optional[List[str]] = None,
        priority: int = 5,
        cooldown_seconds: int = 300,
        valid_until: Optional[datetime] = None,
        description: Optional[str] = None,
    ) -> Alert:
        try:
            from users.models.user import User

            user = await User.objects.aget(id=user_id)

            alert = Alert.objects.create(
                user=user,
                name=name,
                alert_type=alert_type,
                symbol=symbol.upper(),
                condition_value=Decimal(str(condition_value)),
                condition_operator=condition_operator,
                delivery_channels=delivery_channels or [DeliveryChannel.WEBSOCKET],
                priority=priority,
                cooldown_seconds=cooldown_seconds,
                valid_until=valid_until,
                description=description,
            )

            await self._invalidate_cache()

            logger.info(f"Created alert: {alert.name} ({alert.id})")

            return alert

        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise

    async def update_alert(self, alert_id: str, **kwargs) -> Optional[Alert]:
        try:
            alert = await Alert.objects.aget(id=alert_id)

            for field, value in kwargs.items():
                if hasattr(alert, field):
                    setattr(alert, field, value)

            await alert.asave()

            await self._invalidate_cache()

            logger.info(f"Updated alert: {alert.name} ({alert.id})")

            return alert

        except Alert.DoesNotExist:
            logger.warning(f"Alert not found: {alert_id}")
            return None

    async def delete_alert(self, alert_id: str) -> bool:
        try:
            alert = await Alert.objects.aget(id=alert_id)
            alert.status = AlertStatus.DELETED
            await alert.asave()

            await self._invalidate_cache()

            logger.info(f"Deleted alert: {alert_id}")

            return True

        except Alert.DoesNotExist:
            logger.warning(f"Alert not found: {alert_id}")
            return False

    async def pause_alert(self, alert_id: str) -> bool:
        try:
            alert = await Alert.objects.aget(id=alert_id)
            alert.status = AlertStatus.PAUSED
            await alert.asave()

            await self._invalidate_cache()

            logger.info(f"Paused alert: {alert_id}")

            return True

        except Alert.DoesNotExist:
            return False

    async def resume_alert(self, alert_id: str) -> bool:
        try:
            alert = await Alert.objects.aget(id=alert_id)
            alert.status = AlertStatus.ACTIVE
            await alert.asave()

            await self._invalidate_cache()

            logger.info(f"Resumed alert: {alert_id}")

            return True

        except Alert.DoesNotExist:
            return False

    async def _invalidate_cache(self):
        try:
            await self.cache_manager.invalidate_pattern("active_alerts_")
            await self.cache_manager.invalidate_pattern("alerts_")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")

    def get_alert_statistics(self, user_id: str) -> Dict[str, Any]:
        from django.db.models import Count

        now = timezone.now()

        total_alerts = Alert.objects.filter(user_id=user_id).count()
        active_alerts = Alert.objects.filter(
            user_id=user_id, status=AlertStatus.ACTIVE
        ).count()

        triggered_today = Alert.objects.filter(
            user_id=user_id,
            last_triggered_at__gte=now.replace(hour=0, minute=0, second=0),
        ).count()

        alert_type_counts = (
            Alert.objects.filter(user_id=user_id)
            .values("alert_type")
            .annotate(count=Count("id"))
        )

        type_distribution = {
            item["alert_type"]: item["count"] for item in alert_type_counts
        }

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "triggered_today": triggered_today,
            "type_distribution": type_distribution,
        }


_alert_engine_instance: Optional[AlertEngine] = None


def get_alert_engine() -> AlertEngine:
    global _alert_engine_instance
    if _alert_engine_instance is None:
        _alert_engine_instance = AlertEngine()
    return _alert_engine_instance
