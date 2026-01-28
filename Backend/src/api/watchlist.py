from typing import List
from ninja import Router, Query
from pydantic import BaseModel
from django.shortcuts import get_object_or_404
from investments.models.watchlist import Watchlist
from assets.models.asset import Asset
from investments.schemas import Message
from utils.auth import jwt_auth_required

router = Router(tags=["Watchlist"])


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


@router.get("/watchlist", response=List[WatchlistOut], auth=jwt_auth_required)
def list_watchlists(request):
    watchlists = Watchlist.objects.filter(user=request.user)
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


@router.get("/watchlist/{watchlist_id}", response=WatchlistOut, auth=jwt_auth_required)
def get_watchlist(request, watchlist_id: str):
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    return WatchlistOut(
        id=str(watchlist.id),
        name=watchlist.name,
        assets=watchlist.asset_symbols,
        is_public=watchlist.is_public,
        created_at=watchlist.created_at.isoformat(),
    )


@router.post("/watchlist", response=WatchlistOut, auth=jwt_auth_required)
def create_watchlist(request, data: WatchlistCreateIn):
    watchlist = Watchlist.objects.create(
        user=request.user,
        name=data.name,
        is_public=data.is_public,
    )
    for symbol in data.symbols:
        asset = Asset.objects.filter(symbol__iexact=symbol).first()
        if asset:
            watchlist.assets.add(asset)
    return WatchlistOut(
        id=str(watchlist.id),
        name=watchlist.name,
        assets=watchlist.asset_symbols,
        is_public=watchlist.is_public,
        created_at=watchlist.created_at.isoformat(),
    )


@router.put("/watchlist/{watchlist_id}", response=WatchlistOut, auth=jwt_auth_required)
def update_watchlist(request, watchlist_id: str, data: WatchlistUpdateIn):
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    watchlist.name = data.name
    watchlist.is_public = data.is_public
    watchlist.assets.clear()
    for symbol in data.symbols:
        asset = Asset.objects.filter(symbol__iexact=symbol).first()
        if asset:
            watchlist.assets.add(asset)
    watchlist.save()
    return WatchlistOut(
        id=str(watchlist.id),
        name=watchlist.name,
        assets=watchlist.asset_symbols,
        is_public=watchlist.is_public,
        created_at=watchlist.created_at.isoformat(),
    )


@router.delete("/watchlist/{watchlist_id}", response=Message, auth=jwt_auth_required)
def delete_watchlist(request, watchlist_id: str):
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    watchlist.delete()
    return Message(message="Watchlist deleted successfully")


@router.post("/watchlist/{watchlist_id}/assets", response=WatchlistOut, auth=jwt_auth_required)
def add_asset_to_watchlist(request, watchlist_id: str, symbol: str = Query(...)):
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


@router.delete("/watchlist/{watchlist_id}/assets/{symbol}", response=WatchlistOut, auth=jwt_auth_required)
def remove_asset_from_watchlist(request, watchlist_id: str, symbol: str):
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
