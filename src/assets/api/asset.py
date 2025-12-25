from typing import List, Optional
from ninja import Router, Query, Schema
from django.db.models import Q

from assets.models.asset import Asset

router = Router(tags=["Assets"])


class AssetFilter(Schema):
    search: Optional[str] = None
    category: Optional[str] = None


@router.get("/", response=List[AssetOut])
def list_assets(
    request, filters: AssetFilter = Query(...), limit: int = 20, offset: int = 0
):
    """Search for assets with pagination"""
    qs = Asset.objects.all()
    if filters.search:
        qs = qs.filter(
            Q(symbol__icontains=filters.search) | Q(name__icontains=filters.search)
        )
    if filters.category:
        qs = qs.filter(category__slug=filters.category)

    return qs[offset : offset + limit]


@router.get("/{asset_id}/prices", response=List[PriceHistoryOut])
def get_price_history(request, asset_id: str, days: int = 30):
    """Returns price data for charts"""
    return AssetPriceHistory.objects.filter(asset_id=asset_id).order_by("-timestamp")[
        :days
    ]
