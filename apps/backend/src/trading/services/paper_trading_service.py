import random
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from trading.models import PaperTradingAccount, PaperTrade
from assets.models.asset import Asset
from assets.models.historic.prices import AssetPricesHistoric


class MarketDataService:
    def get_current_price(self, symbol: str) -> Optional[float]:
        try:
            asset = Asset.objects.get(symbol__iexact=symbol, is_active=True)
            latest_price = (
                AssetPricesHistoric.objects.filter(asset=asset)
                .order_by("-timestamp")
                .first()
            )
            if latest_price:
                return float(latest_price.close)
            return None
        except Asset.DoesNotExist:
            return None


class PaperTradingService:
    def __init__(self):
        self.market_data = MarketDataService()

    def get_or_create_account(self, user) -> PaperTradingAccount:
        account, created = PaperTradingAccount.objects.get_or_create(
            user=user,
            defaults={
                "cash_balance": Decimal("100000.00"),
                "starting_balance": Decimal("100000.00"),
            },
        )

        if created:
            account.last_reset_at = timezone.now()
            account.save()

        return account

    def execute_buy_order(self, user, asset_symbol: str, quantity: Decimal) -> Dict:
        account = self.get_or_create_account(user)

        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            return {"success": False, "error": "Asset not found"}

        try:
            current_price = self.market_data.get_current_price(asset_symbol)
            if current_price is None:
                return {"success": False, "error": "Price not available"}
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            return {"success": False, "error": f"Error fetching price: {str(e)}"}

        trade_value = Decimal(str(current_price)) * quantity

        if trade_value > account.cash_balance:
            return {
                "success": False,
                "error": "Insufficient funds",
                "required": float(trade_value),
                "available": float(account.cash_balance),
            }

        slippage = random.uniform(-0.001, 0.001)
        execution_price = Decimal(str(current_price)) * (
            Decimal("1") + Decimal(str(slippage))
        )

        with transaction.atomic():
            account.cash_balance -= trade_value
            account.total_trades += 1
            account.save()

            trade = PaperTrade.objects.create(
                account=account,
                asset=asset,
                trade_type="BUY",
                quantity=quantity,
                price=execution_price,
                total_value=trade_value,
                slippage=slippage * 100,
            )

        return {
            "success": True,
            "trade_id": str(trade.id),
            "asset": asset_symbol,
            "quantity": float(quantity),
            "price": float(execution_price),
            "total_value": float(trade_value),
            "remaining_cash": float(account.cash_balance),
        }

    def execute_sell_order(self, user, asset_symbol: str, quantity: Decimal) -> Dict:
        account = self.get_or_create_account(user)

        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            return {"success": False, "error": "Asset not found"}

        current_position = self.get_position(account, asset_symbol)
        if current_position < quantity:
            return {
                "success": False,
                "error": "Insufficient position",
                "owned": float(current_position),
                "requested": float(quantity),
            }

        try:
            current_price = self.market_data.get_current_price(asset_symbol)
            if current_price is None:
                return {"success": False, "error": "Price not available"}
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            return {"success": False, "error": f"Error fetching price: {str(e)}"}

        trade_value = Decimal(str(current_price)) * quantity
        avg_buy_price = self.get_average_buy_price(account, asset_symbol)
        profit_loss = (Decimal(str(current_price)) - avg_buy_price) * quantity

        if profit_loss > 0:
            account.winning_trades += 1
        else:
            account.losing_trades += 1

        slippage = random.uniform(-0.001, 0.001)
        execution_price = Decimal(str(current_price)) * (
            Decimal("1") + Decimal(str(slippage))
        )

        with transaction.atomic():
            account.cash_balance += trade_value
            account.total_trades += 1
            account.save()

            trade = PaperTrade.objects.create(
                account=account,
                asset=asset,
                trade_type="SELL",
                quantity=quantity,
                price=execution_price,
                total_value=trade_value,
                slippage=slippage * 100,
                profit_loss=profit_loss,
                is_winning=(profit_loss > 0),
            )

        return {
            "success": True,
            "trade_id": str(trade.id),
            "asset": asset_symbol,
            "quantity": float(quantity),
            "price": float(execution_price),
            "total_value": float(trade_value),
            "profit_loss": float(profit_loss),
            "remaining_cash": float(account.cash_balance),
        }

    def get_position(self, account: PaperTradingAccount, asset_symbol: str) -> Decimal:
        from django.db.models import Sum

        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            return Decimal("0")

        buys = PaperTrade.objects.filter(
            account=account, asset=asset, trade_type="BUY"
        ).aggregate(total=Sum("quantity"))["total"] or Decimal("0")

        sells = PaperTrade.objects.filter(
            account=account, asset=asset, trade_type="SELL"
        ).aggregate(total=Sum("quantity"))["total"] or Decimal("0")

        return buys - sells

    def get_average_buy_price(
        self, account: PaperTradingAccount, asset_symbol: str
    ) -> Decimal:
        from django.db.models import Sum

        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            return Decimal("0")

        buy_trades = PaperTrade.objects.filter(
            account=account, asset=asset, trade_type="BUY"
        )

        total_value = buy_trades.aggregate(total=Sum("total_value"))[
            "total"
        ] or Decimal("0")
        total_quantity = buy_trades.aggregate(total=Sum("quantity"))[
            "total"
        ] or Decimal("0")

        if total_quantity == 0:
            return Decimal("0")

        return total_value / total_quantity

    def calculate_portfolio_value(self, user) -> Decimal:
        account = self.get_or_create_account(user)

        assets_with_positions = (
            PaperTrade.objects.filter(account=account)
            .values_list("asset__symbol", flat=True)
            .distinct()
        )

        total_value = Decimal("0")

        for symbol in assets_with_positions:
            position = self.get_position(account, symbol)

            if position > 0:
                try:
                    current_price = self.market_data.get_current_price(symbol)
                    if current_price:
                        position_value = Decimal(str(current_price)) * position
                        total_value += position_value
                except:
                    continue

        return total_value

    def get_portfolio_summary(self, user) -> Dict:
        account = self.get_or_create_account(user)

        assets_with_positions = (
            PaperTrade.objects.filter(account=account)
            .values_list("asset__symbol", flat=True)
            .distinct()
        )

        positions = []
        total_cost_basis = Decimal("0")
        total_market_value = Decimal("0")

        for symbol in assets_with_positions:
            position = self.get_position(account, symbol)

            if position > 0:
                try:
                    asset = Asset.objects.get(symbol=symbol)
                    current_price = self.market_data.get_current_price(symbol)
                    avg_buy_price = self.get_average_buy_price(account, symbol)

                    if current_price:
                        market_value = Decimal(str(current_price)) * position
                        cost_basis = avg_buy_price * position
                        profit_loss = market_value - cost_basis

                        positions.append(
                            {
                                "symbol": symbol,
                                "name": asset.name,
                                "quantity": float(position),
                                "avg_price": float(avg_buy_price),
                                "current_price": float(current_price),
                                "market_value": float(market_value),
                                "cost_basis": float(cost_basis),
                                "profit_loss": float(profit_loss),
                                "profit_loss_pct": float(
                                    (profit_loss / cost_basis) * 100
                                )
                                if cost_basis > 0
                                else 0,
                            }
                        )

                        total_cost_basis += cost_basis
                        total_market_value += market_value
                except:
                    continue

        return {
            "cash_balance": float(account.cash_balance),
            "portfolio_value": float(total_market_value),
            "total_value": float(account.cash_balance + total_market_value),
            "total_return": float(
                (
                    (
                        account.cash_balance
                        + total_market_value
                        - account.starting_balance
                    )
                    / account.starting_balance
                )
                * 100
            ),
            "positions": positions,
            "total_trades": account.total_trades,
            "win_rate": account.win_rate,
            "winning_trades": account.winning_trades,
            "losing_trades": account.losing_trades,
        }

    def get_trade_history(self, user, limit: int = 100) -> List[Dict]:
        account = self.get_or_create_account(user)

        trades = (
            PaperTrade.objects.filter(account=account)
            .select_related("asset")
            .order_by("-executed_at")[:limit]
        )

        return [
            {
                "id": str(trade.id),
                "asset": trade.asset.symbol,
                "type": trade.trade_type,
                "quantity": float(trade.quantity),
                "price": float(trade.price),
                "total_value": float(trade.total_value),
                "executed_at": trade.executed_at.isoformat(),
                "profit_loss": float(trade.profit_loss) if trade.profit_loss else None,
            }
            for trade in trades
        ]
