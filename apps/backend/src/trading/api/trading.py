from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from ninja import Router, Query, Schema
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth

from trading.models.order import Order, OrderType, OrderSide, OrderStatus
from trading.models.position import Position
from assets.models.asset import Asset
from portfolios.models.portfolio import Portfolio
from users.models.user import User

router = Router(tags=["Trading"])


class OrderCreateIn(Schema):
    """Input schema for creating a new order"""

    portfolio_id: str
    asset_id: str
    order_type: str  # market, limit, stop, stop_limit, oco
    side: str  # buy, sell
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: str = "day"
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None
    oco_linked_order_id: Optional[str] = None


class OrderUpdateIn(Schema):
    """Input schema for updating an existing order"""

    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: Optional[str] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None


class OrderOut(Schema):
    """Output schema for orders"""

    id: str
    user_id: str
    portfolio_id: str
    asset_id: str
    asset_symbol: str
    asset_name: str
    order_type: str
    side: str
    quantity: Decimal
    price: Optional[Decimal]
    stop_price: Optional[Decimal]
    status: str
    filled_quantity: Decimal
    remaining_quantity: Decimal
    filled_price: Optional[Decimal]
    average_fill_price: Optional[Decimal]
    fees: Decimal
    total_value: Optional[Decimal]
    time_in_force: str
    expiry_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    notes: Optional[str]
    is_active: bool
    is_oco: bool

    class Config:
        from_attributes = True


class PositionOut(Schema):
    """Output schema for positions"""

    id: str
    user_id: str
    portfolio_id: str
    asset_id: str
    asset_symbol: str
    asset_name: str
    side: str
    quantity: Decimal
    avg_entry_price: Decimal
    current_price: Optional[Decimal]
    market_value: Optional[Decimal]
    cost_basis: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_percent: Decimal
    realized_pnl: Decimal
    total_pnl: Decimal
    total_pnl_percent: Decimal
    total_fees: Decimal
    is_open: bool
    opened_at: datetime
    closed_at: Optional[datetime]
    days_open: int
    notes: Optional[str]

    class Config:
        from_attributes = True


class AccountSummaryOut(Schema):
    """Account summary including cash, margin, and buying power"""

    total_cash: Decimal
    available_cash: Decimal
    margin_used: Decimal
    margin_available: Decimal
    buying_power: Decimal
    total_positions_value: Decimal
    total_account_value: Decimal
    unrealized_pnl: Decimal
    realized_pnl_today: Decimal
    day_trading_volume: Decimal
    day_trades_count: int

    class Config:
        from_attributes = True


class PositionSummaryOut(Schema):
    """Summary statistics for positions"""

    total_positions: int
    open_positions: int
    long_positions: int
    short_positions: int
    total_market_value: Decimal
    total_unrealized_pnl: Decimal
    today_pnl: Decimal
    largest_win: Decimal
    largest_loss: Decimal
    win_rate: float


@router.post("/orders", response=OrderOut, auth=JWTAuth())
def create_order(request, payload: OrderCreateIn):
    """Create a new trading order"""
    user = request.auth
    portfolio = get_object_or_404(Portfolio, id=payload.portfolio_id, user=user)
    asset = get_object_or_404(Asset, id=payload.asset_id)

    # Validate order parameters
    if payload.quantity <= 0:
        from ninja.errors import HttpError

        raise HttpError(400, "Quantity must be greater than zero")

    if (
        payload.order_type in [OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT]
        and not payload.price
    ):
        from ninja.errors import HttpError

        raise HttpError(400, "Price is required for limit, stop, and stop-limit orders")

    if (
        payload.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]
        and not payload.stop_price
    ):
        from ninja.errors import HttpError

        raise HttpError(400, "Stop price is required for stop and stop-limit orders")

    # Create the order
    order = Order.objects.create(
        user=user,
        portfolio=portfolio,
        asset=asset,
        order_type=payload.order_type,
        side=payload.side,
        quantity=payload.quantity,
        price=payload.price,
        stop_price=payload.stop_price,
        time_in_force=payload.time_in_force,
        expiry_date=payload.expiry_date,
        notes=payload.notes,
    )

    # For OCO orders, create linked order
    if payload.order_type == OrderType.OCO and payload.oco_linked_order_id:
        order.oco_linked_order_id = payload.oco_linked_order_id

    return order


@router.get("/orders", response=List[OrderOut], auth=JWTAuth())
def list_orders(
    request,
    status: Optional[str] = Query(None),
    portfolio_id: Optional[str] = Query(None),
    asset_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List user's orders with filters"""
    user = request.auth
    qs = Order.objects.filter(user=user, is_deleted=False)

    if status:
        qs = qs.filter(status=status)

    if portfolio_id:
        qs = qs.filter(portfolio_id=portfolio_id)

    if asset_id:
        qs = qs.filter(asset_id=asset_id)

    return list(qs[offset : offset + limit].select_related("asset", "portfolio"))


@router.get("/orders/{order_id}", response=OrderOut, auth=JWTAuth())
def get_order(request, order_id: str):
    """Get details of a specific order"""
    user = request.auth
    order = get_object_or_404(Order, id=order_id, user=user, is_deleted=False)
    return order


@router.put("/orders/{order_id}", response=OrderOut, auth=JWTAuth())
def update_order(request, order_id: str, payload: OrderUpdateIn):
    """Update an existing order (only allowed for pending/partially filled orders)"""
    user = request.auth
    order = get_object_or_404(Order, id=order_id, user=user, is_deleted=False)

    # Only allow updates to active orders
    if not order.is_active:
        from ninja.errors import HttpError

        raise HttpError(400, "Can only update pending or partially filled orders")

    # Update fields
    if payload.price is not None:
        order.price = payload.price

    if payload.stop_price is not None:
        order.stop_price = payload.stop_price

    if payload.time_in_force is not None:
        order.time_in_force = payload.time_in_force

    if payload.expiry_date is not None:
        order.expiry_date = payload.expiry_date

    if payload.notes is not None:
        order.notes = payload.notes

    order.save()
    return order


@router.delete("/orders/{order_id}", auth=JWTAuth())
def cancel_order(request, order_id: str):
    """Cancel an existing order"""
    user = request.auth
    order = get_object_or_404(Order, id=order_id, user=user, is_deleted=False)

    if not order.is_active:
        from ninja.errors import HttpError

        raise HttpError(
            400, "Cannot cancel orders that are already filled or cancelled"
        )

    # Cancel linked OCO order if exists
    if order.oco_linked_order:
        try:
            linked_order = Order.objects.get(id=order.oco_linked_order_id)
            if linked_order.is_active:
                linked_order.status = OrderStatus.CANCELLED
                linked_order.save()
        except Order.DoesNotExist:
            pass

    order.status = OrderStatus.CANCELLED
    order.save()

    return {"success": True, "message": "Order cancelled successfully"}


@router.get("/positions", response=List[PositionOut], auth=JWTAuth())
def list_positions(
    request,
    portfolio_id: Optional[str] = Query(None),
    is_open: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List user's positions"""
    user = request.auth
    qs = Position.objects.filter(user=user, is_deleted=False)

    if portfolio_id:
        qs = qs.filter(portfolio_id=portfolio_id)

    if is_open is not None:
        qs = qs.filter(is_open=is_open)

    positions = list(qs[offset : offset + limit].select_related("asset", "portfolio"))

    # Update current prices for all positions
    for pos in positions:
        try:
            latest_price = Asset.objects.get(id=pos.asset_id)
            # Assuming Asset has a 'last_price' field
            pos.current_price = getattr(latest_price, "last_price", None)
            # Update unrealized P&L
            if pos.current_price and pos.is_open:
                pos.unrealized_pnl = (
                    pos.current_price - pos.avg_entry_price
                ) * pos.quantity
                pos.unrealized_pnl_percent = (
                    (pos.unrealized_pnl / pos.cost_basis) * Decimal("100")
                    if pos.cost_basis > 0
                    else Decimal("0")
                )
        except Asset.DoesNotExist:
            pass

    return positions


@router.get("/positions/{position_id}", response=PositionOut, auth=JWTAuth())
def get_position(request, position_id: str):
    """Get details of a specific position"""
    user = request.auth
    position = get_object_or_404(Position, id=position_id, user=user, is_deleted=False)
    return position


@router.post("/positions/{position_id}/close", auth=JWTAuth())
def close_position(request, position_id: str):
    """Close an open position at market price"""
    user = request.auth
    position = get_object_or_404(Position, id=position_id, user=user, is_deleted=False)

    if not position.is_open:
        from ninja.errors import HttpError

        raise HttpError(400, "Position is already closed")

    # Get current market price
    asset = get_object_or_404(Asset, id=position.asset_id)
    current_price = getattr(asset, "last_price", position.avg_entry_price)

    # Calculate P&L
    position.current_price = current_price
    position.unrealized_pnl = (
        current_price - position.avg_entry_price
    ) * position.quantity
    position.unrealized_pnl_percent = (
        (position.unrealized_pnl / position.cost_basis) * Decimal("100")
        if position.cost_basis > 0
        else Decimal("0")
    )

    # Close the position
    position.is_open = False
    position.closed_at = datetime.now()
    position.realized_pnl = position.unrealized_pnl
    position.unrealized_pnl = Decimal("0")
    position.unrealized_pnl_percent = Decimal("0")
    position.save()

    return {
        "success": True,
        "message": "Position closed successfully",
        "realized_pnl": float(position.realized_pnl),
        "closed_price": float(current_price),
    }


@router.get("/account/summary", response=AccountSummaryOut, auth=JWTAuth())
def get_account_summary(request):
    """Get account summary including cash, margin, and buying power"""
    user = request.auth

    # Get all positions
    positions = Position.objects.filter(user=user, is_open=True, is_deleted=False)

    # Calculate values
    total_positions_value = Decimal("0")
    total_unrealized_pnl = Decimal("0")

    for pos in positions:
        total_positions_value += pos.market_value if pos.market_value else Decimal("0")
        total_unrealized_pnl += pos.unrealized_pnl

    # Simulate account values (in production, these would come from broker API)
    total_cash = Decimal("100000")  # Default cash balance
    margin_used = total_positions_value * Decimal("0.5")  # Simulated margin
    margin_available = Decimal("50000") - margin_used  # Simulated margin limit
    buying_power = total_cash + margin_available
    total_account_value = total_cash + total_positions_value

    # Calculate today's realized P&L
    today = datetime.now().date()
    realized_pnl_today = Decimal("0")
    for pos in Position.objects.filter(user=user, closed_at__date=today):
        realized_pnl_today += pos.realized_pnl

    # Calculate today's trading volume and count
    day_trading_volume = Decimal("0")
    day_trades_count = 0
    for order in Order.objects.filter(
        user=user, status=OrderStatus.FILLED, created_at__date=today
    ):
        day_trading_volume += order.quantity if order.filled_price else Decimal("0")
        day_trades_count += 1

    return {
        "total_cash": total_cash,
        "available_cash": total_cash,
        "margin_used": margin_used,
        "margin_available": margin_available,
        "buying_power": buying_power,
        "total_positions_value": total_positions_value,
        "total_account_value": total_account_value,
        "unrealized_pnl": total_unrealized_pnl,
        "realized_pnl_today": realized_pnl_today,
        "day_trading_volume": day_trading_volume,
        "day_trades_count": day_trades_count,
    }


@router.get("/positions/summary", response=PositionSummaryOut, auth=JWTAuth())
def get_positions_summary(
    request,
    portfolio_id: Optional[str] = Query(None),
):
    """Get summary statistics for user's positions"""
    user = request.auth
    qs = Position.objects.filter(user=user, is_deleted=False)

    if portfolio_id:
        qs = qs.filter(portfolio_id=portfolio_id)

    positions = list(qs)

    # Calculate statistics
    total_positions = len(positions)
    open_positions = len([p for p in positions if p.is_open])
    long_positions = len([p for p in positions if p.side == "long" and p.is_open])
    short_positions = len([p for p in positions if p.side == "short" and p.is_open])

    total_market_value = sum(p.market_value for p in positions if p.market_value)
    total_unrealized_pnl = sum(p.unrealized_pnl for p in positions)

    # Calculate today's P&L
    today = datetime.now().date()
    today_pnl = sum(
        p.realized_pnl for p in positions if p.closed_at and p.closed_at.date() == today
    )
    today_pnl += sum(p.unrealized_pnl for p in positions if p.is_open)

    # Find largest win and loss
    realized_values = [p.realized_pnl for p in positions if p.closed_at]
    largest_win = max(realized_values) if realized_values else Decimal("0")
    largest_loss = min(realized_values) if realized_values else Decimal("0")

    # Calculate win rate
    winning_positions = len([p for p in positions if p.realized_pnl > 0])
    closed_positions = len([p for p in positions if p.closed_at])
    win_rate = (winning_positions / closed_positions) if closed_positions > 0 else 0.0

    return {
        "total_positions": total_positions,
        "open_positions": open_positions,
        "long_positions": long_positions,
        "short_positions": short_positions,
        "total_market_value": total_market_value,
        "total_unrealized_pnl": total_unrealized_pnl,
        "today_pnl": today_pnl,
        "largest_win": float(largest_win),
        "largest_loss": float(largest_loss),
        "win_rate": win_rate,
    }
