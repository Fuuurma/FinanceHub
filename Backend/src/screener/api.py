"""
API endpoints for Screener functionality
"""
import orjson
from ninja import Router, Query, Schema
from ninja_jwt.authentication import JWTAuth
from typing import List, Optional, Dict, Any

from screener.service import (
    stock_screener,
    get_screener_filters,
    apply_screener_preset,
    SCREENER_PRESETS
)
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

router = Router(tags=["Screener"])


class ScreenerFilterIn(Schema):
    key: str
    value: Any
    operator: str = "eq"


class ScreenerPresetIn(Schema):
    preset_name: str


class ScreenerFilterOut(Schema):
    key: str
    label: str
    value: Any
    operator: str
    active: bool


class AssetTypeInfo(Schema):
    key: str
    label: str
    count: int


class ExchangeInfo(Schema):
    key: str
    label: str
    count: int


class SectorInfo(Schema):
    key: str
    label: str
    count: int


class ScreenerPresetOut(Schema):
    key: str
    name: str
    description: str


class ScreenerFiltersOut(Schema):
    categories: Dict[str, Dict[str, List[str]]]
    presets: List[ScreenerPresetOut]
    active_filters: List[ScreenerFilterOut]
    available_asset_types: List[AssetTypeInfo]
    available_exchanges: List[ExchangeInfo]
    available_sectors: List[SectorInfo]


class ScreenerResult(Schema):
    id: str
    symbol: str
    name: str
    asset_type: str
    price: Optional[float]
    change: Optional[float]
    change_percent: Optional[float]
    volume: Optional[float]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]


class ScreenerResponse(Schema):
    results: List[ScreenerResult]
    count: int
    total_screened: int
    filters_applied: int
    filters: List[ScreenerFilterOut]
    elapsed_seconds: float
    limit: int
    timestamp: str


class ScreenerMetadata(Schema):
    categories: Dict[str, Dict[str, List[str]]]
    presets: Dict[str, Dict[str, str]]
    filters_applied: int
    available_asset_types: List[AssetTypeInfo]
    available_exchanges: List[ExchangeInfo]
    available_sectors: List[SectorInfo]


@router.get("/filters", response=ScreenerFiltersOut, auth=JWTAuth())
def get_filters(request) -> ScreenerFiltersOut:
    """
    Get all available filters and presets
    """
    data = get_screener_filters()
    
    return data


@router.get("/presets", auth=JWTAuth())
def get_presets(request) -> Dict[str, List[ScreenerPresetOut]]:
    """
    Get all available screener presets
    """
    presets = [
        {
            'key': key,
            'name': value['name'],
            'description': value['description']
        }
        for key, value in SCREENER_PRESETS.items()
    ]
    
    return presets


@router.post("/screen", response=ScreenerResponse, auth=JWTAuth())
def screen_assets(
    request,
    filters: List[ScreenerFilterIn] = None,
    preset: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("relevance", description="Sort by: relevance, price, volume, change"),
    sort_order: str = Query("desc", description="Sort order: asc, desc")
) -> ScreenerResponse:
    """
    Screen assets based on filters or preset
    
    - Apply custom filters if provided
    - Apply preset if provided
    - Support sorting and pagination
    """
    # Apply preset if provided
    if preset:
        preset_result = apply_screener_preset(preset)
        if 'error' in preset_result:
            return {
                'error': preset_result['error'],
                'results': [],
                'count': 0,
                'total_screened': 0,
                'filters_applied': 0,
                'filters': [],
                'elapsed_seconds': 0,
                'limit': limit,
                "timestamp": ""
            }
    
    # Apply custom filters
    if filters:
        stock_screener.clear_filters()
        for f in filters:
            stock_screener.add_filter(f.key, f.key, f.value, f.operator)
    
    # Run screener
    result = stock_screener.screen(limit=limit)
    
    if 'error' in result:
        return {
            'error': result['error'],
            'results': [],
            'count': 0,
            'total_screened': 0,
            'filters_applied': 0,
            'filters': [],
            'elapsed_seconds': 0,
            'limit': limit,
            "timestamp": ""
        }
    
    # Format results
    formatted_results = []
    for asset_data in result.get('results', []):
        formatted_results.append(ScreenerResult(
            id=str(asset_data.get('id', '')),
            symbol=asset_data.get('symbol', ''),
            name=asset_data.get('name', ''),
            asset_type=asset_data.get('asset_type', ''),
            price=asset_data.get('current_price'),
            change=asset_data.get('change'),
            change_percent=asset_data.get('change_percent'),
            volume=asset_data.get('volume'),
            market_cap=asset_data.get('market_cap'),
            pe_ratio=asset_data.get('pe_ratio'),
            dividend_yield=asset_data.get('dividend_yield'),
        ))
    
    return ScreenerResponse(
        results=formatted_results,
        count=len(formatted_results),
        total_screened=result.get('total_screened', 0),
        filters_applied=result.get('filters_applied', 0),
        filters=result.get('filters', []),
        elapsed_seconds=result.get('elapsed_seconds', 0),
        limit=limit,
        timestamp=result.get('timestamp', '')
    )


@router.get("/filters/asset-types", response=List[AssetTypeInfo], auth=JWTAuth())
def get_asset_types(request):
    """Get available asset types for filtering"""
    data = get_screener_filters()
    return data.get('available_asset_types', [])


@router.get("/filters/exchanges", response=List[ExchangeInfo], auth=JWTAuth())
def get_exchanges(request):
    """Get available exchanges for filtering"""
    data = get_screener filters()
    return data.get('available_exchanges', [])


@router.get("/filters/sectors", response=List[SectorInfo], auth=JWTAuth())
def get_sectors(request):
    """Get available sectors for filtering"""
    data = get_screener_filters()
    return data.get('available_sectors', [])


@router.post("/clear-filters", response=Dict[str, str], auth=JWTAuth())
def clear_filters(request):
    """Clear all active screener filters"""
    stock_screener.clear_filters()
    
    logger.info("Cleared all screener filters")
    
    return {
        "message": "All filters cleared"
    }


@router.post("/apply-preset", response=Dict[str, Any], auth=JWTAuth())
def apply_preset_endpoint(request, preset: ScreenerPresetIn):
    """
    Apply a predefined screener preset
    """
    result = apply_screener_preset(preset.preset_name)
    
    if 'error' in result:
        return {
            'error': result['error'],
            'success': False
        }
    
    return {
        'preset_name': preset.preset_name,
        'filters_applied': result.get('filters_applied', 0),
        'success': True
    }
