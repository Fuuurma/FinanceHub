# investments/api.py
from datetime import date
from ninja import Router
from ninja.pagination import LimitOffsetPagination
from ninja_jwt.authentication import JWTAuth
from typing import List, Optional

from assets.models.price_history import PriceHistory
from portfolios.models.portfolio import Portfolio
from portfolios.schemas.schemas import (
    AssetOut,
    HoldingCreate,
    HoldingOut,
    PortfolioCreate,
    PortfolioOut,
    PriceCreate,
    PriceOut,
    TransactionCreate,
    TransactionOut,
)
from utils.helpers.error_handler.exceptions import (
    PermissionDeniedException,
    ResourceNotFoundException,
)

from assets.models import Asset
from utils.helpers.logger.audit_logger import AuditLogger
from utils.helpers.logger.logger import get_logger
from utils.services.holding import HoldingService
from utils.services.portfolio import PortfolioService

from django.shortcuts import get_object_or_404

from utils.services.transaction import TransactionService

logger = get_logger(__name__)
router = Router(tags=["investments"])

audit_logger = AuditLogger()


# === PORTFOLIOS ===
@router.post("/portfolios", response=PortfolioOut, auth=JWTAuth())
def create_portfolio(request, payload: PortfolioCreate):
    portfolio = PortfolioService.create_portfolio(request.auth, payload.dict())
    audit_logger.user_action(
        user_id=str(request.auth.id),
        action="portfolio_created",
        resource_type="portfolio",
        resource_id=str(portfolio.id),
    )
    return portfolio


@router.get(
    "/portfolios",
    response=List[PortfolioOut],
    auth=JWTAuth(),
    pagination=LimitOffsetPagination,
)
def list_portfolios(request):
    qs = PortfolioService.get_user_portfolios(request.auth)
    for p in qs:
        p.current_value = PortfolioService.calculate_portfolio_value(p)
    return qs


@router.get("/portfolios/{portfolio_id}", response=PortfolioOut, auth=JWTAuth())
def get_portfolio(request, portfolio_id: str):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    portfolio.current_value = PortfolioService.calculate_portfolio_value(portfolio)
    return portfolio


# === HOLDINGS ===
@router.post("/portfolios/{portfolio_id}/holdings", response=HoldingOut, auth=JWTAuth())
def add_holding(request, portfolio_id: str, payload: HoldingCreate):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    holding = HoldingService.add_holding(portfolio, payload.asset_id, payload.quantity)
    audit_logger.user_action(
        user_id=str(request.auth.id),
        action="holding_added",
        resource_type="holding",
        resource_id=str(holding.id),
    )
    return holding


@router.get(
    "/portfolios/{portfolio_id}/holdings", response=List[HoldingOut], auth=JWTAuth()
)
def list_holdings(request, portfolio_id: str):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    holdings = portfolio.holdings.select_related("asset").prefetch_related(
        "asset__prices"
    )
    for h in holdings:
        latest = h.asset.prices.order_by("-date").first()
        h.current_price = latest.close if latest else None
        h.current_value = h.current_price * h.quantity if h.current_price else None
    return holdings


# === TRANSACTIONS ===
@router.post(
    "/portfolios/{portfolio_id}/transactions", response=TransactionOut, auth=JWTAuth()
)
def record_transaction(request, portfolio_id: str, payload: TransactionCreate):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    transaction = TransactionService.record_transaction(portfolio, payload.dict())
    audit_logger.user_action(
        user_id=str(request.auth.id),
        action=f"transaction_{transaction.transaction_type}",
        resource_type="transaction",
        resource_id=str(transaction.id),
        details={"amount": str(transaction.total_amount)},
    )
    return transaction


@router.get(
    "/portfolios/{portfolio_id}/transactions",
    response=List[TransactionOut],
    auth=JWTAuth(),
)
def list_transactions(request, portfolio_id: str):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    return portfolio.transactions.select_related("asset").order_by("-date")


# === ASSETS & PRICES (Public read, Admin write) ===
@router.get("/assets", response=List[AssetOut])
def list_assets(request, search: Optional[str] = None):
    qs = Asset.objects.all()
    if search:
        qs = qs.filter(ticker__icontains=search) | qs.filter(name__icontains=search)
    return qs


@router.get("/assets/{asset_id}/prices", response=List[PriceOut])
def get_prices(
    request,
    asset_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    asset = get_object_or_404(Asset, id=asset_id)
    qs = asset.prices.all()
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)
    return qs.order_by("date")


# Admin-only price creation (or via background job later)
@router.post("/assets/{asset_id}/prices", response=PriceOut, auth=JWTAuth())
def add_price(request, asset_id: str, payload: PriceCreate):
    if not request.auth.is_staff:
        raise PermissionDeniedException()
    asset = get_object_or_404(Asset, id=asset_id)
    price = PriceHistory.objects.create(asset=asset, **payload.dict())
    return price
