from typing import List, Optional
from datetime import datetime
from ninja import Router, Schema, Query
from django.shortcuts import get_object_or_404

from utils.helpers.logger.logger import get_logger
from utils.services.alert_engine import get_alert_engine
from utils.services.cache_manager import get_cache_manager
from investments.models.alert import (
    Alert, AlertHistory, AlertNotification,
    AlertType, AlertStatus, DeliveryChannel
)
from users.models.user import User
from utils.constants.api import (
    ALERT_LIST_LIMIT,
    ALERT_HISTORY_LIMIT,
    ALERT_COOLDOWN_SECONDS,
    ERROR_NOT_FOUND,
    ERROR_VALIDATION,
)

logger = get_logger(__name__)

router = Router(tags=["Alerts"])


class AlertCreateIn(Schema):
    name: str
    alert_type: str
    symbol: str
    condition_value: float
    condition_operator: str = '>='
    delivery_channels: Optional[List[str]] = None
    priority: int = 5
    cooldown_seconds: int = ALERT_COOLDOWN_SECONDS
    valid_until: Optional[datetime] = None
    description: Optional[str] = None


class AlertUpdateIn(Schema):
    name: Optional[str] = None
    condition_value: Optional[float] = None
    condition_operator: Optional[str] = None
    delivery_channels: Optional[List[str]] = None
    priority: Optional[int] = None
    cooldown_seconds: Optional[int] = None
    valid_until: Optional[datetime] = None
    description: Optional[str] = None


class AlertOut(Schema):
    id: str
    name: str
    alert_type: str
    symbol: str
    condition_value: float
    condition_operator: str
    status: str
    priority: int
    triggered_count: int
    delivery_channels: List[str]
    cooldown_seconds: int
    valid_from: datetime
    valid_until: Optional[datetime]
    created_at: datetime
    last_triggered_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AlertHistoryOut(Schema):
    id: str
    triggered_at: datetime
    trigger_value: float
    condition_met: bool
    notification_sent: bool
    notification_channels: List[str]


class AlertStatsOut(Schema):
    total_alerts: int
    active_alerts: int
    triggered_today: int
    type_distribution: dict


@router.get("/", response=List[AlertOut])
async def list_alerts(
    request,
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    alert_type: Optional[str] = None,
    limit: int = Query(default=ALERT_LIST_LIMIT, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """List user's alerts with optional filters"""
    try:
        user_id = str(request.user.id)
        
        cache_key = f"alerts_list_{user_id}_{status}_{symbol}_{alert_type}_{limit}_{offset}"
        cache_manager = get_cache_manager()
        
        cached = await cache_manager.get('alerts', cache_key)
        if cached:
            return cached
        
        queryset = Alert.objects.filter(user_id=user_id)
        
        if status:
            queryset = queryset.filter(status=status)
        if symbol:
            queryset = queryset.filter(symbol__iexact=symbol)
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        alerts = list(queryset.order_by('-priority', '-created_at')[offset:offset + limit])
        
        result = [
            {
                'id': str(alert.id),
                'name': alert.name,
                'alert_type': alert.alert_type,
                'symbol': alert.symbol,
                'condition_value': float(alert.condition_value),
                'condition_operator': alert.condition_operator,
                'status': alert.status,
                'priority': alert.priority,
                'triggered_count': alert.triggered_count,
                'delivery_channels': alert.delivery_channels,
                'cooldown_seconds': alert.cooldown_seconds,
                'valid_from': alert.valid_from,
                'valid_until': alert.valid_until,
                'created_at': alert.created_at,
                'last_triggered_at': alert.last_triggered_at
            }
            for alert in alerts
        ]
        
        await cache_manager.set('alerts', cache_key, value=result, ttl=60)
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        return []


@router.post("/")
async def create_alert(request, payload: AlertCreateIn):
    """Create a new alert"""
    try:
        alert_engine = get_alert_engine()
        
        user_id = str(request.user.id)
        
        if payload.alert_type not in AlertType.values:
            return {"error": f"Invalid alert type. Must be one of: {', '.join(AlertType.values)}"}
        
        if payload.delivery_channels:
            for channel in payload.delivery_channels:
                if channel not in DeliveryChannel.values:
                    return {"error": f"Invalid delivery channel: {channel}"}
        
        alert = await alert_engine.create_alert(
            user_id=user_id,
            name=payload.name,
            alert_type=payload.alert_type,
            symbol=payload.symbol,
            condition_value=payload.condition_value,
            condition_operator=payload.condition_operator,
            delivery_channels=payload.delivery_channels,
            priority=payload.priority,
            cooldown_seconds=payload.cooldown_seconds,
            valid_until=payload.valid_until,
            description=payload.description
        )
        
        return {
            "id": str(alert.id),
            "name": alert.name,
            "alert_type": alert.alert_type,
            "symbol": alert.symbol,
            "status": alert.status,
            "message": "Alert created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return {"error": str(e)}


@router.get("/{alert_id}", response=AlertOut)
async def get_alert(request, alert_id: str):
    """Get a specific alert"""
    try:
        alert = await Alert.objects.filter(
            id=alert_id,
            user_id=str(request.user.id)
        ).afirst()
        
        if not alert:
            return {"error": "Alert not found"}
        
        return {
            'id': str(alert.id),
            'name': alert.name,
            'alert_type': alert.alert_type,
            'symbol': alert.symbol,
            'condition_value': float(alert.condition_value),
            'condition_operator': alert.condition_operator,
            'status': alert.status,
            'priority': alert.priority,
            'triggered_count': alert.triggered_count,
            'delivery_channels': alert.delivery_channels,
            'cooldown_seconds': alert.cooldown_seconds,
            'valid_from': alert.valid_from,
            'valid_until': alert.valid_until,
            'created_at': alert.created_at,
            'last_triggered_at': alert.last_triggered_at
        }
        
    except Exception as e:
        logger.error(f"Error getting alert: {e}")
        return {"error": str(e)}


@router.put("/{alert_id}")
async def update_alert(request, alert_id: str, payload: AlertUpdateIn):
    """Update an existing alert"""
    try:
        alert_engine = get_alert_engine()
        
        update_data = {k: v for k, v in payload.dict().items() if v is not None}
        
        alert = await alert_engine.update_alert(alert_id, **update_data)
        
        if not alert:
            return {"error": "Alert not found"}
        
        return {
            "id": str(alert.id),
            "name": alert.name,
            "message": "Alert updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating alert: {e}")
        return {"error": str(e)}


@router.delete("/{alert_id}")
async def delete_alert(request, alert_id: str):
    """Delete an alert (soft delete)"""
    try:
        alert_engine = get_alert_engine()
        
        success = await alert_engine.delete_alert(alert_id)
        
        if not success:
            return {"error": "Alert not found"}
        
        return {"message": "Alert deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        return {"error": str(e)}


@router.post("/{alert_id}/pause")
async def pause_alert(request, alert_id: str):
    """Pause an active alert"""
    try:
        alert_engine = get_alert_engine()
        
        success = await alert_engine.pause_alert(alert_id)
        
        if not success:
            return {"error": "Alert not found"}
        
        return {"message": "Alert paused successfully"}
        
    except Exception as e:
        logger.error(f"Error pausing alert: {e}")
        return {"error": str(e)}


@router.post("/{alert_id}/resume")
async def resume_alert(request, alert_id: str):
    """Resume a paused alert"""
    try:
        alert_engine = get_alert_engine()
        
        success = await alert_engine.resume_alert(alert_id)
        
        if not success:
            return {"error": "Alert not found"}
        
        return {"message": "Alert resumed successfully"}
        
    except Exception as e:
        logger.error(f"Error resuming alert: {e}")
        return {"error": str(e)}


@router.get("/{alert_id}/history", response=List[AlertHistoryOut])
async def get_alert_history(
    request,
    alert_id: str,
    limit: int = Query(default=ALERT_HISTORY_LIMIT, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """Get alert trigger history"""
    try:
        alert = await Alert.objects.filter(
            id=alert_id,
            user_id=str(request.user.id)
        ).afirst()
        
        if not alert:
            return {"error": "Alert not found"}
        
        history = await AlertHistory.objects.filter(
            alert=alert
        ).order_by('-triggered_at')[offset:offset + limit]
        
        return [
            {
                'id': str(h.id),
                'triggered_at': h.triggered_at,
                'trigger_value': float(h.trigger_value),
                'condition_met': h.condition_met,
                'notification_sent': h.notification_sent,
                'notification_channels': h.notification_channels
            }
            for h in history
        ]
        
    except Exception as e:
        logger.error(f"Error getting alert history: {e}")
        return []


@router.get("/stats", response=AlertStatsOut)
async def get_alert_stats(request):
    """Get alert statistics for current user"""
    try:
        alert_engine = get_alert_engine()
        
        user_id = str(request.user.id)
        
        stats = alert_engine.get_alert_statistics(user_id)
        
        return AlertStatsOut(**stats)
        
    except Exception as e:
        logger.error(f"Error getting alert stats: {e}")
        return AlertStatsOut(
            total_alerts=0,
            active_alerts=0,
            triggered_today=0,
            type_distribution={}
        )


@router.post("/{alert_id}/test")
async def test_alert(request, alert_id: str):
    """Test an alert by manually triggering it"""
    try:
        alert = await Alert.objects.filter(
            id=alert_id,
            user_id=str(request.user.id)
        ).afirst()
        
        if not alert:
            return {"error": "Alert not found"}
        
        alert_engine = get_alert_engine()
        
        should_trigger = await alert_engine._check_alert(alert)
        
        return {
            "alert_id": str(alert.id),
            "name": alert.name,
            "symbol": alert.symbol,
            "would_trigger": should_trigger,
            "current_condition_value": float(alert.condition_value),
            "condition_operator": alert.condition_operator
        }
        
    except Exception as e:
        logger.error(f"Error testing alert: {e}")
        return {"error": str(e)}


@router.get("/types/")
async def get_alert_types():
    """Get available alert types"""
    return [
        {"value": choice[0], "label": choice[1]}
        for choice in AlertType.choices
    ]


@router.get("/channels/")
async def get_delivery_channels():
    """Get available delivery channels"""
    return [
        {"value": choice[0], "label": choice[1]}
        for choice in DeliveryChannel.choices
    ]
