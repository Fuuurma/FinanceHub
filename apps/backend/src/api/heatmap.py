"""
Heat Map API
Provides market heat map data for different views.
"""

from ninja import Router
from typing import List, Dict, Any
from django.db.models import Sum, Avg
from investments.models import Asset, Portfolio, WatchlistItem

router = Router(tags=["Heat Map"])


def calculate_asset_change(asset: Asset) -> float:
    """Calculate percentage change for an asset."""
    if not asset.previous_close or asset.previous_close == 0:
        return 0.0
    return ((asset.current_price - asset.previous_close) / asset.previous_close) * 100


@router.get("/heatmap/{view}")
def get_heatmap_data(request, view: str) -> List[Dict[str, Any]]:
    """
    Get heat map data for different views.

    Views:
    - sp500: S&P 500 sectors
    - nasdaq: NASDAQ Composite
    - dow: Dow Jones Industrial Average
    - portfolio: User's portfolio holdings
    - watchlist: User's watchlist
    """
    user = request.auth

    if view == 'sp500':
        return get_sp500_heatmap()
    elif view == 'nasdaq':
        return get_nasdaq_heatmap()
    elif view == 'dow':
        return get_dow_heatmap()
    elif view == 'portfolio':
        return get_portfolio_heatmap(user)
    elif view == 'watchlist':
        return get_watchlist_heatmap(user)
    else:
        return []


def get_sp500_heatmap() -> List[Dict[str, Any]]:
    """Get S&P 500 sector heat map."""
    sectors = Asset.objects.filter(
        asset_type='stock',
        exchange__code='NYSE'
    ).values('sector').annotate(
        total_market_cap=Sum('market_cap'),
        avg_change=Avg('percent_change')
    ).order_by('-total_market_cap')

    data = []
    for sector in sectors:
        if sector['sector']:
            data.append({
                'id': sector['sector'].lower().replace(' ', '-'),
                'name': sector['sector'],
                'value': sector['total_market_cap'] or 0,
                'change': sector['avg_change'] or 0,
                'changeAmount': 0,
                'type': 'sector'
            })

    return data


def get_nasdaq_heatmap() -> List[Dict[str, Any]]:
    """Get NASDAQ sector heat map (tech-heavy)."""
    sectors = Asset.objects.filter(
        asset_type='stock',
        exchange__code='NASDAQ'
    ).values('sector').annotate(
        total_market_cap=Sum('market_cap'),
        avg_change=Avg('percent_change')
    ).order_by('-total_market_cap')

    data = []
    for sector in sectors:
        if sector['sector']:
            data.append({
                'id': sector['sector'].lower().replace(' ', '-'),
                'name': sector['sector'],
                'value': sector['total_market_cap'] or 0,
                'change': sector['avg_change'] or 0,
                'changeAmount': 0,
                'type': 'sector'
            })

    return data


def get_dow_heatmap() -> List[Dict[str, Any]]:
    """Get Dow Jones Industrial Average heat map."""
    dow_symbols = [
        'AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 'CRM', 'CSCO', 'CVX',
        'DIS', 'DOW', 'GS', 'HD', 'HON', 'IBM', 'INTC', 'JNJ',
        'JPM', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'PG',
        'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT', 'XOM'
    ]

    assets = Asset.objects.filter(symbol__in=dow_symbols)

    data = []
    for asset in assets:
        data.append({
            'id': asset.symbol,
            'name': asset.name or asset.symbol,
            'symbol': asset.symbol,
            'value': asset.market_cap or 0,
            'change': asset.percent_change or 0,
            'changeAmount': (asset.percent_change or 0) * (asset.market_cap or 0) / 100,
            'type': 'stock'
        })

    return sorted(data, key=lambda x: x['value'], reverse=True)


def get_portfolio_heatmap(user) -> List[Dict[str, Any]]:
    """Get user's portfolio heat map."""
    if not user or not user.is_authenticated:
        return []

    portfolios = Portfolio.objects.filter(user=user).prefetch_related('positions__asset')

    data = []
    for portfolio in portfolios:
        for position in portfolio.positions.all():
            asset = position.asset
            change = 0
            if position.average_cost and position.average_cost > 0:
                change = ((asset.current_price - position.average_cost) / position.average_cost) * 100

            data.append({
                'id': f"{portfolio.id}-{asset.id}",
                'name': asset.name or asset.symbol,
                'symbol': asset.symbol,
                'value': position.market_value or 0,
                'change': change,
                'changeAmount': position.unrealized_gain_loss or 0,
                'type': 'stock'
            })

    return sorted(data, key=lambda x: x['value'], reverse=True)


def get_watchlist_heatmap(user) -> List[Dict[str, Any]]:
    """Get user's watchlist heat map."""
    if not user or not user.is_authenticated:
        return []

    watchlist_items = WatchlistItem.objects.filter(
        user=user
    ).select_related('asset')

    data = []
    for item in watchlist_items:
        asset = item.asset
        if asset:
            data.append({
                'id': asset.symbol,
                'name': asset.name or asset.symbol,
                'symbol': asset.symbol,
                'value': asset.market_cap or 0,
                'change': asset.percent_change or 0,
                'changeAmount': (asset.percent_change or 0) * (asset.market_cap or 0) / 100,
                'type': 'stock'
            })

    return sorted(data, key=lambda x: x['value'], reverse=True)


@router.get("/heatmap/{view}/{sector}")
def get_sector_stocks(request, view: str, sector: str) -> List[Dict[str, Any]]:
    """Get stocks within a specific sector."""
    sector_name = sector.replace('-', ' ').title()

    stocks = Asset.objects.filter(
        asset_type='stock',
        sector__icontains=sector_name
    ).values(
        'symbol', 'name', 'market_cap', 'percent_change'
    )[:50]

    data = []
    for stock in stocks:
        data.append({
            'id': stock['symbol'],
            'name': stock['name'] or stock['symbol'],
            'symbol': stock['symbol'],
            'value': stock['market_cap'] or 0,
            'change': stock['percent_change'] or 0,
            'changeAmount': (stock['percent_change'] or 0) * (stock['market_cap'] or 0) / 100,
            'type': 'stock'
        })

    return sorted(data, key=lambda x: x['value'], reverse=True)
