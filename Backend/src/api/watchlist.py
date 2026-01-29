from typing import List, Optional, Dict
from ninja import Router, Query
from pydantic import BaseModel
from django.shortcuts import get_object_or_404
from django.db import transaction
from ninja_jwt.authentication import JWTAuth

from assets.models.asset import Asset
from investments.models.watchlist import Watchlist
from utils.constants.api import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    DEFAULT_OFFSET,
    RATE_LIMITS,
    CACHE_TTLS,
)
from utils.api.decorators import api_endpoint
from core.exceptions import NotFoundException, ValidationException


jwt_auth = JWTAuth()
router = Router(tags=["Watchlist"])


class Message(BaseModel):
    message: str


class WatchlistOut(BaseModel):
    id: str
    name: str
    assets: List[str]
    is_public: bool
    created_at: str

    class Config:
        from_attributes = True


class WatchlistCreateIn(BaseModel):
    name: str
    symbols: List[str] = []
    is_public: bool = False


class WatchlistUpdateIn(BaseModel):
    name: str
    symbols: List[str] = []
    is_public: bool = False


def _get_assets_by_symbol(symbols: List[str]) -> Dict[str, Asset]:
    """Bulk fetch assets to avoid N+1 queries."""
    if not symbols:
        return {}
    upper_symbols = [s.upper() for s in symbols]
    return {
        asset.symbol.upper(): asset
        for asset in Asset.objects.filter(symbol__in=upper_symbols)
    }


@router.get("/watchlist", response=List[WatchlistOut], auth=jwt_auth)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['read'], key_prefix="watchlist")
def list_watchlists(
    request,
    limit: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(default=DEFAULT_OFFSET, ge=0),
):
    """List user's watchlists with pagination."""
    watchlists = Watchlist.objects.filter(user=request.user)[
        offset : offset + limit
    ]
    return [
        WatchlistOut(
            id=str(w.id),
            name=w.name,
            assets=w.asset_symbols,
            is_public=w.is_public,
            created_at=w.created_at.isoformat(),
        )
        for w in watchlists
    ]


@router.get("/watchlist/{watchlist_id}", response=WatchlistOut, auth=jwt_auth)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['read'], key_prefix="watchlist")
def get_watchlist(request, watchlist_id: str):
    """Get a specific watchlist."""
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    return WatchlistOut(
        id=str(watchlist.id),
        name=watchlist.name,
        assets=watchlist.asset_symbols,
        is_public=watchlist.is_public,
        created_at=watchlist.created_at.isoformat(),
    )


@router.post("/watchlist", response=WatchlistOut, auth=jwt_auth)
@api_endpoint(rate=RATE_LIMITS['write'], key_prefix="watchlist")
@transaction.atomic
def create_watchlist(request, data: WatchlistCreateIn):
    """Create a new watchlist with bulk asset lookup (N+1 fix).

    Uses database transaction to ensure atomicity of watchlist creation
    and asset association.
    """
    watchlist = Watchlist.objects.create(
        user=request.user,
        name=data.name,
        is_public=data.is_public,
    )
    if data.symbols:
        assets_map = _get_assets_by_symbol(data.symbols)
        assets_to_add = [
            assets_map[s.upper()]
            for s in data.symbols
            if s.upper() in assets_map
        ]
        if assets_to_add:
            watchlist.assets.add(*assets_to_add)
    return WatchlistOut(
        id=str(watchlist.id),
        name=watchlist.name,
        assets=watchlist.asset_symbols,
        is_public=watchlist.is_public,
        created_at=watchlist.created_at.isoformat(),
    )


@router.put("/watchlist/{watchlist_id}", response=WatchlistOut, auth=jwt_auth)
@api_endpoint(rate=RATE_LIMITS['write'], key_prefix="watchlist")
@transaction.atomic
def update_watchlist(request, watchlist_id: str, data: WatchlistUpdateIn):
    """Update watchlist with bulk asset lookup (N+1 fix).

    Uses database transaction to ensure atomicity of watchlist update
    and asset re-association.
    """
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    watchlist.name = data.name
    watchlist.is_public = data.is_public

    if data.symbols:
        assets_map = _get_assets_by_symbol(data.symbols)
        assets_to_set = [
            assets_map[s.upper()]
            for s in data.symbols
            if s.upper() in assets_map
        ]
        watchlist.assets.set(assets_to_set)
    else:
        watchlist.assets.clear()

    watchlist.save()
    return WatchlistOut(
        id=str(watchlist.id),
        name=watchlist.name,
        assets=watchlist.asset_symbols,
        is_public=watchlist.is_public,
        created_at=watchlist.created_at.isoformat(),
    )


@router.delete("/watchlist/{watchlist_id}", response=Message, auth=jwt_auth)
@api_endpoint(rate=RATE_LIMITS['write'], key_prefix="watchlist")
def delete_watchlist(request, watchlist_id: str):
    """Delete a watchlist."""
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    watchlist.delete()
    return Message(message="Watchlist deleted successfully")


@router.post(
    "/watchlist/{watchlist_id}/assets", response=WatchlistOut, auth=jwt_auth
)
@api_endpoint(rate=RATE_LIMITS['write'], key_prefix="watchlist")
def add_asset_to_watchlist(request, watchlist_id: str, symbol: str = Query(...)):
    """Add an asset to a watchlist."""
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    asset = get_object_or_404(Asset, symbol__iexact=symbol)
    watchlist.assets.add(asset)
    return WatchlistOut(
        id=str(watchlist.id),
        name=watchlist.name,
        assets=watchlist.asset_symbols,
        is_public=watchlist.is_public,
        created_at=watchlist.created_at.isoformat(),
    )


@router.delete(
    "/watchlist/{watchlist_id}/assets/{symbol}",
    response=WatchlistOut,
    auth=jwt_auth,
)
@api_endpoint(rate=RATE_LIMITS['write'], key_prefix="watchlist")
def remove_asset_from_watchlist(request, watchlist_id: str, symbol: str):
    """Remove an asset from a watchlist."""
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    asset = Asset.objects.filter(symbol__iexact=symbol).first()
    if asset:
        watchlist.assets.remove(asset)
    return WatchlistOut(
        id=str(watchlist.id),
        name=watchlist.name,
        assets=watchlist.asset_symbols,
        is_public=watchlist.is_public,
        created_at=watchlist.created_at.isoformat(),
    )
