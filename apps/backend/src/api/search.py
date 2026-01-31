from typing import Optional, List
from ninja import Router, Schema, Query
from pydantic import Field

router = Router(tags=["Search & Discovery"])

search_service = None

try:
    from investments.services.search_service import UniversalSearchService

    search_service = UniversalSearchService()
except ImportError:
    pass


class SearchQuerySchema(Schema):
    q: str = Field(..., min_length=1, max_length=200, description="Search query")
    asset_types: Optional[List[str]] = Field(
        default=None, description="Filter by asset types"
    )
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class AdvancedSearchSchema(Schema):
    q: str = Field(default="", max_length=200)
    asset_types: Optional[List[str]] = None
    sector: Optional[List[str]] = None
    exchange: Optional[List[str]] = None
    market_cap_min: Optional[float] = None
    market_cap_max: Optional[float] = None
    pe_ratio_min: Optional[float] = None
    pe_ratio_max: Optional[float] = None
    dividend_yield_min: Optional[float] = None
    volume_min: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    change_pct_min: Optional[float] = None
    change_pct_max: Optional[float] = None
    sort_by: str = Field(default="market_cap")
    sort_order: str = Field(default="desc")
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class SaveSearchSchema(Schema):
    name: str = Field(..., min_length=1, max_length=200)
    query: str = Field(default="", max_length=200)
    filters: Optional[dict] = None
    sort_by: str = Field(default="market_cap")
    sort_order: str = Field(default="desc")
    description: str = Field(default="", max_length=1000)


class ComparisonSchema(Schema):
    name: str = Field(..., min_length=1, max_length=200)
    asset_ids: List[int] = Field(..., min_length=2, max_length=10)
    metrics: Optional[List[str]] = None


@router.get("/search")
def universal_search(
    request, q: str, asset_types: Optional[str] = None, limit: int = 20, offset: int = 0
):
    """Universal search across all asset types"""
    if not search_service:
        return {"error": "Search service not available"}, 503

    try:
        types = asset_types.split(",") if asset_types else None
        result = search_service.universal_search(
            query=q,
            asset_types=types,
            limit=limit,
            offset=offset,
            user_id=getattr(request, "auth", None)
            and getattr(request.auth, "id", 0)
            or 0,
        )
        return result
    except Exception as e:
        return {"error": str(e)}, 500


@router.post("/search/advanced")
def advanced_search(request, data: AdvancedSearchSchema):
    """Advanced search with filters"""
    if not search_service:
        return {"error": "Search service not available"}, 503

    try:
        filters = {}
        if data.asset_types:
            filters["asset_type"] = data.asset_types
        if data.sector:
            filters["sector"] = data.sector
        if data.exchange:
            filters["exchange"] = data.exchange
        if data.market_cap_min is not None:
            filters["market_cap_min"] = data.market_cap_min
        if data.market_cap_max is not None:
            filters["market_cap_max"] = data.market_cap_max
        if data.pe_ratio_min is not None:
            filters["pe_ratio_min"] = data.pe_ratio_min
        if data.pe_ratio_max is not None:
            filters["pe_ratio_max"] = data.pe_ratio_max
        if data.dividend_yield_min is not None:
            filters["dividend_yield_min"] = data.dividend_yield_min
        if data.volume_min is not None:
            filters["volume_min"] = data.volume_min
        if data.price_min is not None:
            filters["price_min"] = data.price_min
        if data.price_max is not None:
            filters["price_max"] = data.price_max
        if data.change_pct_min is not None:
            filters["change_pct_min"] = data.change_pct_min
        if data.change_pct_max is not None:
            filters["change_pct_max"] = data.change_pct_max

        result = search_service.advanced_search(
            query=data.q,
            filters=filters,
            sort_by=data.sort_by,
            sort_order=data.sort_order,
            limit=data.limit,
            offset=data.offset,
            user_id=getattr(request, "auth", None)
            and getattr(request.auth, "id", 0)
            or 0,
        )
        return result
    except Exception as e:
        return {"error": str(e)}, 500


@router.get("/search/suggestions")
def search_suggestions(request, q: str, limit: int = 10):
    """Get search suggestions"""
    if not search_service:
        return {"suggestions": []}

    try:
        suggestions = search_service._generate_suggestions(q, None)[:limit]
        return {"suggestions": suggestions}
    except Exception:
        return {"suggestions": []}


@router.get("/search/filters")
def get_filter_options(request):
    """Get available filter options"""
    if not search_service:
        return {"error": "Search service not available"}, 503

    try:
        return search_service.get_filter_options()
    except Exception as e:
        return {"error": str(e)}, 500


@router.get("/search/sectors")
def get_sectors(request):
    """Get available sectors"""
    if not search_service:
        return {"sectors": []}

    return {"sectors": search_service.get_sectors()}


@router.get("/search/exchanges")
def get_exchanges(request):
    """Get available exchanges"""
    if not search_service:
        return {"exchanges": []}

    return {"exchanges": search_service.get_exchanges()}


@router.get("/search/templates")
def get_screen_templates(request, category: Optional[str] = None):
    """Get pre-built screen templates"""
    if not search_service:
        return {"templates": []}

    return {"templates": search_service.get_screen_templates(category)}


@router.post("/search/saved")
def save_search(request, data: SaveSearchSchema):
    """Save a search configuration"""
    if not search_service:
        return {"error": "Search service not available"}, 503

    user_id = getattr(request, "auth", None) and getattr(request.auth, "id", 0) or 0
    if user_id == 0:
        return {"error": "Authentication required"}, 401

    try:
        result = search_service.save_search(
            user_id=user_id,
            name=data.name,
            query=data.query,
            filters=data.filters,
            sort_by=data.sort_by,
            sort_order=data.sort_order,
            description=data.description,
        )
        return result
    except Exception as e:
        return {"error": str(e)}, 500


@router.get("/search/saved")
def get_saved_searches(request):
    """Get user's saved searches"""
    if not search_service:
        return {"searches": []}

    user_id = getattr(request, "auth", None) and getattr(request.auth, "id", 0) or 0
    if user_id == 0:
        return {"searches": []}

    return {"searches": search_service.get_saved_searches(user_id)}


@router.post("/comparison")
def create_comparison(request, data: ComparisonSchema):
    """Create an asset comparison"""
    if not search_service:
        return {"error": "Search service not available"}, 503

    user_id = getattr(request, "auth", None) and getattr(request.auth, "id", 0) or 0
    if user_id == 0:
        return {"error": "Authentication required"}, 401

    try:
        result = search_service.create_comparison(
            user_id=user_id,
            name=data.name,
            asset_ids=data.asset_ids,
            metrics=data.metrics,
        )
        return result
    except Exception as e:
        return {"error": str(e)}, 500


@router.get("/comparison/{comparison_id}")
def get_comparison(request, comparison_id: int):
    """Get an asset comparison"""
    if not search_service:
        return {"error": "Search service not available"}, 503

    try:
        result = search_service.get_comparison(comparison_id)
        if "error" in result:
            return result, 404
        return result
    except Exception as e:
        return {"error": str(e)}, 500


@router.get("/search/quick")
def quick_search(request, q: str, type: Optional[str] = None):
    """Quick search for autocomplete - lightweight endpoint"""
    if not q or len(q) < 1:
        return {"results": []}

    try:
        from investments.models import Asset

        qs = Asset.objects.all()

        if type:
            qs = qs.filter(asset_type=type)

        qs = qs.filter(Q(symbol__istartswith=q.upper()[:4]) | Q(name__icontains=q))[:10]

        results = [
            {
                "symbol": a.symbol,
                "name": a.name[:50] + "..." if len(a.name) > 50 else a.name,
                "asset_type": a.asset_type,
                "exchange": getattr(a, "exchange", "") or "",
            }
            for a in qs
        ]

        return {"results": results}
    except Exception:
        return {"results": []}
