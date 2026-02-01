# 📋 Task Assignment: C-036 Paper Trading System (Backend)

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** Linus (Backend Coder)
**Priority:** HIGH - Phase 1 Core Feature
**Estimated Effort:** 8-10 hours backend
**Timeline:** Start immediately, quality-driven (no deadline)

---

## 🎯 OVERVIEW

You are assigned to **C-036: Paper Trading System** - backend development (lead).

**Collaborators:**
- **Turing (Frontend Coder):** Building trading interface, consuming your API
- **GRACE (QA):** Creating test cases, validating functionality
- **Charo (Security):** Security audit, exploit prevention
- **MIES (UI/UX):** Design mockups for paper trading interface
- **HADI (Accessibility):** WCAG 2.1 Level AA compliance

**Your Role:** Lead backend development for paper trading system. Turing is waiting on your API.

---

## 📋 YOUR TASKS

### Task 1: Virtual Portfolio Model (2h)
**File:** `apps/backend/src/trading/models/paper_portfolio.py`

**Requirements:**
```python
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal

class PaperTradingPortfolio(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paper_portfolio'
    )
    virtual_cash = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('100000.00')
    )
    initial_cash = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('100000.00')
    )
    portfolio_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('100000.00')
    )
    total_return = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'paper_trading_portfolios'
        verbose_name = 'Paper Trading Portfolio'
        verbose_name_plural = 'Paper Trading Portfolios'

    def __str__(self):
        return f"Paper Portfolio - {self.user.username}"

    def calculate_portfolio_value(self):
        """Calculate total portfolio value (cash + positions)"""
        from .services.paper_trading_engine import PaperTradingEngine
        engine = PaperTradingEngine()
        self.portfolio_value = engine.calculate_portfolio_value(self)
        self.save()
        return self.portfolio_value

    def calculate_return(self):
        """Calculate total return percentage"""
        if self.initial_cash > 0:
            self.total_return = (self.portfolio_value - self.initial_cash) / self.initial_cash
            self.save()
        return self.total_return

    def reset_portfolio(self):
        """Reset portfolio to initial state"""
        self.virtual_cash = self.initial_cash
        self.portfolio_value = self.initial_cash
        self.total_return = Decimal('0.0000')
        self.save()

        # Delete all positions and orders
        self.positions.all().delete()
        self.orders.all().delete()
```

**Tasks:**
- [ ] Create `PaperTradingPortfolio` model
- [ ] Add fields: user, virtual_cash, initial_cash, portfolio_value, total_return
- [ ] Add methods: `calculate_portfolio_value()`, `calculate_return()`, `reset_portfolio()`
- [ ] Add string representation
- [ ] Add Meta class configuration
- [ ] Create database migration
- [ ] Run migration

---

### Task 2: Virtual Order Model (2h)
**File:** `apps/backend/src/trading/models/paper_order.py`

**Requirements:**
```python
class PaperTradingOrder(models.Model):
    ORDER_TYPES = [
        ('market', 'Market Order'),
        ('limit', 'Limit Order'),
        ('stop', 'Stop Order'),
    ]

    SIDES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('filled', 'Filled'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]

    portfolio = models.ForeignKey(
        PaperTradingPortfolio,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.PROTECT
    )
    order_type = models.CharField(
        max_length=10,
        choices=ORDER_TYPES
    )
    side = models.CharField(
        max_length=4,
        choices=SIDES
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=4
    )
    price = models.DecimalField(  # Limit price or stop price
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    filled_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    filled_at = models.DateTimeField(
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    rejection_reason = models.TextField(
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'paper_trading_orders'
        verbose_name = 'Paper Trading Order'
        verbose_name_plural = 'Paper Trading Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['portfolio', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['asset', '-created_at']),
        ]

    def __str__(self):
        return f"{self.side.upper()} {self.quantity} {self.asset.symbol} @ {self.price or 'MARKET'}"

    def clean(self):
        """Validate order before saving"""
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")

        if self.order_type in ['limit', 'stop'] and not self.price:
            raise ValidationError(f"{self.order_type.capitalize()} orders require a price")

        if self.side == 'buy' and self.order_type == 'limit':
            # Check sufficient funds
            required = self.quantity * self.price
            if self.portfolio.virtual_cash < required:
                raise ValidationError(f"Insufficient funds. Required: ${required}, Available: ${self.portfolio.virtual_cash}")
```

**Tasks:**
- [ ] Create `PaperTradingOrder` model
- [ ] Add fields: portfolio, asset, order_type, side, quantity, price, status
- [ ] add fields: filled_price, filled_at, rejection_reason
- [ ] Add validation in `clean()` method
- [ ] Add indexes for fast queries
- [ ] Create database migration
- [ ] Run migration

---

### Task 3: Paper Trading Engine (3h)
**File:** `apps/backend/src/trading/services/paper_trading_engine.py`

**Requirements:**
```python
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
from ..models import PaperTradingPortfolio, PaperTradingOrder
from assets.models import Asset
from assets.services.market_data_service import MarketDataService

class PaperTradingEngine:
    def __init__(self):
        self.market_data = MarketDataService()

    @transaction.atomic
    def execute_market_order(self, portfolio, asset_symbol, side, quantity):
        """
        Execute market order instantly at current price
        
        Args:
            portfolio: PaperTradingPortfolio instance
            asset_symbol: str (e.g., "AAPL")
            side: str ("buy" or "sell")
            quantity: Decimal (number of shares)
            
        Returns:
            PaperTradingOrder instance (filled)
        """
        try:
            # Get asset
            asset = Asset.objects.get(symbol=asset_symbol.upper())
            
            # Get current price from market data
            current_price = self.market_data.get_current_price(asset_symbol)
            
            # Create order
            order = PaperTradingOrder.objects.create(
                portfolio=portfolio,
                asset=asset,
                order_type='market',
                side=side,
                quantity=Decimal(str(quantity))
            )
            
            # Validate and execute
            if side == 'buy':
                return self._execute_buy_order(portfolio, order, current_price)
            else:
                return self._execute_sell_order(portfolio, order, current_price)
                
        except Asset.DoesNotExist:
            order.status = 'rejected'
            order.rejection_reason = f"Asset {asset_symbol} not found"
            order.save()
            return order
        except Exception as e:
            order.status = 'rejected'
            order.rejection_reason = str(e)
            order.save()
            return order

    def _execute_buy_order(self, portfolio, order, current_price):
        """Execute buy order"""
        # Check sufficient funds
        required = order.quantity * current_price
        if portfolio.virtual_cash < required:
            order.status = 'rejected'
            order.rejection_reason = f"Insufficient funds. Required: ${required}, Available: ${portfolio.virtual_cash}"
            order.save()
            return order

        # Execute order
        portfolio.virtual_cash -= required
        portfolio.save()

        order.filled_price = current_price
        order.filled_at = timezone.now()
        order.status = 'filled'
        order.save()

        # Create or update position
        self._update_position(portfolio, order.asset, order.quantity, current_price)

        # Recalculate portfolio value
        portfolio.calculate_portfolio_value()
        portfolio.calculate_return()

        return order

    def _execute_sell_order(self, portfolio, order, current_price):
        """Execute sell order"""
        # Check sufficient position
        position = portfolio.positions.filter(asset=order.asset).first()
        if not position or position.quantity < order.quantity:
            order.status = 'rejected'
            order.rejection_reason = f"Insufficient position. Required: {order.quantity}, Available: {position.quantity if position else 0}"
            order.save()
            return order

        # Execute order
        portfolio.virtual_cash += order.quantity * current_price
        portfolio.save()

        order.filled_price = current_price
        order.filled_at = timezone.now()
        order.status = 'filled'
        order.save()

        # Update or close position
        if position.quantity == order.quantity:
            position.delete()  # Close position
        else:
            position.quantity -= order.quantity
            position.save()

        # Recalculate portfolio value
        portfolio.calculate_portfolio_value()
        portfolio.calculate_return()

        return order

    def _update_position(self, portfolio, asset, quantity, price):
        """Create or update position"""
        from ..models.paper_position import PaperPosition
        
        position, created = portfolio.positions.get_or_create(
            asset=asset,
            defaults={
                'quantity': quantity,
                'avg_price': price
            }
        )

        if not created:
            # Calculate new average price
            total_cost = (position.quantity * position.avg_price) + (quantity * price)
            total_quantity = position.quantity + quantity
            position.avg_price = total_cost / total_quantity
            position.quantity = total_quantity
            position.save()

    @transaction.atomic
    def execute_limit_order(self, portfolio, asset_symbol, side, quantity, limit_price):
        """
        Create limit order (to be filled when price matches)
        
        Args:
            limit_price: Decimal (price threshold)
            
        Returns:
            PaperTradingOrder instance (pending)
        """
        asset = Asset.objects.get(symbol=asset_symbol.upper())

        # Validate order
        if side == 'buy':
            required = quantity * limit_price
            if portfolio.virtual_cash < required:
                raise ValidationError(f"Insufficient funds for limit order")
        else:
            position = portfolio.positions.filter(asset=asset).first()
            if not position or position.quantity < quantity:
                raise ValidationError(f"Insufficient position for limit order")

        # Create pending order
        order = PaperTradingOrder.objects.create(
            portfolio=portfolio,
            asset=asset,
            order_type='limit',
            side=side,
            quantity=Decimal(str(quantity)),
            price=Decimal(str(limit_price)),
            status='pending'
        )

        # Add to limit order queue (background task will monitor)
        return order

    def cancel_order(self, order_id):
        """Cancel pending order"""
        try:
            order = PaperTradingOrder.objects.get(id=order_id, status='pending')
            order.status = 'cancelled'
            order.save()
            return True
        except PaperTradingOrder.DoesNotExist:
            return False

    def calculate_portfolio_value(self, portfolio):
        """Calculate total portfolio value (cash + positions)"""
        total = portfolio.virtual_cash

        for position in portfolio.positions.all():
            current_price = self.market_data.get_current_price(position.asset.symbol)
            total += position.quantity * current_price

        return total

    def get_positions(self, portfolio):
        """Get all positions with current values"""
        positions = []
        for position in portfolio.positions.all():
            current_price = self.market_data.get_current_price(position.asset.symbol)
            market_value = position.quantity * current_price
            cost_basis = position.quantity * position.avg_price
            pl = market_value - cost_basis
            pl_percent = (pl / cost_basis * 100) if cost_basis > 0 else 0

            positions.append({
                'id': position.id,
                'symbol': position.asset.symbol,
                'quantity': position.quantity,
                'avg_price': position.avg_price,
                'current_price': current_price,
                'market_value': market_value,
                'pl': pl,
                'pl_percent': pl_percent
            })

        return positions
```

**Tasks:**
- [ ] Create `PaperTradingEngine` class
- [ ] Implement `execute_market_order()` method
- [ ] Implement `_execute_buy_order()` method
- [ ] Implement `_execute_sell_order()` method
- [ ] Implement `_update_position()` method
- [ ] Implement `execute_limit_order()` method
- [ ] Implement `cancel_order()` method
- [ ] Implement `calculate_portfolio_value()` method
- [ ] Implement `get_positions()` method
- [ ] Add comprehensive error handling
- [ ] Add transaction wrapping for atomicity
- [ ] Create `PaperPosition` model (if not exists)

---

### Task 4: API Endpoints (2h)
**File:** `apps/backend/src/trading/api/paper_trading.py`

**Requirements:**
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import PaperTradingPortfolio, PaperTradingOrder
from ..services.paper_trading_engine import PaperTradingEngine
from ..serializers import (
    PaperTradingPortfolioSerializer,
    PaperTradingOrderSerializer,
    CreateOrderSerializer
)

class PaperTradingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    engine = PaperTradingEngine()

    def list_portfolios(self, request):
        """Get user's paper trading portfolio"""
        portfolio, created = PaperTradingPortfolio.objects.get_or_create(
            user=request.user,
            defaults={
                'virtual_cash': 100000,
                'initial_cash': 100000
            }
        )

        # Recalculate portfolio value
        portfolio.calculate_portfolio_value()
        portfolio.calculate_return()

        serializer = PaperTradingPortfolioSerializer(portfolio)
        return Response(serializer.data)

    def create_order(self, request):
        """Create new order"""
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get portfolio
        portfolio = get_object_or_404(PaperTradingPortfolio, user=request.user)

        # Execute order
        if serializer.validated_data['order_type'] == 'market':
            order = self.engine.execute_market_order(
                portfolio=portfolio,
                asset_symbol=serializer.validated_data['symbol'],
                side=serializer.validated_data['side'],
                quantity=serializer.validated_data['quantity']
            )
        else:
            order = self.engine.execute_limit_order(
                portfolio=portfolio,
                asset_symbol=serializer.validated_data['symbol'],
                side=serializer.validated_data['side'],
                quantity=serializer.validated_data['quantity'],
                limit_price=serializer.validated_data.get('price')
            )

        return Response(PaperTradingOrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def list_orders(self, request):
        """Get user's orders"""
        portfolio = get_object_or_404(PaperTradingPortfolio, user=request.user)
        orders = portfolio.orders.all()[:100]  # Last 100 orders

        serializer = PaperTradingOrderSerializer(orders, many=True)
        return Response(serializer.data)

    def cancel_order(self, request, pk=None):
        """Cancel pending order"""
        portfolio = get_object_or_404(PaperTradingPortfolio, user=request.user)
        order = get_object_or_404(PaperTradingOrder, pk=pk, portfolio=portfolio)

        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success = self.engine.cancel_order(order.id)
        if success:
            return Response({'message': 'Order cancelled'})
        else:
            return Response(
                {'error': 'Failed to cancel order'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def list_positions(self, request):
        """Get user's positions"""
        portfolio = get_object_or_404(PaperTradingPortfolio, user=request.user)
        positions = self.engine.get_positions(portfolio)

        return Response(positions)

    @action(detail=False, methods=['post'])
    def reset_portfolio(self, request):
        """Reset portfolio to initial state"""
        portfolio = get_object_or_404(PaperTradingPortfolio, user=request.user)
        portfolio.reset_portfolio()

        return Response({'message': 'Portfolio reset successfully'})

    @action(detail=False, methods=['get'])
    def performance(self, request):
        """Get portfolio performance history"""
        portfolio = get_object_or_404(PaperTradingPortfolio, user=request.user)

        # Get historical performance (last 24 hours)
        # This would require a separate model to track historical values
        # For now, return current value
        return Response({
            'current_value': portfolio.portfolio_value,
            'total_return': portfolio.total_return,
            'history': []  # TODO: Implement historical tracking
        })
```

**Tasks:**
- [ ] Create `PaperTradingViewSet`
- [ ] Implement `list_portfolios()` endpoint (GET /api/paper-trading/portfolio/)
- [ ] Implement `create_order()` endpoint (POST /api/paper-trading/orders/)
- [ ] Implement `list_orders()` endpoint (GET /api/paper-trading/orders/)
- [ ] Implement `cancel_order()` endpoint (DELETE /api/paper-trading/orders/{id}/)
- [ ] Implement `list_positions()` endpoint (GET /api/paper-trading/positions/)
- [ ] Implement `reset_portfolio()` endpoint (POST /api/paper-trading/reset/)
- [ ] Implement `performance()` endpoint (GET /api/paper-trading/performance/)
- [ ] Create serializers
- [ ] Add URL routing
- [ ] Add permission classes (user can only access their own portfolio)

---

### Task 5: WebSocket Integration (1h)
**File:** `apps/backend/src/trading/consumers/paper_trading.py`

**Requirements:**
```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class PaperTradingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user_id = self.scope["user"].id
        self.group_name = f"paper_trading_{self.user_id}"

        # Join user's personal group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def portfolio_update(self, event):
        """Send portfolio update to client"""
        await self.send(text_data=json.dumps({
            'type': 'portfolio_update',
            'data': event['data']
        }))

    async def order_update(self, event):
        """Send order update to client"""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'data': event['data']
        }))

    async def position_update(self, event):
        """Send position update to client"""
        await self.send(text_data=json.dumps({
            'type': 'position_update',
            'data': event['data']
        }))
```

**Tasks:**
- [ ] Create `PaperTradingConsumer` for WebSocket
- [ ] Implement `connect()` method with authentication
- [ ] Implement `disconnect()` method
- [ ] Implement `portfolio_update()` broadcast
- [ ] Implement `order_update()` broadcast
- [ ] Implement `position_update()` broadcast
- [ ] Add WebSocket routing
- [ ] Test WebSocket connection

** Broadcasting Updates:**
After order execution, broadcast updates:

```python
# In PaperTradingEngine._execute_buy_order()
await self.channel_layer.group_send(
    f"paper_trading_{portfolio.user_id}",
    {
        'type': 'portfolio_update',
        'data': {
            'portfolio_value': float(portfolio.portfolio_value),
            'virtual_cash': float(portfolio.virtual_cash),
            'total_return': float(portfolio.total_return)
        }
    }
)
```

---

## ✅ ACCEPTANCE CRITERIA

Your backend work is complete when:

- [ ] `PaperTradingPortfolio` model created and migrated
- [ ] `PaperTradingOrder` model created and migrated
- [ ] `PaperPosition` model created and migrated
- [ ] `PaperTradingEngine` implements all methods
- [ ] Market orders execute correctly
- [ ] Limit orders created correctly (pending status)
- [ ] Order cancellation works
- [ ] Portfolio value calculated correctly
- [ ] All API endpoints working
- [ ] WebSocket consumer created
- [ ] All methods have error handling
- [ ] All database operations are atomic (transactions)
- [ ] API has proper permissions (user isolation)
- [ ] Zero security vulnerabilities (validated by Charo)

---

## 📊 SUCCESS METRICS

- API response time < 200ms (p95)
- Order execution < 100ms
- WebSocket latency < 50ms
- 100% test coverage for engine and API
- Zero data races (atomic transactions)
- Handles 1000+ concurrent users

---

## 🚀 NEXT STEPS

### Immediate (Today)
1. **Create branch:** `feature/c-036-paper-trading-backend`
2. **Create models:** Portfolio, Order, Position
3. **Run migrations:** Set up database schema
4. **Contact Turing:** Coordinate API integration

### This Week
1. **Build engine:** Complete PaperTradingEngine
2. **Create API:** All endpoints working
3. **Add WebSocket:** Real-time updates
4. **Write tests:** Unit tests for engine
5. **Coordinate with Turing:** Frontend integration

### Next Week
1. **Security review:** Charo will audit code
2. **Performance testing:** Load test with 1000+ users
3. **Bug fixes:** Address issues from QA
4. **Documentation:** Document API endpoints

---

## 📞 COMMUNICATION

**Daily Check-ins:**
- Turing: Frontend progress, API questions
- GRACE: Testing status, bug reports
- Charo: Security review feedback

**Weekly Updates:**
- Report progress to GAUDÍ (Architect)
- Flag blockers immediately

**Ask for help:**
- Market data integration → ARIA (coordination)
- Security questions → Charo
- Database optimization → ARIA
- Testing failures → GRACE

---

## 🔄 COORDINATION WITH TURING

**Turing needs:**
1. API endpoints (provide URL documentation)
2. Request/response formats (provide examples)
3. WebSocket message format (provide schema)
4. Error codes (provide documentation)

**Before Turing starts:**
- [ ] All API endpoints working
- [ ] API documentation complete
- [ ] WebSocket working
- [ ] Test data available

**During development:**
- Daily sync with Turing
- Provide API updates immediately
- Fix API bugs quickly

---

**Status:** ✅ Task Assigned
**Timeline:** Start immediately, quality-driven
**Collaborators:** Turing (FE), GRACE (QA), Charo (Security)

---

⚙️ *Linus - Backend Coder*

🔧 *Focus: C-036 Paper Trading Engine*

*"Quality over speed. The details matter."*
