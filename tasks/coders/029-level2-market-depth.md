# C-029: Level 2 Market Depth (Order Book) Data

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 12-16 hours  
**Dependencies:** C-005 (Backend Improvements), C-006 (Data Pipeline)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement Level 2 market depth (order book) data feed with real-time bid/ask orders, price aggregation, volume analysis, and market sentiment indicators for professional traders.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 2.1 - Live Pricing):**

- Level 2 market depth (order book)
- Real-time quotes (delayed option for free tier)
- Tick-by-tick data for pro users
- Bid/ask spreads
- Volume & turnover

---

## ✅ CURRENT STATE

**What exists:**
- Basic price data (bid/ask spreads)
- Real-time pricing for top-of-book
- Asset tracking

**What's missing:**
- Full order book depth (multiple price levels)
- Order flow analytics
- Market depth visualization data
- Time & sales data
- Aggregated order book data

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (2-3 hours)

**Create `apps/backend/src/investments/models/market_depth.py`:**

```python
from django.db import models
from .asset import Asset

class OrderBookLevel(models.Model):
    """Individual price levels in order book"""
    
    SIDE_CHOICES = [
        ('bid', 'Bid'),
        ('ask', 'Ask'),
    ]
    
    # Asset reference
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='order_book_levels')
    
    # Order details
    side = models.CharField(max_length=3, choices=SIDE_CHOICES)
    price = models.DecimalField(max_digits=20, decimal_places=6)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)  # Number of shares/coins
    orders_count = models.IntegerField(default=1)  # Number of orders at this level
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['asset', 'side', '-price']),
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
        unique_together = [['asset', 'side', 'price', 'timestamp']]

class OrderBookSnapshot(models.Model):
    """Aggregated order book snapshot at point in time"""
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='order_book_snapshots')
    
    # Full order book data (JSON arrays of price levels)
    bids = models.JSONField(default=list)  # [[price, quantity], ...]
    asks = models.JSONField(default=list)  # [[price, quantity], ...]
    
    # Aggregated metrics
    total_bid_volume = models.DecimalField(max_digits=30, decimal_places=8)
    total_ask_volume = models.DecimalField(max_digits=30, decimal_places=8)
    bid_ask_spread = models.DecimalField(max_digits=20, decimal_places=6)
    bid_ask_spread_pct = models.DecimalField(max_digits=10, decimal_places=6)
    
    # Market depth metrics (sum of volume at best N levels)
    top_5_bid_volume = models.DecimalField(max_digits=30, decimal_places=8)
    top_5_ask_volume = models.DecimalField(max_digits=30, decimal_places=8)
    top_10_bid_volume = models.DecimalField(max_digits=30, decimal_places=8)
    top_10_ask_volume = models.DecimalField(max_digits=30, decimal_places=8)
    
    # Weighted average price
    vwap_bid = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    vwap_ask = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    
    # Order imbalance (buy vs sell pressure)
    order_imbalance = models.DecimalField(max_digits=10, decimal_places=4, null=True)  # -1 to +1
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

class TimeAndSales(models.Model):
    """Tick-by-tick trade data"""
    
    TRADE_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('unknown', 'Unknown'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='time_and_sales')
    
    # Trade details
    price = models.DecimalField(max_digits=20, decimal_places=6)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPE_CHOICES, default='unknown')
    
    # Timestamp
    timestamp = models.DateTimeField(db_index=True)
    
    # Trade ID (from exchange)
    trade_id = models.CharField(max_length=100, blank=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['trade_id']),
        ]
        ordering = ['-timestamp']

class MarketDepthSummary(models.Model):
    """Rolling summary of market depth (calculated periodically)"""
    
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='depth_summary')
    
    # Current depth
    best_bid = models.DecimalField(max_digits=20, decimal_places=6)
    best_ask = models.DecimalField(max_digits=20, decimal_places=6)
    current_spread = models.DecimalField(max_digits=20, decimal_places=6)
    
    # Depth strength (sum of volume within X% of mid price)
    depth_within_1pct = models.DecimalField(max_digits=30, decimal_places=8)  # Volume within 1%
    depth_within_5pct = models.DecimalField(max_digits=30, decimal_places=8)  # Volume within 5%
    depth_within_10pct = models.DecimalField(max_digits=30, decimal_places=8)  # Volume within 10%
    
    # Order flow metrics (last N minutes)
    buy_volume_5min = models.DecimalField(max_digits=30, decimal_places=8)
    sell_volume_5min = models.DecimalField(max_digits=30, decimal_places=8)
    buy_volume_15min = models.DecimalField(max_digits=30, decimal_places=8)
    sell_volume_15min = models.DecimalField(max_digits=30, decimal_places=8)
    
    # Price impact (how much price moves per unit of volume)
    price_impact_per_1k = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['asset']),
        ]

class LargeOrders(models.Model):
    """Track unusually large orders (whale activity)"""
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='large_orders')
    
    # Order details
    side = models.CharField(max_length=3)  # bid/ask
    price = models.DecimalField(max_digits=20, decimal_places=6)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    value_usd = models.DecimalField(max_digits=30, decimal_places=2)  # Notional value
    
    # Size classification
    size_multiple = models.DecimalField(max_digits=10, decimal_places=2)  # How many times avg order size
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['-value_usd']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
```

---

### **Phase 2: Market Depth Service** (5-6 hours)

**Create `apps/backend/src/investments/services/market_depth_service.py`:**

```python
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Sum, Avg, Count, F, Window
from django.db.models.functions import DenseRank
from django.utils import timezone
from investments.models.market_depth import (
    OrderBookLevel, OrderBookSnapshot, TimeAndSales,
    MarketDepthSummary, LargeOrders
)
from investments.models.asset import Asset
from investments.services.price_service import PriceService

class MarketDepthService:
    
    def __init__(self):
        self.price_service = PriceService()
    
    @transaction.atomic
    def update_order_book(
        self,
        asset_id: int,
        bids: List[Tuple[float, float]],  # [(price, quantity), ...]
        asks: List[Tuple[float, float]]
    ) -> Dict:
        """
        Update order book with new data
        
        Returns: Summary metrics
        """
        asset = Asset.objects.get(id=asset_id)
        now = timezone.now()
        
        # Delete old order book levels for this asset
        OrderBookLevel.objects.filter(asset=asset).delete()
        
        # Insert new bid levels
        bid_levels = [
            OrderBookLevel(
                asset=asset,
                side='bid',
                price=Decimal(str(price)),
                quantity=Decimal(str(quantity))
            )
            for price, quantity in bids[:20]  # Top 20 levels
        ]
        OrderBookLevel.objects.bulk_create(bid_levels)
        
        # Insert new ask levels
        ask_levels = [
            OrderBookLevel(
                asset=asset,
                side='ask',
                price=Decimal(str(price)),
                quantity=Decimal(str(quantity))
            )
            for price, quantity in asks[:20]  # Top 20 levels
        ]
        OrderBookLevel.objects.bulk_create(ask_levels)
        
        # Create snapshot
        snapshot = self._create_snapshot(asset, bids, asks)
        
        # Check for large orders
        self._detect_large_orders(asset, bids, asks)
        
        # Update summary
        self._update_depth_summary(asset)
        
        return {
            'snapshot_id': snapshot.id,
            'timestamp': snapshot.timestamp,
            'bid_ask_spread': float(snapshot.bid_ask_spread),
            'order_imbalance': float(snapshot.order_imbalance) if snapshot.order_imbalance else None,
        }
    
    def _create_snapshot(
        self,
        asset: Asset,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]]
    ) -> OrderBookSnapshot:
        """Create order book snapshot with metrics"""
        
        # Calculate metrics
        total_bid_volume = sum(q for _, q in bids)
        total_ask_volume = sum(q for _, q in asks)
        
        best_bid = bids[0][0] if bids else 0
        best_ask = asks[0][0] if asks else 0
        spread = best_ask - best_bid if best_ask and best_bid else 0
        spread_pct = (spread / best_bid * 100) if best_bid > 0 else 0
        
        # Top N levels volume
        top_5_bid_vol = sum(q for _, q in bids[:5])
        top_5_ask_vol = sum(q for _, q in asks[:5])
        top_10_bid_vol = sum(q for _, q in bids[:10])
        top_10_ask_vol = sum(q for _, q in asks[:10])
        
        # VWAP
        vwap_bid = sum(p * q for p, q in bids[:10]) / top_10_bid_vol if top_10_bid_vol > 0 else None
        vwap_ask = sum(p * q for p, q in asks[:10]) / top_10_ask_vol if top_10_ask_vol > 0 else None
        
        # Order imbalance (-1 to +1)
        imbalance = None
        if total_bid_volume > 0 and total_ask_volume > 0:
            imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
        
        snapshot = OrderBookSnapshot.objects.create(
            asset=asset,
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
        asset: Asset,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]]
    ):
        """Detect and log unusually large orders"""
        
        # Calculate average order size
        all_orders = [(p, q, 'bid') for p, q in bids] + [(p, q, 'ask') for p, q in asks]
        if not all_orders:
            return
        
        avg_size = sum(q for _, q, _ in all_orders) / len(all_orders)
        
        # Current price
        current_price = asset.current_price
        
        for price, quantity, side in all_orders:
            # Calculate notional value
            value = price * quantity
            
            # Check if order is large (>5x average or >$100K)
            if quantity > avg_size * 5 or value > 100000:
                LargeOrders.objects.create(
                    asset=asset,
                    side=side,
                    price=Decimal(str(price)),
                    quantity=Decimal(str(quantity)),
                    value_usd=Decimal(str(value)),
                    size_multiple=Decimal(str(quantity / avg_size))
                )
    
    def _update_depth_summary(self, asset: Asset):
        """Update rolling market depth summary"""
        
        # Get latest snapshot
        latest_snapshot = OrderBookSnapshot.objects.filter(
            asset=asset
        ).order_by('-timestamp').first()
        
        if not latest_snapshot:
            return
        
        # Get current price
        mid_price = (float(latest_snapshot.bids[0][0]) + float(latest_snapshot.asks[0][0])) / 2
        
        # Calculate depth within percentages
        depth_1pct_bid = sum(q for p, q in latest_snapshot.bids if p >= mid_price * 0.99)
        depth_1pct_ask = sum(q for p, q in latest_snapshot.asks if p <= mid_price * 1.01)
        
        depth_5pct_bid = sum(q for p, q in latest_snapshot.bids if p >= mid_price * 0.95)
        depth_5pct_ask = sum(q for p, q in latest_snapshot.asks if p <= mid_price * 1.05)
        
        depth_10pct_bid = sum(q for p, q in latest_snapshot.bids if p >= mid_price * 0.90)
        depth_10pct_ask = sum(q for p, q in latest_snapshot.asks if p <= mid_price * 1.10)
        
        # Get trade volume in last 5/15 minutes
        five_min_ago = timezone.now() - timedelta(minutes=5)
        fifteen_min_ago = timezone.now() - timedelta(minutes=15)
        
        buy_vol_5m = TimeAndSales.objects.filter(
            asset=asset,
            timestamp__gte=five_min_ago,
            trade_type='buy'
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        sell_vol_5m = TimeAndSales.objects.filter(
            asset=asset,
            timestamp__gte=five_min_ago,
            trade_type='sell'
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        buy_vol_15m = TimeAndSales.objects.filter(
            asset=asset,
            timestamp__gte=fifteen_min_ago,
            trade_type='buy'
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        sell_vol_15m = TimeAndSales.objects.filter(
            asset=asset,
            timestamp__gte=fifteen_min_ago,
            trade_type='sell'
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        # Calculate price impact (per $1000 traded)
        # This is a simplified calculation
        total_volume = buy_vol_5m + sell_vol_5m
        price_impact = None
        if total_volume > 0:
            price_change_pct = abs(float(latest_snapshot.order_imbalance or 0)) * 10  # Rough estimate
            price_impact = price_change_pct / (float(total_volume) / 1000) if total_volume > 0 else None
        
        # Update or create summary
        summary, created = MarketDepthSummary.objects.update_or_create(
            asset=asset,
            defaults={
                'best_bid': Decimal(str(latest_snapshot.bids[0][0])) if latest_snapshot.bids else None,
                'best_ask': Decimal(str(latest_snapshot.asks[0][0])) if latest_snapshot.asks else None,
                'current_spread': latest_snapshot.bid_ask_spread,
                'depth_within_1pct': Decimal(str(depth_1pct_bid + depth_1pct_ask)),
                'depth_within_5pct': Decimal(str(depth_5pct_bid + depth_5pct_ask)),
                'depth_within_10pct': Decimal(str(depth_10pct_bid + depth_10pct_ask)),
                'buy_volume_5min': buy_vol_5m,
                'sell_volume_5min': sell_vol_5m,
                'buy_volume_15min': buy_vol_15m,
                'sell_volume_15min': sell_vol_15m,
                'price_impact_per_1k': Decimal(str(price_impact)) if price_impact else None,
            }
        )
        
        return summary
    
    def get_order_book(
        self,
        asset_id: int,
        depth: int = 20
    ) -> Dict:
        """
        Get current order book for asset
        
        Returns: {bids, asks, metrics}
        """
        asset = Asset.objects.get(id=asset_id)
        
        # Get latest snapshot
        snapshot = OrderBookSnapshot.objects.filter(
            asset=asset
        ).order_by('-timestamp').first()
        
        if not snapshot:
            return {
                'bids': [],
                'asks': [],
                'metrics': {}
            }
        
        # Format bids and asks
        bids = [
            {
                'price': float(p),
                'quantity': float(q),
                'total': float(p * q)
            }
            for p, q in snapshot.bids[:depth]
        ]
        
        asks = [
            {
                'price': float(p),
                'quantity': float(q),
                'total': float(p * q)
            }
            for p, q in snapshot.asks[:depth]
        ]
        
        # Metrics
        metrics = {
            'spread': float(snapshot.bid_ask_spread),
            'spread_pct': float(snapshot.bid_ask_spread_pct),
            'total_bid_volume': float(snapshot.total_bid_volume),
            'total_ask_volume': float(snapshot.total_ask_volume),
            'top_5_bid_volume': float(snapshot.top_5_bid_volume),
            'top_5_ask_volume': float(snapshot.top_5_ask_volume),
            'vwap_bid': float(snapshot.vwap_bid) if snapshot.vwap_bid else None,
            'vwap_ask': float(snapshot.vwap_ask) if snapshot.vwap_ask else None,
            'order_imbalance': float(snapshot.order_imbalance) if snapshot.order_imbalance else None,
            'timestamp': snapshot.timestamp.isoformat(),
        }
        
        return {
            'bids': bids,
            'asks': asks,
            'metrics': metrics
        }
    
    def get_time_and_sales(
        self,
        asset_id: int,
        limit: int = 100
    ) -> List[Dict]:
        """Get recent trades"""
        trades = TimeAndSales.objects.filter(
            asset_id=asset_id
        ).order_by('-timestamp')[:limit]
        
        return [
            {
                'price': float(t.price),
                'quantity': float(t.quantity),
                'trade_type': t.trade_type,
                'timestamp': t.timestamp.isoformat(),
                'trade_id': t.trade_id
            }
            for t in trades
        ]
    
    def get_depth_summary(self, asset_id: int) -> Dict:
        """Get market depth summary"""
        try:
            summary = MarketDepthSummary.objects.get(asset_id=asset_id)
        except MarketDepthSummary.DoesNotExist:
            return None
        
        return {
            'best_bid': float(summary.best_bid),
            'best_ask': float(summary.best_ask),
            'spread': float(summary.current_spread),
            'depth_within_1pct': float(summary.depth_within_1pct),
            'depth_within_5pct': float(summary.depth_within_5pct),
            'depth_within_10pct': float(summary.depth_within_10pct),
            'buy_volume_5min': float(summary.buy_volume_5min),
            'sell_volume_5min': float(summary.sell_volume_5min),
            'buy_volume_15min': float(summary.buy_volume_15min),
            'sell_volume_15min': float(summary.sell_volume_15min),
            'price_impact_per_1k': float(summary.price_impact_per_1k) if summary.price_impact_per_1k else None,
            'updated_at': summary.updated_at.isoformat(),
        }
    
    def get_large_orders(
        self,
        asset_id: int,
        min_value: Optional[float] = None,
        hours: int = 24
    ) -> List[Dict]:
        """Get recent large orders (whale activity)"""
        since = timezone.now() - timedelta(hours=hours)
        
        queryset = LargeOrders.objects.filter(
            asset_id=asset_id,
            timestamp__gte=since
        )
        
        if min_value:
            queryset = queryset.filter(value_usd__gte=min_value)
        
        large_orders = queryset.order_by('-timestamp')[:50]
        
        return [
            {
                'side': o.side,
                'price': float(o.price),
                'quantity': float(o.quantity),
                'value_usd': float(o.value_usd),
                'size_multiple': float(o.size_multiple),
                'timestamp': o.timestamp.isoformat(),
            }
            for o in large_orders
        ]
    
    @transaction.atomic
    def record_trade(
        self,
        asset_id: int,
        price: float,
        quantity: float,
        trade_type: str = 'unknown',
        trade_id: str = None
    ):
        """Record a trade (tick-by-tick data)"""
        TimeAndSales.objects.create(
            asset_id=asset_id,
            price=Decimal(str(price)),
            quantity=Decimal(str(quantity)),
            trade_type=trade_type,
            trade_id=trade_id or ''
        )
    
    def get_order_flow_heatmap(
        self,
        asset_id: int,
        hours: int = 1
    ) -> Dict:
        """
        Get order flow heatmap data
        Shows buy/sell pressure at different price levels
        """
        since = timezone.now() - timedelta(hours=hours)
        
        # Get trades in period
        trades = TimeAndSales.objects.filter(
            asset_id=asset_id,
            timestamp__gte=since
        )
        
        # Calculate volume at each price level
        price_levels = {}
        for trade in trades:
            price_key = float(trade.price)
            if price_key not in price_levels:
                price_levels[price_key] = {'buy_volume': 0, 'sell_volume': 0}
            
            if trade.trade_type == 'buy':
                price_levels[price_key]['buy_volume'] += float(trade.quantity)
            elif trade.trade_type == 'sell':
                price_levels[price_key]['sell_volume'] += float(trade.quantity)
        
        # Format for heatmap
        heatmap_data = [
            {
                'price': price,
                'buy_volume': data['buy_volume'],
                'sell_volume': data['sell_volume'],
                'net_volume': data['buy_volume'] - data['sell_volume']
            }
            for price, data in sorted(price_levels.items())
        ]
        
        return {
            'data': heatmap_data,
            'period_hours': hours
        }
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/market_depth.py`:**

```python
from ninja import Router, Schema
from investments.services.market_depth_service import MarketDepthService

router = Router(tags=['market_depth'])
depth_service = MarketDepthService()

@router.get("/market-depth/{asset_id}/order-book")
def get_order_book(request, asset_id: int, depth: int = 20):
    """Get current order book (Level 2 data)"""
    return depth_service.get_order_book(asset_id, depth=depth)

@router.get("/market-depth/{asset_id}/time-sales")
def get_time_and_sales(request, asset_id: int, limit: int = 100):
    """Get recent trades (tick-by-tick)"""
    return depth_service.get_time_and_sales(asset_id, limit=limit)

@router.get("/market-depth/{asset_id}/summary")
def get_depth_summary(request, asset_id: int):
    """Get market depth summary"""
    return depth_service.get_depth_summary(asset_id)

@router.get("/market-depth/{asset_id}/large-orders")
def get_large_orders(
    request,
    asset_id: int,
    min_value: float = None,
    hours: int = 24
):
    """Get large orders (whale activity)"""
    return depth_service.get_large_orders(asset_id, min_value=min_value, hours=hours)

@router.get("/market-depth/{asset_id}/order-flow-heatmap")
def get_order_flow_heatmap(request, asset_id: int, hours: int = 1):
    """Get order flow heatmap"""
    return depth_service.get_order_flow_heatmap(asset_id, hours=hours)
```

---

### **Phase 4: Data Pipeline Integration** (2-3 hours)

**Create Dramatiq tasks for updating market depth:**

```python
# apps/backend/src/investments/tasks/market_depth_tasks.py
import dramatiq
from investments.services.market_depth_service import MarketDepthService

@dramatiq.actor
def update_order_book(asset_id: int, bids: list, asks: list):
    """Update order book from exchange data"""
    service = MarketDepthService()
    service.update_order_book(asset_id, bids, asks)

@dramatiq.actor
def record_trade(asset_id: int, price: float, quantity: float, trade_type: str, trade_id: str):
    """Record individual trade"""
    service = MarketDepthService()
    service.record_trade(asset_id, price, quantity, trade_type, trade_id)
```

---

## 📋 DELIVERABLES

- [ ] OrderBookLevel, OrderBookSnapshot, TimeAndSales models
- [ ] MarketDepthSummary, LargeOrders models
- [ ] MarketDepthService with 10 methods
- [ ] 5 API endpoints for market depth data
- [ ] Large order detection
- [ ] Order flow heatmap
- [ ] Time & sales tracking
- [ ] Database migrations
- [ ] Unit tests

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Order book displays top 20 bid/ask levels
- [ ] Real-time updates via WebSocket
- [ ] Large order detection working (>5x average or >$100K)
- [ ] Time & sales data captured
- [ ] Order flow heatmap generated
- [ ] Depth summary calculated accurately
- [ ] API response time <500ms
- [ ] Support for 100+ assets concurrently
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Order book update latency <1 second
- Support for 1000+ order updates per second
- Large order detection accuracy >95%
- Depth summary calculation <2 seconds
- Time & sales data retention for 30+ days

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/029-level2-market-depth.md
