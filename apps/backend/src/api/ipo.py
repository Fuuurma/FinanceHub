from typing import Optional
from ninja import Router, Schema, Field
from pydantic import BaseModel

router = Router(tags=["IPO Calendar"])

ipo_service = None

try:
    from investments.services.ipo_service import IPOCalendarService

    ipo_service = IPOCalendarService()
except ImportError:
    pass


class IPOQuerySchema(Schema):
    days_ahead: int = Field(default=90, ge=1, le=365)
    status: Optional[str] = None
    sector: Optional[str] = None
    exchange: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class IPOAlertSchema(BaseModel):
    alert_type: str = Field(default="upcoming")
    sector: str = ""
    exchange: str = ""
    min_deal_size: Optional[float] = None
    max_deal_size: Optional[float] = None


class WatchlistSchema(BaseModel):
    ipo_id: int
    notes: str = ""


@router.get("/ipo/upcoming")
def get_upcoming_ipos(
    request,
    days_ahead: int = 90,
    status: Optional[str] = None,
    sector: Optional[str] = None,
    exchange: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    """Get upcoming IPOs"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    result = ipo_service.get_upcoming_ipos(
        days_ahead=days_ahead,
        status=status,
        sector=sector,
        exchange=exchange,
        limit=limit,
        offset=offset,
    )
    return result


@router.get("/ipo/recent")
def get_recent_ipos(request, days_back: int = 90, limit: int = 50, offset: int = 0):
    """Get recently listed IPOs"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    return ipo_service.get_recent_ipos(days_back=days_back, limit=limit, offset=offset)


@router.get("/ipo/{ipo_id}")
def get_ipo_detail(request, ipo_id: int):
    """Get IPO details"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    result = ipo_service.get_ipo_detail(ipo_id)
    if "error" in result:
        return result, 404
    return result


@router.get("/ipo/stats/summary")
def get_ipo_stats(request):
    """Get IPO statistics"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    return ipo_service.get_stats()


@router.get("/ipo/calendar/summary")
def get_calendar_summary(request, months: int = 3):
    """Get IPO calendar summary by month"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    return ipo_service.get_calendar_summary(months=months)


@router.get("/ipo/filters/sectors")
def get_sectors(request):
    """Get available sectors"""
    if not ipo_service:
        return {"sectors": []}

    return {"sectors": ipo_service.get_sectors()}


@router.get("/ipo/filters/exchanges")
def get_exchanges(request):
    """Get available exchanges"""
    if not ipo_service:
        return {"exchanges": []}

    return {"exchanges": ipo_service.get_exchanges()}


@router.post("/ipo/watchlist")
def add_to_watchlist(request, data: WatchlistSchema):
    """Add IPO to watchlist"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    user_id = getattr(request, "auth", None) and getattr(request.auth, "id", 0) or 0
    if user_id == 0:
        return {"error": "Authentication required"}, 401

    return ipo_service.add_to_watchlist(user_id, data.ipo_id, data.notes)


@router.delete("/ipo/watchlist/{ipo_id}")
def remove_from_watchlist(request, ipo_id: int):
    """Remove IPO from watchlist"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    user_id = getattr(request, "auth", None) and getattr(request.auth, "id", 0) or 0
    if user_id == 0:
        return {"error": "Authentication required"}, 401

    return ipo_service.remove_from_watchlist(user_id, ipo_id)


@router.get("/ipo/watchlist")
def get_watchlist(request):
    """Get user's watchlist"""
    if not ipo_service:
        return {"watchlist": []}

    user_id = getattr(request, "auth", None) and getattr(request.auth, "id", 0) or 0
    if user_id == 0:
        return {"watchlist": []}

    return {"watchlist": ipo_service.get_watchlist(user_id)}


@router.post("/ipo/alerts")
def create_alert(request, data: IPOAlertSchema):
    """Create IPO alert"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    user_id = getattr(request, "auth", None) and getattr(request.auth, "id", 0) or 0
    if user_id == 0:
        return {"error": "Authentication required"}, 401

    return ipo_service.create_alert(
        user_id=user_id,
        alert_type=data.alert_type,
        sector=data.sector,
        exchange=data.exchange,
        min_deal_size=data.min_deal_size,
        max_deal_size=data.max_deal_size,
    )


@router.get("/ipo/alerts")
def get_alerts(request):
    """Get user's IPO alerts"""
    if not ipo_service:
        return {"alerts": []}

    user_id = getattr(request, "auth", None) and getattr(request.auth, "id", 0) or 0
    if user_id == 0:
        return {"alerts": []}

    return {"alerts": ipo_service.get_alerts(user_id)}


@router.delete("/ipo/alerts/{alert_id}")
def delete_alert(request, alert_id: int):
    """Delete IPO alert"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    user_id = getattr(request, "auth", None) and getattr(request.auth, "id", 0) or 0
    if user_id == 0:
        return {"error": "Authentication required"}, 401

    return ipo_service.delete_alert(user_id, alert_id)


@router.get("/ipo/spacs")
def get_spacs(request, status: Optional[str] = None, limit: int = 50, offset: int = 0):
    """Get SPAC list"""
    if not ipo_service:
        return {"error": "IPO service not available"}, 503

    return ipo_service.get_spacs(status=status, limit=limit, offset=offset)
