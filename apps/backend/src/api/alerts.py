"""
Alerts API
Endpoints for managing alerts and notifications.
"""

import logging
from datetime import timedelta
from typing import Optional
from ninja import Router, Query
from pydantic import BaseModel
from django.http import HttpResponse
from django.utils import timezone

from investments.models.alerts import (
    Alert,
    AlertTrigger,
    Notification,
    NotificationPreference,
)
from investments.services.alerts.alert_service import AlertService
from assets.models import Asset

router = Router(tags=["Alerts"])
logger = logging.getLogger(__name__)

alert_service = AlertService()


class CreateAlertRequest(BaseModel):
    alert_type: str
    name: str
    asset_id: Optional[int] = None
    portfolio_id: Optional[int] = None
    condition_value: float
    condition_operator: str = ">="
    frequency: str = "once"
    expires_at: Optional[str] = None
    send_email: bool = False
    send_push: bool = True
    send_sms: bool = False
    send_in_app: bool = True
    custom_message: str = ""


class UpdateAlertRequest(BaseModel):
    name: Optional[str] = None
    condition_value: Optional[float] = None
    condition_operator: Optional[str] = None
    frequency: Optional[str] = None
    send_email: Optional[bool] = None
    send_push: Optional[bool] = None
    send_sms: Optional[bool] = None
    send_in_app: Optional[bool] = None
    custom_message: Optional[str] = None


@router.get("/alerts/")
def list_alerts(
    request,
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
):
    """List all alerts for the current user."""
    alerts = alert_service.get_user_alerts(request.user, status=status)

    if alert_type:
        alerts = [a for a in alerts if a.alert_type == alert_type]

    return {
        "alerts": [
            {
                "id": a.id,
                "name": a.name,
                "alert_type": a.alert_type,
                "status": a.status,
                "asset_symbol": a.asset.symbol if a.asset else None,
                "condition_value": float(a.condition_value),
                "condition_operator": a.condition_operator,
                "frequency": a.frequency,
                "send_email": a.send_email,
                "send_push": a.send_push,
                "send_sms": a.send_sms,
                "send_in_app": a.send_in_app,
                "created_at": a.created_at.isoformat(),
                "last_triggered_at": a.last_triggered_at.isoformat()
                if a.last_triggered_at
                else None,
                "trigger_count": a.trigger_count,
            }
            for a in alerts
        ]
    }


@router.post("/alerts/")
def create_alert(request, data: CreateAlertRequest):
    """Create a new alert."""
    try:
        alert = alert_service.create_alert(
            user=request.user,
            alert_type=data.alert_type,
            name=data.name,
            asset_id=data.asset_id,
            portfolio_id=data.portfolio_id,
            condition_value=data.condition_value,
            condition_operator=data.condition_operator,
            frequency=data.frequency,
            expires_at=data.expires_at,
            send_email=data.send_email,
            send_push=data.send_push,
            send_sms=data.send_sms,
            send_in_app=data.send_in_app,
            custom_message=data.custom_message,
        )

        return {
            "id": alert.id,
            "status": "created",
            "message": "Alert created successfully",
        }
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error creating alert: {e}")
        return {"error": str(e)}, 400


@router.get("/alerts/{alert_id}")
def get_alert(request, alert_id: int):
    """Get a specific alert."""
    alerts = alert_service.get_user_alerts(request.user)
    alert = next((a for a in alerts if a.id == alert_id), None)

    if not alert:
        return {"error": "Alert not found"}, 404

    return {
        "id": alert.id,
        "name": alert.name,
        "alert_type": alert.alert_type,
        "status": alert.status,
        "asset_id": alert.asset_id,
        "asset_symbol": alert.asset.symbol if alert.asset else None,
        "condition_value": float(alert.condition_value),
        "condition_operator": alert.condition_operator,
        "frequency": alert.frequency,
        "expires_at": alert.expires_at.isoformat() if alert.expires_at else None,
        "send_email": alert.send_email,
        "send_push": alert.send_push,
        "send_sms": alert.send_sms,
        "send_in_app": alert.send_in_app,
        "custom_message": alert.custom_message,
        "created_at": alert.created_at.isoformat(),
        "last_triggered_at": alert.last_triggered_at.isoformat()
        if alert.last_triggered_at
        else None,
        "trigger_count": alert.trigger_count,
    }


@router.patch("/alerts/{alert_id}")
def update_alert(request, alert_id: int, data: UpdateAlertRequest):
    """Update an alert."""
    update_data = data.model_dump(exclude_unset=True)
    alert = alert_service.update_alert(alert_id, request.user, **update_data)

    if not alert:
        return {"error": "Alert not found"}, 404

    return {"status": "updated", "id": alert.id}


@router.delete("/alerts/{alert_id}")
def delete_alert(request, alert_id: int):
    """Delete an alert."""
    success = alert_service.delete_alert(alert_id, request.user)
    if not success:
        return {"error": "Alert not found"}, 404
    return {"status": "deleted"}


@router.post("/alerts/{alert_id}/pause")
def pause_alert(request, alert_id: int):
    """Pause an alert."""
    alert = alert_service.pause_alert(alert_id, request.user)
    if not alert:
        return {"error": "Alert not found"}, 404
    return {"status": "paused", "id": alert.id}


@router.post("/alerts/{alert_id}/resume")
def resume_alert(request, alert_id: int):
    """Resume a paused alert."""
    alert = alert_service.resume_alert(alert_id, request.user)
    if not alert:
        return {"error": "Alert not found"}, 404
    return {"status": "active", "id": alert.id}


@router.get("/alerts/{alert_id}/triggers")
def get_alert_triggers(request, alert_id: int, limit: int = 20):
    """Get trigger history for an alert."""
    alerts = alert_service.get_user_alerts(request.user)
    alert = next((a for a in alerts if a.id == alert_id), None)

    if not alert:
        return {"error": "Alert not found"}, 404

    triggers = AlertTrigger.objects.filter(alert=alert).order_by("-triggered_at")[
        :limit
    ]

    return {
        "triggers": [
            {
                "id": t.id,
                "triggered_at": t.triggered_at.isoformat(),
                "trigger_value": float(t.trigger_value),
                "asset_price": float(t.asset_price) if t.asset_price else None,
                "email_sent": t.email_sent,
                "push_sent": t.push_sent,
                "sms_sent": t.sms_sent,
                "viewed": t.viewed,
            }
            for t in triggers
        ]
    }


@router.get("/notifications/")
def list_notifications(
    request,
    unread_only: bool = False,
    limit: int = 50,
):
    """List notifications for the current user."""
    notifications = alert_service.get_user_notifications(
        request.user, unread_only=unread_only, limit=limit
    )

    return {
        "notifications": [
            {
                "id": n.id,
                "notification_type": n.notification_type,
                "title": n.title,
                "message": n.message,
                "read": n.read,
                "priority": n.priority,
                "action_url": n.action_url,
                "related_asset_symbol": n.related_asset.symbol
                if n.related_asset
                else None,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ],
        "unread_count": alert_service.get_unread_count(request.user),
    }


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(request, notification_id: int):
    """Mark a notification as read."""
    success = alert_service.mark_notification_read(notification_id, request.user)
    if not success:
        return {"error": "Notification not found"}, 404
    return {"status": "read"}


@router.post("/notifications/read-all")
def mark_all_read(request):
    """Mark all notifications as read."""
    count = alert_service.mark_all_notifications_read(request.user)
    return {"status": "updated", "count": count}


@router.get("/notifications/count")
def get_unread_count(request):
    """Get count of unread notifications."""
    return {"count": alert_service.get_unread_count(request.user)}


@router.get("/alerts/trigger")
def trigger_check(request):
    """Manually trigger alert check (for testing)."""
    triggers = alert_service.check_and_trigger_alerts()
    return {
        "status": "checked",
        "triggers_count": len(triggers),
        "triggers": [
            {
                "id": t.id,
                "alert_id": t.alert_id,
                "triggered_at": t.triggered_at.isoformat(),
            }
            for t in triggers
        ],
    }
