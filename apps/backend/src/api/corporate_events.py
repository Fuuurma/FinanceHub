from ninja import Router
from ninja.security import HttpUser
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from investments.services.corporate_events_service import CorporateEventsService

router = Router(tags=["corporate_events"])
service = CorporateEventsService()


class EarningsCalendarResponse(BaseModel):
    id: int
    asset_id: int
    symbol: str
    company_name: str
    date: str
    time: str
    quarter: str
    estimated_eps: Optional[float] = None


class DividendsCalendarResponse(BaseModel):
    id: int
    asset_id: int
    symbol: str
    ex_date: Optional[str] = None
    record_date: Optional[str] = None
    payment_date: Optional[str] = None
    amount: float
    frequency: str


class CorporateActionsResponse(BaseModel):
    id: int
    type: str
    symbol: str
    description: str
    details: dict


class EconomicCalendarResponse(BaseModel):
    id: int
    name: str
    date: str
    importance: str
    actual: Optional[float] = None
    forecast: Optional[float] = None
    previous: Optional[float] = None
    country: str


@router.get("/calendar/earnings", response=List[EarningsCalendarResponse])
def earnings_calendar(request, days_ahead: int = 30):
    """Get upcoming earnings calendar"""
    return service.get_upcoming_earnings(days_ahead)


@router.get("/calendar/dividends", response=List[DividendsCalendarResponse])
def dividends_calendar(request, portfolio_only: bool = False):
    """Get upcoming dividend payments"""
    user_id = request.auth.id if portfolio_only else None
    return service.get_upcoming_dividends(user_id)


@router.get("/calendar/corporate-actions")
def corporate_actions_calendar(
    request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    action_types: Optional[str] = None,
):
    """Get corporate actions calendar"""
    types_list = action_types.split(",") if action_types else None
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    return service.get_corporate_actions_calendar(start, end, types_list)


@router.get("/calendar/economic", response=List[EconomicCalendarResponse])
def economic_calendar(
    request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    importance: Optional[str] = None,
):
    """Get economic calendar"""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    return service.get_economic_calendar(start, end, importance)


@router.get("/portfolios/{portfolio_id}/earnings-impact")
def earnings_impact_analysis(request, portfolio_id: int):
    """Analyze earnings impact on portfolio"""
    return service.analyze_earnings_impact(portfolio_id)


@router.get("/assets/{asset_id}/dividend-projection")
def dividend_projection(request, asset_id: int, periods: int = 4):
    """Get dividend projection for asset"""
    return service.get_dividend_projection(asset_id, periods)


@router.get("/assets/{asset_id}/corporate-actions")
def asset_corporate_actions(request, asset_id: int, limit: int = 20):
    """Get corporate actions for specific asset"""
    return service.get_asset_corporate_actions(asset_id, limit)


@router.get("/assets/{asset_id}/earnings-history")
def earnings_history(request, asset_id: int, limit: int = 8):
    """Get earnings history for asset"""
    return service.get_asset_earnings_history(asset_id, limit)
