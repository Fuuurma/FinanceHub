from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from investments.models.market_depth import (
    OrderBookLevel,
    OrderBookSnapshot,
    TimeAndSales,
    MarketDepthSummary,
    LargeOrders,
)


class MarketDepthService:
    def __init__(self):
        pass

    @transaction.atomic
    def update_order_book(
        self,
        asset_id: int,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]],
    ) -> Dict:
        """Update order book with new data"""
        now = timezone.now()

        OrderBookLevel.objects.filter(asset_id=asset_id).delete()

        bid_levels = [
            OrderBookLevel(
                asset_id=asset_id,
                side="bid",
                price=Decimal(str(price)),
                quantity=Decimal(str(quantity)),
            )
            for price, quantity in bids[:20]
        ]
        OrderBookLevel.objects.bulk_create(bid_levels)

        ask_levels = [
            OrderBookLevel(
                asset_id=asset_id,
                side="ask",
                price=Decimal(str(price)),
                quantity=Decimal(str(quantity)),
            )
            for price, quantity in asks[:20]
        ]
        OrderBookLevel.objects.bulk_create(ask_levels)

        snapshot = self._create_snapshot(asset_id, bids, asks)
        self._detect_large_orders(asset_id, bids, asks)
        self._update_depth_summary(asset_id)

        return {
            "snapshot_id": snapshot.id,
            "timestamp": snapshot.timestamp.isoformat() if snapshot.timestamp else None,
            "bid_ask_spread": float(snapshot.bid_ask_spread) if snapshot else None,
            "order_imbalance": float(snapshot.order_imbalance)
            if snapshot and snapshot.order_imbalance
            else None,
        }

    def _create_snapshot(
        self,
        asset_id: int,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]],
    ) -> OrderBookSnapshot:
        """Create order book snapshot with metrics"""

        total_bid_volume = sum(q for _, q in bids) if bids else Decimal("0")
        total_ask_volume = sum(q for _, q in asks) if asks else Decimal("0")

        best_bid = bids[0][0] if bids else 0
        best_ask = asks[0][0] if asks else 0
        spread = best_ask - best_bid if best_ask and best_bid else 0
        spread_pct = (spread / best_bid * 100) if best_bid > 0 else 0

        top_5_bid_vol = sum(q for _, q in bids[:5]) if bids else Decimal("0")
        top_5_ask_vol = sum(q for _, q in asks[:5]) if asks else Decimal("0")
        top_10_bid_vol = sum(q for _, q in bids[:10]) if bids else Decimal("0")
        top_10_ask_vol = sum(q for _, q in asks[:10]) if asks else Decimal("0")

        vwap_bid = None
        vwap_ask = None
        if float(top_10_bid_vol) > 0:
            vwap_bid = sum(p * q for p, q in bids[:10]) / float(top_10_bid_vol)
        if float(top_10_ask_vol) > 0:
            vwap_ask = sum(p * q for p, q in asks[:10]) / float(top_10_ask_vol)

        imbalance = None
        if float(total_bid_volume) > 0 and float(total_ask_volume) > 0:
            imbalance = (float(total_bid_volume) - float(total_ask_volume)) / (
                float(total_bid_volume) + float(total_ask_volume)
            )

        snapshot = OrderBookSnapshot.objects.create(
            asset_id=asset_id,
            bids=bids[:20],
            asks=asks[:20],
            total_bid_volume=Decimal(str(total_bid_volume)),
            total_ask_volume=Decimal(str(total_ask_volume)),
            bid_ask_spread=Decimal(str(spread)),
            bid_ask_spread_pct=Decimal(str(spread_pct)),
            top_5_bid_volume=Decimal(str(top_5_bid_vol)),
            top_5_ask_volume=Decimal(str(top_5_ask_vol)),
            top_10_bid_volume=Decimal(str(top_10_bid_vol)),
            top_10_ask_volume=Decimal(str(top_10_ask_vol)),
            vwap_bid=Decimal(str(vwap_bid)) if vwap_bid else None,
            vwap_ask=Decimal(str(vwap_ask)) if vwap_ask else None,
            order_imbalance=Decimal(str(imbalance)) if imbalance is not None else None,
        )

        return snapshot

    def _detect_large_orders(
        self,
        asset_id: int,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]],
    ):
        """Detect and log unusually large orders"""

        all_orders = [(p, q, "bid") for p, q in bids] + [(p, q, "ask") for p, q in asks]
        if not all_orders:
            return

        avg_size = sum(q for _, q, _ in all_orders) / len(all_orders)
        if avg_size == 0:
            return

        for price, quantity, side in all_orders:
            value = price * quantity
            if quantity > avg_size * 5 or value > 100000:
                LargeOrders.objects.create(
                    asset_id=asset_id,
                    side=side,
                    price=Decimal(str(price)),
                    quantity=Decimal(str(quantity)),
                    value_usd=Decimal(str(value)),
                    size_multiple=Decimal(str(quantity / avg_size)),
                )

    def _update_depth_summary(self, asset_id: int):
        """Update rolling market depth summary"""

        latest_snapshot = (
            OrderBookSnapshot.objects.filter(asset_id=asset_id)
            .order_by("-timestamp")
            .first()
        )

        if not latest_snapshot:
            return

        bids_data = latest_snapshot.bids if latest_snapshot.bids else []
        asks_data = latest_snapshot.asks if latest_snapshot.asks else []

        best_bid = bids_data[0][0] if bids_data else 0
        best_ask = asks_data[0][0] if asks_data else 0
        mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0

        if mid_price == 0:
            return

        depth_1pct_bid = sum(q for p, q in bids_data if p >= mid_price * 0.99)
        depth_1pct_ask = sum(q for p, q in asks_data if p <= mid_price * 1.01)
        depth_5pct_bid = sum(q for p, q in bids_data if p >= mid_price * 0.95)
        depth_5pct_ask = sum(q for p, q in asks_data if p <= mid_price * 1.05)
        depth_10pct_bid = sum(q for p, q in bids_data if p >= mid_price * 0.90)
        depth_10pct_ask = sum(q for p, q in asks_data if p <= mid_price * 1.10)

        five_min_ago = timezone.now() - timedelta(minutes=5)
        fifteen_min_ago = timezone.now() - timedelta(minutes=15)

        buy_vol_5m = TimeAndSales.objects.filter(
            asset_id=asset_id,
            timestamp__gte=five_min_ago,
            trade_type="buy",
        ).aggregate(total=Sum("quantity"))["total"] or Decimal("0")

        sell_vol_5m = TimeAndSales.objects.filter(
            asset_id=asset_id,
            timestamp__gte=five_min_ago,
            trade_type="sell",
        ).aggregate(total=Sum("quantity"))["total"] or Decimal("0")

        buy_vol_15m = TimeAndSales.objects.filter(
            asset_id=asset_id,
            timestamp__gte=fifteen_min_ago,
            trade_type="buy",
        ).aggregate(total=Sum("quantity"))["total"] or Decimal("0")

        sell_vol_15m = TimeAndSales.objects.filter(
            asset_id=asset_id,
            timestamp__gte=fifteen_min_ago,
            trade_type="sell",
        ).aggregate(total=Sum("quantity"))["total"] or Decimal("0")

        total_volume = float(buy_vol_5m) + float(sell_vol_5m)
        price_impact = None
        if total_volume > 0:
            imbalance = float(latest_snapshot.order_imbalance or 0)
            price_change_pct = abs(imbalance) * 10
            price_impact = (
                price_change_pct / (total_volume / 1000) if total_volume > 0 else None
            )

        MarketDepthSummary.objects.update_or_create(
            asset_id=asset_id,
            defaults={
                "best_bid": Decimal(str(best_bid)) if best_bid else Decimal("0"),
                "best_ask": Decimal(str(best_ask)) if best_ask else Decimal("0"),
                "current_spread": latest_snapshot.bid_ask_spread,
                "depth_within_1pct": Decimal(str(depth_1pct_bid + depth_1pct_ask)),
                "depth_within_5pct": Decimal(str(depth_5pct_bid + depth_5pct_ask)),
                "depth_within_10pct": Decimal(str(depth_10pct_bid + depth_10pct_ask)),
                "buy_volume_5min": buy_vol_5m,
                "sell_volume_5min": sell_vol_5m,
                "buy_volume_15min": buy_vol_15m,
                "sell_volume_15min": sell_vol_15m,
                "price_impact_per_1k": Decimal(str(price_impact))
                if price_impact
                else None,
            },
        )

    def get_order_book(self, asset_id: int, depth: int = 20) -> Dict:
        """Get current order book for asset"""

        snapshot = (
            OrderBookSnapshot.objects.filter(asset_id=asset_id)
            .order_by("-timestamp")
            .first()
        )

        if not snapshot:
            return {"bids": [], "asks": [], "metrics": {}}

        bids = [
            {
                "price": float(p),
                "quantity": float(q),
                "total": float(p * q),
            }
            for p, q in snapshot.bids[:depth]
        ]

        asks = [
            {
                "price": float(p),
                "quantity": float(q),
                "total": float(p * q),
            }
            for p, q in snapshot.asks[:depth]
        ]

        metrics = {
            "spread": float(snapshot.bid_ask_spread)
            if snapshot.bid_ask_spread
            else None,
            "spread_pct": float(snapshot.bid_ask_spread_pct)
            if snapshot.bid_ask_spread_pct
            else None,
            "total_bid_volume": float(snapshot.total_bid_volume),
            "total_ask_volume": float(snapshot.total_ask_volume),
            "top_5_bid_volume": float(snapshot.top_5_bid_volume),
            "top_5_ask_volume": float(snapshot.top_5_ask_volume),
            "vwap_bid": float(snapshot.vwap_bid) if snapshot.vwap_bid else None,
            "vwap_ask": float(snapshot.vwap_ask) if snapshot.vwap_ask else None,
            "order_imbalance": float(snapshot.order_imbalance)
            if snapshot.order_imbalance
            else None,
            "timestamp": snapshot.timestamp.isoformat() if snapshot.timestamp else None,
        }

        return {"bids": bids, "asks": asks, "metrics": metrics}

    def get_time_and_sales(self, asset_id: int, limit: int = 100) -> List[Dict]:
        """Get recent trades"""

        trades = TimeAndSales.objects.filter(asset_id=asset_id).order_by("-timestamp")[
            :limit
        ]

        return [
            {
                "price": float(t.price),
                "quantity": float(t.quantity),
                "trade_type": t.trade_type,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "trade_id": t.trade_id,
            }
            for t in trades
        ]

    def get_depth_summary(self, asset_id: int) -> Optional[Dict]:
        """Get market depth summary"""

        try:
            summary = MarketDepthSummary.objects.get(asset_id=asset_id)
        except MarketDepthSummary.DoesNotExist:
            return None

        return {
            "best_bid": float(summary.best_bid) if summary.best_bid else None,
            "best_ask": float(summary.best_ask) if summary.best_ask else None,
            "spread": float(summary.current_spread) if summary.current_spread else None,
            "depth_within_1pct": float(summary.depth_within_1pct)
            if summary.depth_within_1pct
            else None,
            "depth_within_5pct": float(summary.depth_within_5pct)
            if summary.depth_within_5pct
            else None,
            "depth_within_10pct": float(summary.depth_within_10pct)
            if summary.depth_within_10pct
            else None,
            "buy_volume_5min": float(summary.buy_volume_5min)
            if summary.buy_volume_5min
            else None,
            "sell_volume_5min": float(summary.sell_volume_5min)
            if summary.sell_volume_5min
            else None,
            "buy_volume_15min": float(summary.buy_volume_15min)
            if summary.buy_volume_15min
            else None,
            "sell_volume_15min": float(summary.sell_volume_15min)
            if summary.sell_volume_15min
            else None,
            "price_impact_per_1k": float(summary.price_impact_per_1k)
            if summary.price_impact_per_1k
            else None,
            "updated_at": summary.updated_at.isoformat()
            if summary.updated_at
            else None,
        }

    def get_large_orders(
        self,
        asset_id: int,
        min_value: Optional[float] = None,
        hours: int = 24,
    ) -> List[Dict]:
        """Get recent large orders (whale activity)"""

        since = timezone.now() - timedelta(hours=hours)

        queryset = LargeOrders.objects.filter(
            asset_id=asset_id,
            timestamp__gte=since,
        )

        if min_value:
            queryset = queryset.filter(value_usd__gte=min_value)

        large_orders = queryset.order_by("-timestamp")[:50]

        return [
            {
                "side": o.side,
                "price": float(o.price) if o.price else None,
                "quantity": float(o.quantity) if o.quantity else None,
                "value_usd": float(o.value_usd) if o.value_usd else None,
                "size_multiple": float(o.size_multiple) if o.size_multiple else None,
                "timestamp": o.timestamp.isoformat() if o.timestamp else None,
            }
            for o in large_orders
        ]

    @transaction.atomic
    def record_trade(
        self,
        asset_id: int,
        price: float,
        quantity: float,
        trade_type: str = "unknown",
        trade_id: str = None,
    ):
        """Record a trade (tick-by-tick data)"""

        TimeAndSales.objects.create(
            asset_id=asset_id,
            price=Decimal(str(price)),
            quantity=Decimal(str(quantity)),
            trade_type=trade_type,
            trade_id=trade_id or "",
        )

    def get_order_flow_heatmap(self, asset_id: int, hours: int = 1) -> Dict:
        """Get order flow heatmap data"""

        since = timezone.now() - timedelta(hours=hours)

        trades = TimeAndSales.objects.filter(
            asset_id=asset_id,
            timestamp__gte=since,
        )

        price_levels = {}
        for trade in trades:
            price_key = float(trade.price)
            if price_key not in price_levels:
                price_levels[price_key] = {"buy_volume": 0, "sell_volume": 0}

            if trade.trade_type == "buy":
                price_levels[price_key]["buy_volume"] += float(trade.quantity)
            elif trade.trade_type == "sell":
                price_levels[price_key]["sell_volume"] += float(trade.quantity)

        heatmap_data = [
            {
                "price": price,
                "buy_volume": data["buy_volume"],
                "sell_volume": data["sell_volume"],
                "net_volume": data["buy_volume"] - data["sell_volume"],
            }
            for price, data in sorted(price_levels.items())
        ]

        return {"data": heatmap_data, "period_hours": hours}
