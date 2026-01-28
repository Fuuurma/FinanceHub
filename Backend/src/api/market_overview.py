"""
Market Overview API - Aggregates data from multiple sources for dashboard
"""
from typing import List, Optional
from decimal import Decimal
from ninja import Router
from pydantic import BaseModel
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache

from utils.services.fundamental_service import get_fundamental_service
from utils.services.data_orchestrator import get_data_orchestrator
from utils.helpers.logger.logger import get_logger
from utils.constants.api import RATE_LIMIT_READ, CACHE_TTL_SHORT

logger = get_logger(__name__)

router = Router()


class MarketOverviewResponse(BaseModel):
    """
    Comprehensive market overview for dashboard
    
    Includes:
    - Market indices performance
    - Sector performance
    - Top gainers and losers
    - Asset class distribution
    - Market sentiment indicators
    """
    indices: List[dict]
    sectors: List[dict]
    top_gainers: List[dict]
    top_losers: List[dict]
    asset_distribution: dict
    market_sentiment: dict
    fetched_at: str
    sources: List[str]


class MarketIndicesResponse(BaseModel):
    """
    Major market indices with performance data
    """
    indices: List[dict]
    fetched_at: str
    source: str


class MarketMoversResponse(BaseModel):
    """
    Top market movers (gainers and losers)
    """
    gainers: List[dict]
    losers: List[dict]
    crypto_gainers: List[dict] = []
    crypto_losers: List[dict] = []
    fetched_at: str


class AssetDistributionResponse(BaseModel):
    """
    Asset class distribution for portfolio composition
    """
    equities: dict
    crypto: dict
    commodities: dict
    bonds: dict
    cash: dict
    total_value: Decimal
    distribution_percent: dict
    fetched_at: str


@router.get("/overview", response=MarketOverviewResponse)
async def get_market_overview():
    """
    Get comprehensive market overview for dashboard
    
    Aggregates data from fundamentals, market data, and portfolio data
    to provide a holistic view of the market.
    """
    fundamental_service = get_fundamental_service()
    market_service = get_market_data_service()
    
    try:
        # Get sector performance from fundamentals
        sector_data = await fundamental_service.get_sector_performance()
        sectors = sector_data.get('sectors', [])
        
        # Get top gainers/losers from market data
        top_movers = await orchestrator.get_top_movers(limit=10)
        top_gainers = top_movers.get('gainers', [])
        top_losers = top_movers.get('losers', [])
        
        # Get major market indices
        indices_data = [
            {
                'symbol': '^GSPC',
                'name': 'S&P 500',
                'price': await orchestrator.get_current_price('^GSPC'),
                'change': await orchestrator.get_24h_change('^GSPC'),
                'change_percent': await orchestrator.get_24h_change_percent('^GSPC'),
            },
            {
                'symbol': '^DJI',
                'name': 'Dow Jones',
                'price': await orchestrator.get_current_price('^DJI'),
                'change': await orchestrator.get_24h_change('^DJI'),
                'change_percent': await orchestrator.get_24h_change_percent('^DJI'),
            },
            {
                'symbol': '^IXIC',
                'name': 'NASDAQ',
                'price': await orchestrator.get_current_price('^IXIC'),
                'change': await orchestrator.get_24h_change('^IXIC'),
                'change_percent': await orchestrator.get_24h_change_percent('^IXIC'),
            },
        ]
        
        # Calculate market sentiment
        avg_gainer_change = sum(g.get('change_percent', 0) for g in top_gainers[:10]) / len(top_gainers[:10]) if top_gainers else 0
        avg_loser_change = sum(g.get('change_percent', 0) for g in top_losers[:10]) / len(top_losers[:10]) if top_losers else 0
        
        market_sentiment = {
            'overall': 'bullish' if avg_gainer_change > abs(avg_loser_change) else 'bearish',
            'strength': abs(avg_gainer_change - avg_loser_change),
            'trending_sectors': sorted(sectors, key=lambda x: x.get('avg_change_24h', 0), reverse=True)[:3],
        }
        
        # Asset distribution (mock data for now)
        asset_distribution = {
            'equities': {'value': 0, 'percentage': 0},
            'crypto': {'value': 0, 'percentage': 0},
            'commodities': {'value': 0, 'percentage': 0},
            'bonds': {'value': 0, 'percentage': 0},
            'cash': {'value': 0, 'percentage': 0},
            'total_value': Decimal('0'),
            'distribution_percent': {}
        }
        
        return {
            'indices': indices_data,
            'sectors': sectors,
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'asset_distribution': asset_distribution,
            'market_sentiment': market_sentiment,
            'fetched_at': timezone.now().isoformat(),
            'sources': ['market_data', 'fundamentals']
        }
        
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        return {
            'indices': [],
            'sectors': [],
            'top_gainers': [],
            'top_losers': [],
            'asset_distribution': {},
            'market_sentiment': {},
            'fetched_at': timezone.now().isoformat(),
            'sources': ['market_data']
        }


@router.get("/indices", response=MarketIndicesResponse)
async def get_market_indices():
    """
    Get major market indices with current prices and changes
    """
    market_service = get_market_data_service()
    
    try:
        indices = [
            {
                'symbol': '^GSPC',
                'name': 'S&P 500',
                'price': await orchestrator.get_current_price('^GSPC'),
                'change': await orchestrator.get_24h_change('^GSPC'),
                'change_percent': await orchestrator.get_24h_change_percent('^GSPC'),
                'volume': await orchestrator.get_24h_volume('^GSPC'),
                'high_52w': await orchestrator.get_52w_high('^GSPC'),
                'low_52w': await orchestrator.get_52w_low('^GSPC'),
            },
            {
                'symbol': '^DJI',
                'name': 'Dow Jones Industrial',
                'price': await orchestrator.get_current_price('^DJI'),
                'change': await orchestrator.get_24h_change('^DJI'),
                'change_percent': await orchestrator.get_24h_change_percent('^DJI'),
                'volume': await orchestrator.get_24h_volume('^DJI'),
                'high_52w': await orchestrator.get_52w_high('^DJI'),
                'low_52w': await orchestrator.get_52w_low('^DJI'),
            },
            {
                'symbol': '^IXIC',
                'name': 'NASDAQ Composite',
                'price': await orchestrator.get_current_price('^IXIC'),
                'change': await orchestrator.get_24h_change('^IXIC'),
                'change_percent': await orchestrator.get_24h_change_percent('^IXIC'),
                'volume': await orchestrator.get_24h_volume('^IXIC'),
                'high_52w': await orchestrator.get_52w_high('^IXIC'),
                'low_52w': await orchestrator.get_52w_low('^IXIC'),
            },
            {
                'symbol': '^RUT',
                'name': 'Russell 2000',
                'price': await orchestrator.get_current_price('^RUT'),
                'change': await orchestrator.get_24h_change('^RUT'),
                'change_percent': await orchestrator.get_24h_change_percent('^RUT'),
                'volume': await orchestrator.get_24h_volume('^RUT'),
                'high_52w': await orchestrator.get_52w_high('^RUT'),
                'low_52w': await orchestrator.get_52w_low('^RUT'),
            },
        ]
        
        return {
            'indices': indices,
            'fetched_at': timezone.now().isoformat(),
            'source': 'market_data'
        }
        
    except Exception as e:
        logger.error(f"Error fetching market indices: {e}")
        return {
            'indices': [],
            'fetched_at': timezone.now().isoformat(),
            'source': 'market_data'
        }


@router.get("/movers")
async def get_market_movers(
    asset_type: str = 'equities',
    limit: int = 20
):
    """
    Get top market movers (gainers and losers)
    
    Args:
        asset_type: 'equities', 'crypto', 'commodities', or 'all'
        limit: Number of movers to return
    """
    market_service = get_market_data_service()
    
    try:
        # Get top gainers
        gainers = await orchestrator.get_top_movers(
            direction='gainers',
            asset_type=asset_type,
            limit=limit
        )
        
        # Get top losers
        losers = await orchestrator.get_top_movers(
            direction='losers',
            asset_type=asset_type,
            limit=limit
        )
        
        # Get crypto movers if requested
        crypto_gainers = []
        crypto_losers = []
        if asset_type in ['crypto', 'all']:
            crypto_gainers = await orchestrator.get_top_movers(
                direction='gainers',
                asset_type='crypto',
                limit=limit
            )
            crypto_losers = await orchestrator.get_top_movers(
                direction='losers',
                asset_type='crypto',
                limit=limit
            )
        
        return MarketMoversResponse(
            gainers=gainers,
            losers=losers,
            crypto_gainers=crypto_gainers,
            crypto_losers=crypto_losers,
            fetched_at=timezone.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error fetching market movers: {e}")
        return MarketMoversResponse(
            gainers=[],
            losers=[],
            fetched_at=timezone.now().isoformat()
        )


@router.get("/trending")
async def get_trending_assets(
    asset_type: str = 'all',
    limit: int = 10,
    time_period: str = '24h'
):
    """
    Get trending assets based on volume and social signals
    
    Args:
        asset_type: 'equities', 'crypto', 'commodities', or 'all'
        limit: Number of assets to return
        time_period: '1h', '24h', '7d', '30d'
    """
    market_service = get_market_data_service()
    
    try:
        trending = await orchestrator.get_trending_assets(
            asset_type=asset_type,
            limit=limit,
            time_period=time_period
        )
        
        return {
            'assets': trending,
            'asset_type': asset_type,
            'time_period': time_period,
            'fetched_at': timezone.now().isoformat(),
            'source': 'market_data'
        }
        
    except Exception as e:
        logger.error(f"Error fetching trending assets: {e}")
        return {
            'assets': [],
            'asset_type': asset_type,
            'time_period': time_period,
            'fetched_at': timezone.now().isoformat(),
            'source': 'market_data'
        }
