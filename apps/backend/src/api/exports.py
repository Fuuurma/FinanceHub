"""
Data Export API
Endpoints for exporting portfolio, holdings, transactions, and historical data.
"""

import logging
from datetime import datetime
from typing import Optional
from ninja import Router, Query
from pydantic import BaseModel
from django.http import HttpResponse
from django.db.models import Q

from investments.models import (
    Portfolio, Position, Transaction, Asset, AssetPricesHistoric,
    WatchlistItem, ScreenerResult
)
from utils.export.exporters import DataExporter, ExportConfig

router = Router(tags=["Export"])
logger = logging.getLogger(__name__)


class DateRangeParams(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExportRequest(BaseModel):
    format: str = 'csv'
    columns: Optional[list[str]] = None
    include_headers: bool = True


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return None


def format_date_range(start: Optional[datetime], end: Optional[datetime]) -> str:
    """Format date range for filename."""
    now = datetime.now()
    start = start or now.replace(year=now.year - 1)
    end = end or now
    return f"{start.strftime('%Y%m%d')}-{end.strftime('%Y%m%d')}"


@router.get("/export/portfolio/{portfolio_id}")
def export_portfolio(
    request,
    portfolio_id: int,
    format: str = Query('csv', regex='^(csv|excel|json)$'),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Export portfolio holdings and performance data."""
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return HttpResponse("Portfolio not found", status=404)

    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)

    positions = portfolio.positions.select_related('asset').all()

    data = []
    for position in positions:
        asset = position.asset
        data.append({
            'symbol': asset.symbol,
            'name': asset.name,
            'quantity': position.quantity,
            'average_cost': position.average_cost,
            'current_price': asset.current_price,
            'market_value': position.market_value,
            'unrealized_gain_loss': position.unrealized_gain_loss,
            'unrealized_gain_loss_pct': position.unrealized_gain_loss_pct,
            'sector': asset.sector,
            'asset_type': asset.asset_type,
            'exchange': asset.exchange.code if asset.exchange else '',
            'currency': asset.currency.code if asset.currency else 'USD',
            'purchase_date': position.created_at.strftime('%Y-%m-%d') if position.created_at else '',
        })

    config = ExportConfig(
        format=format,
        columns=['symbol', 'name', 'quantity', 'average_cost', 'current_price',
                 'market_value', 'unrealized_gain_loss', 'unrealized_gain_loss_pct',
                 'sector', 'asset_type', 'exchange', 'currency', 'purchase_date'],
        filename=f"portfolio_{portfolio.name}_{format_date_range(start_dt, end_dt)}"
    )

    exporter = DataExporter(data, config)
    content_type, content_disposition, content = exporter.export('portfolio')

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = content_disposition
    return response


@router.get("/export/transactions/")
def export_transactions(
    request,
    format: str = Query('csv', regex='^(csv|excel|json)$'),
    portfolio_id: Optional[int] = None,
    asset_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Export transaction history."""
    queryset = Transaction.objects.filter(user=request.user)

    if portfolio_id:
        queryset = queryset.filter(portfolio_id=portfolio_id)

    if asset_id:
        queryset = queryset.filter(asset_id=asset_id)

    if transaction_type:
        queryset = queryset.filter(transaction_type=transaction_type.upper())

    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)

    if start_dt:
        queryset = queryset.filter(created_at__gte=start_dt)
    if end_dt:
        queryset = queryset.filter(created_at__lte=end_dt)

    data = []
    for tx in queryset.order_by('-created_at').select_related('asset', 'portfolio'):
        data.append({
            'date': tx.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_type': tx.transaction_type,
            'symbol': tx.asset.symbol if tx.asset else '',
            'quantity': tx.quantity,
            'price': tx.price,
            'total_amount': tx.total_amount,
            'fees': tx.fees,
            'portfolio': tx.portfolio.name if tx.portfolio else '',
            'notes': tx.notes or '',
        })

    config = ExportConfig(
        format=format,
        columns=['date', 'transaction_type', 'symbol', 'quantity', 'price',
                 'total_amount', 'fees', 'portfolio', 'notes'],
        filename=f"transactions_{format_date_range(start_dt, end_dt)}"
    )

    exporter = DataExporter(data, config)
    content_type, content_disposition, content = exporter.export('transactions')

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = content_disposition
    return response


@router.get("/export/historical/{symbol}")
def export_historical_data(
    request,
    symbol: str,
    format: str = Query('csv', regex='^(csv|excel|json)$'),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = Query('1d', regex='^(1d|1w|1m)$'),
):
    """Export historical price data for an asset."""
    try:
        asset = Asset.objects.get(symbol=symbol.upper())
    except Asset.DoesNotExist:
        return HttpResponse("Asset not found", status=404)

    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)

    queryset = AssetPricesHistoric.objects.filter(asset=asset).order_by('-timestamp')

    if start_dt:
        queryset = queryset.filter(timestamp__gte=start_dt)
    if end_dt:
        queryset = queryset.filter(timestamp__lte=end_dt)

    limit_map = {'1d': 365, '1w': 520, '1m': None}
    if limit := limit_map.get(interval):
        queryset = queryset[:limit]

    data = []
    for price in queryset:
        data.append({
            'timestamp': price.timestamp.strftime('%Y-%m-%d'),
            'open_price': price.open_price,
            'high_price': price.high_price,
            'low_price': price.low_price,
            'close_price': price.close_price,
            'volume': price.volume,
            'adj_close': price.adj_close or price.close_price,
        })

    config = ExportConfig(
        format=format,
        columns=['timestamp', 'open_price', 'high_price', 'low_price',
                 'close_price', 'volume', 'adj_close'],
        filename=f"{symbol}_historical_{format_date_range(start_dt, end_dt)}"
    )

    exporter = DataExporter(data, config)
    content_type, content_disposition, content = exporter.export(f"{symbol}_historical")

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = content_disposition
    return response


@router.get("/export/watchlist/")
def export_watchlist(
    request,
    format: str = Query('csv', regex='^(csv|excel|json)$'),
):
    """Export user's watchlist."""
    watchlist_items = WatchlistItem.objects.filter(
        user=request.user
    ).select_related('asset__exchange', 'asset__currency').order_by('created_at')

    data = []
    for item in watchlist_items:
        asset = item.asset
        data.append({
            'symbol': asset.symbol,
            'name': asset.name,
            'current_price': asset.current_price,
            'percent_change': asset.percent_change,
            'market_cap': asset.market_cap,
            'sector': asset.sector,
            'exchange': asset.exchange.code if asset.exchange else '',
            'currency': asset.currency.code if asset.currency else 'USD',
            'added_date': item.created_at.strftime('%Y-%m-%d') if item.created_at else '',
            'notes': item.notes or '',
        })

    config = ExportConfig(
        format=format,
        filename=f"watchlist_{datetime.now().strftime('%Y%m%d')}"
    )

    exporter = DataExporter(data, config)
    content_type, content_disposition, content = exporter.export('watchlist')

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = content_disposition
    return response


@router.get("/export/screener/{preset_id}")
def export_screener_results(
    request,
    preset_id: int,
    format: str = Query('csv', regex='^(csv|excel|json)$'),
    limit: int = Query(100, ge=1, le=1000),
):
    """Export screener results."""
    from investments.models import ScreenerPreset

    try:
        preset = ScreenerPreset.objects.get(id=preset_id, user=request.user)
    except ScreenerPreset.DoesNotExist:
        return HttpResponse("Screener preset not found", status=404)

    results = ScreenerResult.objects.filter(
        preset=preset
    ).select_related('asset').order_by('-created_at')[:limit]

    data = []
    for result in results:
        asset = result.asset
        data.append({
            'symbol': asset.symbol,
            'name': asset.name,
            'current_price': asset.current_price,
            'percent_change': asset.percent_change,
            'market_cap': asset.market_cap,
            'pe_ratio': asset.pe_ratio,
            'eps': asset.eps,
            'dividend_yield': asset.dividend_yield,
            'sector': asset.sector,
            'exchange': asset.exchange.code if asset.exchange else '',
        })

    config = ExportConfig(
        format=format,
        filename=f"screener_{preset.name}_{datetime.now().strftime('%Y%m%d')}"
    )

    exporter = DataExporter(data, config)
    content_type, content_disposition, content = exporter.export('screener_results')

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = content_disposition
    return response


@router.get("/export/performance/{portfolio_id}")
def export_portfolio_performance(
    request,
    portfolio_id: int,
    format: str = Query('csv', regex='^(csv|excel|json)$'),
    period: str = Query('1Y', regex='^(1M|3M|6M|1Y|YTD|ALL)$'),
):
    """Export portfolio performance data."""
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return HttpResponse("Portfolio not found", status=404)

    from investments.services.analytics_service import AnalyticsService

    analytics = AnalyticsService()
    performance_data = analytics.get_portfolio_performance_history(
        portfolio, period=period
    )

    data = []
    for item in performance_data:
        data.append({
            'date': item.get('date', ''),
            'total_value': item.get('total_value', 0),
            'total_return': item.get('total_return', 0),
            'total_return_pct': item.get('total_return_pct', 0),
            'daily_return': item.get('daily_return', 0),
            'daily_return_pct': item.get('daily_return_pct', 0),
        })

    config = ExportConfig(
        format=format,
        filename=f"{portfolio.name}_performance_{period}_{datetime.now().strftime('%Y%m%d')}"
    )

    exporter = DataExporter(data, config)
    content_type, content_disposition, content = exporter.export('portfolio_performance')

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = content_disposition
    return response
