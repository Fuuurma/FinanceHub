from typing import List, Optional
from datetime import datetime, timedelta
from ninja import Router, Query, Schema
from django.db.models import Q
from django.shortcuts import get_object_or_404

from assets.models.asset import Asset
from assets.models.historic.prices import AssetPricesHistoric
from assets.models.historic.metrics import AssetMetricsHistoric
from assets.models.sector import Sector
from assets.models.industry import Industry

router = Router(tags=["Assets"])


class AssetOut(Schema):
    id: str
    symbol: str
    name: str
    asset_type: str
    exchange: Optional[str]
    currency: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class AssetDetailOut(Schema):
    id: str
    symbol: str
    name: str
    asset_type: str
    exchange: Optional[str]
    currency: Optional[str]
    description: Optional[str]
    sector: Optional[str]
    sector_code: Optional[str]
    industry: Optional[str]
    industry_code: Optional[str]
    market_cap: Optional[float]
    country: Optional[str]
    website: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class PriceOut(Schema):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    class Config:
        from_attributes = True


class AssetFilter(Schema):
    search: Optional[str] = None
    asset_type: Optional[str] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    sector_code: Optional[str] = None
    industry: Optional[str] = None
    industry_code: Optional[str] = None


@router.get("/", response=List[AssetOut])
def list_assets(
    request, filters: AssetFilter = Query(...), limit: int = 20, offset: int = 0
):
    """Search for assets with pagination and filters"""
    qs = Asset.objects.filter(is_active=True).select_related(
        "asset_type", "sector_fk", "industry_fk", "country"
    )

    if filters.search:
        qs = qs.filter(
            Q(symbol__icontains=filters.search) | Q(name__icontains=filters.search)
        )

    if filters.asset_type:
        qs = qs.filter(asset_type__name__iexact=filters.asset_type)

    if filters.exchange:
        qs = qs.filter(exchanges__symbol__iexact=filters.exchange)

    if filters.sector:
        qs = qs.filter(
            Q(sector_fk__name__iexact=filters.sector)
            | Q(sector_fk__code__iexact=filters.sector)
            | Q(sector__iexact=filters.sector)
        )

    if filters.sector_code:
        qs = qs.filter(sector_fk__code__iexact=filters.sector_code)

    if filters.industry:
        qs = qs.filter(
            Q(industry_fk__name__iexact=filters.industry)
            | Q(industry_fk__code__iexact=filters.industry)
            | Q(industry__iexact=filters.industry)
        )

    return list(qs[offset : offset + limit])


def serialize_asset_detail(asset: Asset) -> dict:
    """Serialize asset with proper sector/industry info from FKs."""
    return {
        "id": str(asset.id),
        "symbol": asset.ticker,
        "name": asset.name,
        "asset_type": asset.asset_type.name if asset.asset_type else None,
        "exchange": asset.exchange,
        "currency": asset.currency,
        "description": asset.metadata.get("description") if asset.metadata else None,
        "sector": asset.sector_fk.name if asset.sector_fk else asset.sector,
        "sector_code": asset.sector_fk.code if asset.sector_fk else None,
        "industry": asset.industry_fk.name if asset.industry_fk else asset.industry,
        "industry_code": asset.industry_fk.code if asset.industry_fk else None,
        "market_cap": float(asset.market_cap) if asset.market_cap else None,
        "country": asset.country.name if asset.country else None,
        "website": asset.website,
        "is_active": asset.status == "active",
    }


@router.get("/{symbol}", response=AssetDetailOut)
def get_asset(request, symbol: str):
    """Get detailed information for a specific asset"""
    asset = get_object_or_404(Asset, ticker__iexact=symbol, is_active=True)
    return serialize_asset_detail(asset)


@router.get("/{symbol}/price")
def get_current_price(request, symbol: str):
    """Get the current price of an asset"""
    asset = get_object_or_404(Asset, symbol__iexact=symbol, is_active=True)

    latest_price = (
        AssetPricesHistoric.objects.filter(asset=asset).order_by("-timestamp").first()
    )

    if not latest_price:
        return {"error": "Price data not available"}

    return {
        "symbol": asset.symbol,
        "price": latest_price.close,
        "change": getattr(latest_price, "change", 0),
        "change_percent": getattr(latest_price, "change_percent", 0),
        "timestamp": latest_price.timestamp,
        "high": latest_price.high,
        "low": latest_price.low,
        "open": latest_price.open,
        "volume": latest_price.volume,
    }


@router.get("/{symbol}/historical", response=List[PriceOut])
def get_historical_prices(
    request,
    symbol: str,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    interval: str = "1d",
):
    """
    Get historical price data for an asset
    Intervals: 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M
    """
    asset = get_object_or_404(Asset, symbol__iexact=symbol, is_active=True)

    qs = AssetPricesHistoric.objects.filter(asset=asset)

    if from_date:
        qs = qs.filter(timestamp__gte=from_date)
    if to_date:
        qs = qs.filter(timestamp__lte=to_date)

    data = list(qs.order_by("-timestamp")[:1000])

    return list(reversed(data))


@router.get("/{symbol}/fundamentals")
def get_fundamentals(request, symbol: str):
    """Get fundamental data for an asset"""
    asset = get_object_or_404(Asset, symbol__iexact=symbol, is_active=True)

    metrics = (
        AssetMetricsHistoric.objects.filter(asset=asset).order_by("-timestamp").first()
    )

    if not metrics:
        return {"error": "Fundamental data not available"}

    return {
        "symbol": asset.symbol,
        "name": asset.name,
        "metrics": {
            "market_cap": getattr(metrics, "market_cap", None),
            "pe_ratio": getattr(metrics, "pe_ratio", None),
            "pb_ratio": getattr(metrics, "pb_ratio", None),
            "eps": getattr(metrics, "eps", None),
            "dividend_yield": getattr(metrics, "dividend_yield", None),
            "beta": getattr(metrics, "beta", None),
            "revenue": getattr(metrics, "revenue", None),
            "net_income": getattr(metrics, "net_income", None),
            "total_assets": getattr(metrics, "total_assets", None),
            "total_debt": getattr(metrics, "total_debt", None),
        },
        "timestamp": metrics.timestamp,
    }


@router.get("/{symbol}/news")
def get_news(request, symbol: str, limit: int = 10):
    """Get recent news for an asset"""
    return {"symbol": symbol, "news": [], "message": "News feed not yet implemented"}
