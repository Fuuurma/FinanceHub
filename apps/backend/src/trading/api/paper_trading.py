from decimal import Decimal, InvalidOperation
from typing import Optional
from ninja import Router, Schema
from ninja_jwt.authentication import JWTAuth
from trading.services.paper_trading_service import PaperTradingService

router = Router(tags=["Paper Trading"], auth=JWTAuth())

service = PaperTradingService()


class AccountOut(Schema):
    cash_balance: float
    starting_balance: float
    total_trades: int
    win_rate: float
    reset_count: int


class PaperTradingSummaryOut(Schema):
    cash_balance: float
    portfolio_value: float
    total_value: float
    total_return: float
    positions: list
    total_trades: int
    win_rate: float
    winning_trades: int
    losing_trades: int


class AccountDetailOut(Schema):
    account: AccountOut
    summary: PaperTradingSummaryOut


class BuyIn(Schema):
    asset: str
    quantity: Decimal


class BuyOut(Schema):
    success: bool
    trade_id: Optional[str] = None
    asset: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    total_value: Optional[float] = None
    remaining_cash: Optional[float] = None
    error: Optional[str] = None


class SellIn(Schema):
    asset: str
    quantity: Decimal


class SellOut(Schema):
    success: bool
    trade_id: Optional[str] = None
    asset: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    total_value: Optional[float] = None
    profit_loss: Optional[float] = None
    remaining_cash: Optional[float] = None
    error: Optional[str] = None


class ResetOut(Schema):
    success: bool
    message: str
    new_balance: float


class TradeOut(Schema):
    id: str
    asset: str
    type: str
    quantity: float
    price: float
    total_value: float
    executed_at: str
    profit_loss: Optional[float] = None


class TradeHistoryOut(Schema):
    trades: list


class PerformanceOut(Schema):
    total_return: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int


@router.get("/account", response=AccountDetailOut)
def get_account(request):
    account = service.get_or_create_account(request.user)
    summary = service.get_portfolio_summary(request.user)
    return {
        "account": {
            "cash_balance": float(account.cash_balance),
            "starting_balance": float(account.starting_balance),
            "total_trades": account.total_trades,
            "win_rate": account.win_rate,
            "reset_count": account.reset_count,
        },
        "summary": summary,
    }


@router.post("/buy", response=BuyOut)
def buy_asset(request, data: BuyIn):
    if data.quantity <= 0:
        return BuyOut(success=False, error="Quantity must be positive")

    result = service.execute_buy_order(request.user, data.asset.upper(), data.quantity)

    if not result.get("success"):
        return BuyOut(success=False, error=result.get("error"))

    return BuyOut(
        success=True,
        trade_id=result.get("trade_id"),
        asset=result.get("asset"),
        quantity=result.get("quantity"),
        price=result.get("price"),
        total_value=result.get("total_value"),
        remaining_cash=result.get("remaining_cash"),
    )


@router.post("/sell", response=SellOut)
def sell_asset(request, data: SellIn):
    if data.quantity <= 0:
        return SellOut(success=False, error="Quantity must be positive")

    result = service.execute_sell_order(request.user, data.asset.upper(), data.quantity)

    if not result.get("success"):
        return SellOut(success=False, error=result.get("error"))

    return SellOut(
        success=True,
        trade_id=result.get("trade_id"),
        asset=result.get("asset"),
        quantity=result.get("quantity"),
        price=result.get("price"),
        total_value=result.get("total_value"),
        profit_loss=result.get("profit_loss"),
        remaining_cash=result.get("remaining_cash"),
    )


@router.post("/reset", response=ResetOut)
def reset_account(request):
    account = service.get_or_create_account(request.user)
    account.reset_account()
    return {
        "success": True,
        "message": "Account reset successfully",
        "new_balance": float(account.cash_balance),
    }


@router.get("/history", response=TradeHistoryOut)
def get_history(request, limit: int = 100):
    trades = service.get_trade_history(request.user, limit)
    return {"trades": trades}


@router.get("/performance", response=PerformanceOut)
def get_performance(request):
    summary = service.get_portfolio_summary(request.user)
    return {
        "total_return": summary["total_return"],
        "win_rate": summary["win_rate"],
        "total_trades": summary["total_trades"],
        "winning_trades": summary["winning_trades"],
        "losing_trades": summary["losing_trades"],
    }
