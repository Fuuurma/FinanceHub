import asyncio
import json
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from trading.models import PaperTradingAccount, PaperTradingOrder, PaperPosition
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


class WebSocketBroadcaster:
    def __init__(self):
        self.channel_layer = get_channel_layer()

    def broadcast_to_user(self, user_id: int, event_type: str, data: Dict):
        group_name = f"paper_trading_{user_id}"
        async_to_sync(self.channel_layer.group_send)(
            group_name, {"type": event_type, "data": data}
        )

    def broadcast_portfolio_update(self, portfolio: PaperTradingAccount):
        self.broadcast_to_user(
            portfolio.user_id,
            "portfolio_update",
            {
                "cash_balance": float(portfolio.cash_balance),
                "portfolio_value": float(portfolio.portfolio_value),
                "total_return": float(portfolio.total_return),
            },
        )

    def broadcast_order_update(self, order: PaperTradingOrder):
        self.broadcast_to_user(
            order.portfolio.user_id,
            "order_update",
            {
                "order_id": str(order.id),
                "status": order.status,
                "side": order.side,
                "symbol": order.asset.symbol,
                "quantity": float(order.quantity),
                "filled_price": float(order.filled_price)
                if order.filled_price
                else None,
                "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            },
        )

    def broadcast_position_update(self, position: PaperPosition):
        self.broadcast_to_user(
            position.portfolio.user_id,
            "position_update",
            {
                "position_id": str(position.id),
                "symbol": position.asset.symbol,
                "quantity": float(position.quantity),
                "avg_price": float(position.avg_price),
            },
        )


class PaperTradingEngine:
    def __init__(self):
        self.market_data = MarketDataService()
        self.broadcaster = WebSocketBroadcaster()

    def get_or_create_portfolio(self, user) -> PaperTradingAccount:
        portfolio, created = PaperTradingAccount.objects.get_or_create(
            user=user,
            defaults={
                "cash_balance": Decimal("100000.00"),
                "starting_balance": Decimal("100000.00"),
            },
        )
        if created:
            portfolio.last_reset_at = timezone.now()
            portfolio.save()
        return portfolio

    @transaction.atomic
    def execute_market_order(
        self, portfolio, asset_symbol: str, side: str, quantity: Decimal
    ) -> PaperTradingOrder:
        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            order = PaperTradingOrder(
                portfolio=portfolio,
                asset_id=None,
                order_type="market",
                side=side,
                quantity=quantity,
            )
            order.reject(f"Asset {asset_symbol} not found")
            return order

        current_price = self.market_data.get_current_price(asset_symbol)
        if current_price is None:
            order = PaperTradingOrder(
                portfolio=portfolio,
                asset=asset,
                order_type="market",
                side=side,
                quantity=quantity,
            )
            order.reject("Price not available")
            return order

        order = PaperTradingOrder.objects.create(
            portfolio=portfolio,
            asset=asset,
            order_type="market",
            side=side,
            quantity=quantity,
        )

        try:
            if side == "buy":
                return self._execute_buy_order(
                    portfolio, order, Decimal(str(current_price))
                )
            else:
                return self._execute_sell_order(
                    portfolio, order, Decimal(str(current_price))
                )
        except Exception as e:
            order.reject(str(e))
            return order

    def _execute_buy_order(
        self,
        portfolio: PaperTradingAccount,
        order: PaperTradingOrder,
        current_price: Decimal,
    ) -> PaperTradingOrder:
        required = order.quantity * current_price
        if portfolio.cash_balance < required:
            order.reject(
                f"Insufficient funds. Required: ${required}, Available: ${portfolio.cash_balance}"
            )
            self.broadcaster.broadcast_order_update(order)
            return order

        portfolio.cash_balance -= required
        portfolio.save()

        order.fill(current_price)

        self._update_position(portfolio, order.asset, order.quantity, current_price)

        self._recalculate_portfolio(portfolio)
        self.broadcaster.broadcast_order_update(order)
        self.broadcaster.broadcast_portfolio_update(portfolio)

        return order

    def _execute_sell_order(
        self,
        portfolio: PaperTradingAccount,
        order: PaperTradingOrder,
        current_price: Decimal,
    ) -> PaperTradingOrder:
        position = portfolio.positions.filter(asset=order.asset).first()
        if not position or position.quantity < order.quantity:
            order.reject(
                f"Insufficient position. Required: {order.quantity}, Available: {position.quantity if position else 0}"
            )
            self.broadcaster.broadcast_order_update(order)
            return order

        portfolio.cash_balance += order.quantity * current_price
        portfolio.save()

        order.fill(current_price)

        if position.quantity == order.quantity:
            position.delete()
        else:
            position.quantity -= order.quantity
            position.avg_price = (
                (position.quantity + order.quantity) * position.avg_price
                - order.quantity * current_price
            ) / position.quantity
            position.save()

        self._recalculate_portfolio(portfolio)
        self.broadcaster.broadcast_order_update(order)
        self.broadcaster.broadcast_portfolio_update(portfolio)

        return order

    def _update_position(
        self,
        portfolio: PaperTradingAccount,
        asset: Asset,
        quantity: Decimal,
        price: Decimal,
    ):
        position, created = portfolio.positions.get_or_create(
            asset=asset, defaults={"quantity": quantity, "avg_price": price}
        )

        if not created:
            total_cost = (position.quantity * position.avg_price) + (quantity * price)
            position.quantity = position.quantity + quantity
            position.avg_price = total_cost / position.quantity
            position.save()

        self.broadcaster.broadcast_position_update(position)

    def _recalculate_portfolio(self, portfolio: PaperTradingAccount):
        portfolio_value = self.calculate_portfolio_value(portfolio)
        portfolio.portfolio_value = portfolio_value

        if portfolio.starting_balance > 0:
            portfolio.total_return = float(
                (portfolio.cash_balance + portfolio_value - portfolio.starting_balance)
                / portfolio.starting_balance
                * 100
            )
        portfolio.save()

    @transaction.atomic
    def execute_limit_order(
        self,
        portfolio,
        asset_symbol: str,
        side: str,
        quantity: Decimal,
        limit_price: Decimal,
    ) -> PaperTradingOrder:
        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            order = PaperTradingOrder(
                portfolio=portfolio,
                asset_id=None,
                order_type="limit",
                side=side,
                quantity=quantity,
                price=limit_price,
            )
            order.reject(f"Asset {asset_symbol} not found")
            return order

        if side == "buy":
            required = quantity * limit_price
            if portfolio.cash_balance < required:
                order = PaperTradingOrder(
                    portfolio=portfolio,
                    asset=asset,
                    order_type="limit",
                    side=side,
                    quantity=quantity,
                    price=limit_price,
                )
                order.reject(f"Insufficient funds for limit order")
                self.broadcaster.broadcast_order_update(order)
                return order
        else:
            position = portfolio.positions.filter(asset=asset).first()
            if not position or position.quantity < quantity:
                order = PaperTradingOrder(
                    portfolio=portfolio,
                    asset=asset,
                    order_type="limit",
                    side=side,
                    quantity=quantity,
                    price=limit_price,
                )
                order.reject(f"Insufficient position for limit order")
                self.broadcaster.broadcast_order_update(order)
                return order

        order = PaperTradingOrder.objects.create(
            portfolio=portfolio,
            asset=asset,
            order_type="limit",
            side=side,
            quantity=quantity,
            price=limit_price,
            status="pending",
        )

        self.broadcaster.broadcast_order_update(order)
        return order

    def cancel_order(self, order_id: int, user_id: int) -> bool:
        try:
            order = PaperTradingOrder.objects.get(
                id=order_id, portfolio__user_id=user_id, status="pending"
            )
            order.cancel()
            self.broadcaster.broadcast_order_update(order)
            return True
        except PaperTradingOrder.DoesNotExist:
            return False

    def calculate_portfolio_value(self, portfolio: PaperTradingAccount) -> Decimal:
        total = portfolio.cash_balance

        for position in portfolio.positions.all():
            current_price = self.market_data.get_current_price(position.asset.symbol)
            if current_price:
                total += position.quantity * Decimal(str(current_price))

        return total

    def get_positions(self, portfolio: PaperTradingAccount) -> List[Dict]:
        positions = []
        for position in portfolio.positions.all():
            current_price = self.market_data.get_current_price(position.asset.symbol)
            if current_price:
                market_value = position.quantity * Decimal(str(current_price))
                cost_basis = position.quantity * position.avg_price
                pl = market_value - cost_basis
                pl_percent = (pl / cost_basis * 100) if cost_basis > 0 else Decimal("0")

                positions.append(
                    {
                        "id": str(position.id),
                        "symbol": position.asset.symbol,
                        "name": position.asset.name,
                        "quantity": float(position.quantity),
                        "avg_price": float(position.avg_price),
                        "current_price": float(current_price),
                        "market_value": float(market_value),
                        "pl": float(pl),
                        "pl_percent": float(pl_percent),
                    }
                )

        return positions

    def get_orders(
        self, portfolio: PaperTradingAccount, limit: int = 100
    ) -> List[Dict]:
        orders = portfolio.orders.all().select_related("asset")[:limit]
        return [
            {
                "id": str(order.id),
                "symbol": order.asset.symbol,
                "order_type": order.order_type,
                "side": order.side,
                "quantity": float(order.quantity),
                "price": float(order.price) if order.price else None,
                "stop_price": float(order.stop_price) if order.stop_price else None,
                "filled_price": float(order.filled_price)
                if order.filled_price
                else None,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            }
            for order in orders
        ]

    def check_limit_orders(self):
        pending_orders = PaperTradingOrder.objects.filter(
            status="pending", order_type="limit"
        ).select_related("portfolio", "asset", "portfolio__user")

        for order in pending_orders:
            current_price = self.market_data.get_current_price(order.asset.symbol)
            if current_price is None:
                continue

            current_price_decimal = Decimal(str(current_price))

            if order.side == "buy" and current_price_decimal <= order.price:
                self._execute_buy_order(order.portfolio, order, current_price_decimal)
            elif order.side == "sell" and current_price_decimal >= order.price:
                self._execute_sell_order(order.portfolio, order, current_price_decimal)

    def reset_portfolio(self, portfolio: PaperTradingAccount):
        portfolio.cash_balance = portfolio.starting_balance
        portfolio.last_reset_at = timezone.now()
        portfolio.reset_count += 1
        portfolio.total_trades = 0
        portfolio.winning_trades = 0
        portfolio.losing_trades = 0
        portfolio.total_return = 0.0
        portfolio.save()

        portfolio.positions.all().delete()
        portfolio.orders.all().delete()

        self.broadcaster.broadcast_portfolio_update(portfolio)
