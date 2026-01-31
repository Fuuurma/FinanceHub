# Task C-036: Paper Trading System

**Priority:** P1 HIGH
**Estimated Time:** 16-20 hours
**Assigned To:** Backend Coder + Frontend Coder
**Status:** PENDING

## ⚡ Quick Start Guide

**What to do FIRST (in order):**

1. **Backend (Step 1):** Create models (2h) - PaperTradingAccount, PaperTrade
2. **Backend (Step 2):** Create service (3h) - Trading logic, validation
3. **Backend (Step 3):** Create API endpoints (2h) - 6 REST endpoints
4. **Backend (Step 4):** Create account initialization (1h) - Auto-create accounts
5. **Frontend (Step 5):** Create dashboard (2h) - Main UI page
6. **Frontend (Step 6):** Create trade form (1.5h) - Buy/sell interface
7. **Frontend (Step 7):** Create portfolio summary (1h) - Positions display
8. **Frontend (Step 8):** Create trade history (1h) - Table with filters
9. **Frontend (Step 9):** Add navigation (0.5h) - Menu integration
10. **Frontend (Step 10):** Polish and test (1h) - Refine UI

**Total: 15 hours (estimate)**

---

## Overview
Implement a complete paper trading system that allows users to practice trading strategies with virtual money without risking real capital. This is essential for users to test strategies before live trading.

## User Story
As a user, I want to practice trading with a virtual portfolio so I can test my strategies and learn to use the platform without risking real money.

---

## 🔧 STEP-BY-STEP IMPLEMENTATION GUIDE

### STEP 1: Create Database Models (2 hours)

**File:** `apps/backend/src/trading/models/__init__.py`

```python
from .paper_trading import PaperTradingAccount, PaperTrade

__all__ = ['PaperTradingAccount', 'PaperTrade']
```

**File:** `apps/backend/src/trading/models/paper_trading.py`

```python
from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.common.models import UUIDModel, TimestampedModel, SoftDeleteModel
from apps.investments.models import Asset

class PaperTradingAccount(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Virtual trading account for paper trading.
    
    Users can practice trading without risking real money.
    Each user gets one paper trading account with virtual funds.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paper_trading_account'
    )
    
    # Cash balance
    cash_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('100000.00'),
        help_text="Virtual cash balance (default: $100,000)"
    )
    
    starting_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('100000.00'),
        help_text="Starting balance when account was created/reset"
    )
    
    # Performance metrics
    total_trades = models.IntegerField(
        default=0,
        help_text="Total number of trades executed"
    )
    
    winning_trades = models.IntegerField(
        default=0,
        help_text="Number of profitable trades"
    )
    
    losing_trades = models.IntegerField(
        default=0,
        help_text="Number of unprofitable trades"
    )
    
    total_return = models.FloatField(
        default=0.0,
        help_text="Total return percentage"
    )
    
    # Reset tracking
    last_reset_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time account was reset"
    )
    
    reset_count = models.IntegerField(
        default=0,
        help_text="Number of times account has been reset"
    )
    
    class Meta:
        db_table = 'paper_trading_accounts'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['total_return']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - Paper Trading Account (${self.cash_balance:,.2f})"
    
    @property
    def portfolio_value(self) -> Decimal:
        """Calculate current portfolio value (cash + positions)."""
        from ..services.paper_trading_service import PaperTradingService
        service = PaperTradingService()
        return service.calculate_portfolio_value(self.user)
    
    @property
    def total_value(self) -> Decimal:
        """Total account value (cash + portfolio)."""
        return self.cash_balance + self.portfolio_value
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate (winning trades / total trades)."""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
    
    def reset_account(self):
        """Reset account to starting balance."""
        self.cash_balance = self.starting_balance
        self.last_reset_at = timezone.now()
        self.reset_count += 1
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_return = 0.0
        self.save()
        
        # Delete all existing positions
        self.paper_trades.all().delete()


class PaperTrade(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Individual paper trade execution.
    
    Tracks all virtual trades for performance analysis.
    """
    account = models.ForeignKey(
        PaperTradingAccount,
        on_delete=models.CASCADE,
        related_name='paper_trades'
    )
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name='paper_trades'
    )
    
    trade_type = models.CharField(
        max_length=10,
        choices=[('BUY', 'Buy'), ('SELL', 'Sell')]
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Quantity traded (can be fractional for crypto)"
    )
    
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Execution price per share/coin"
    )
    
    # Execution details
    executed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the trade was executed"
    )
    
    # Simulated slippage (small random price variation)
    slippage = models.FloatField(
        default=0.0,
        help_text="Simulated slippage percentage (e.g., 0.01 for 1%)"
    )
    
    # Trade value
    total_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Total trade value (quantity * price)"
    )
    
    # Performance tracking
    is_winning = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether this trade was profitable (for closed positions)"
    )
    
    profit_loss = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Profit/loss for this trade"
    )
    
    class Meta:
        db_table = 'paper_trades'
        indexes = [
            models.Index(fields=['account', 'executed_at']),
            models.Index(fields=['asset']),
            models.Index(fields=['trade_type']),
        ]
    
    def __str__(self):
        return f"{self.trade_type} {self.quantity} {self.asset.symbol} @ ${self.price}"
```

**CREATE MIGRATION:**
```bash
python manage.py makemigrations trading
python manage.py migrate trading
```

---

### STEP 2: Create Paper Trading Service (3 hours) ⭐ CRITICAL

**File:** `apps/backend/src/trading/services/paper_trading_service.py`

```python
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional
from ..models import PaperTradingAccount, PaperTrade
from apps.investments.models import Asset
from apps.market_data.services.market_data_service import MarketDataService

class PaperTradingService:
    """
    Paper trading service for virtual trading.
    
    Handles:
    - Account creation/management
    - Buy/sell order execution
    - Portfolio tracking
    - Performance metrics
    """
    
    def __init__(self):
        self.market_data = MarketDataService()
    
    def get_or_create_account(self, user) -> PaperTradingAccount:
        """
        Get or create paper trading account for user.
        
        Args:
            user: User instance
            
        Returns:
            PaperTradingAccount instance
        """
        account, created = PaperTradingAccount.objects.get_or_create(
            user=user,
            defaults={
                'cash_balance': Decimal('100000.00'),
                'starting_balance': Decimal('100000.00')
            }
        )
        
        if created:
            account.last_reset_at = timezone.now()
            account.save()
        
        return account
    
    def execute_buy_order(
        self,
        user,
        asset_symbol: str,
        quantity: Decimal
    ) -> Dict:
        """
        Execute a virtual buy order.
        
        Args:
            user: User instance
            asset_symbol: Asset symbol (e.g., 'AAPL')
            quantity: Quantity to buy
            
        Returns:
            Dictionary with execution result
        """
        # Get account
        account = self.get_or_create_account(user)
        
        # Get asset
        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            return {'success': False, 'error': 'Asset not found'}
        
        # Get current price
        try:
            current_price = self.market_data.get_current_price(asset_symbol)
            if current_price is None:
                return {'success': False, 'error': 'Price not available'}
        except Exception as e:
            return {'success': False, 'error': f'Error fetching price: {str(e)}'}
        
        # Calculate trade value
        trade_value = Decimal(str(current_price)) * quantity
        
        # Validate sufficient funds
        if trade_value > account.cash_balance:
            return {
                'success': False,
                'error': 'Insufficient funds',
                'required': float(trade_value),
                'available': float(account.cash_balance)
            }
        
        # Simulate slippage (small random price variation, max 0.1%)
        import random
        slippage = random.uniform(-0.001, 0.001)  # -0.1% to +0.1%
        execution_price = Decimal(str(current_price)) * (Decimal('1') + Decimal(str(slippage)))
        
        # Execute trade within transaction
        with transaction.atomic():
            # Deduct cash
            account.cash_balance -= trade_value
            account.total_trades += 1
            account.save()
            
            # Create trade record
            trade = PaperTrade.objects.create(
                account=account,
                asset=asset,
                trade_type='BUY',
                quantity=quantity,
                price=execution_price,
                total_value=trade_value,
                slippage=slippage * 100  # Convert to percentage
            )
        
        return {
            'success': True,
            'trade_id': str(trade.id),
            'asset': asset_symbol,
            'quantity': float(quantity),
            'price': float(execution_price),
            'total_value': float(trade_value),
            'remaining_cash': float(account.cash_balance)
        }
    
    def execute_sell_order(
        self,
        user,
        asset_symbol: str,
        quantity: Decimal
    ) -> Dict:
        """
        Execute a virtual sell order.
        
        Args:
            user: User instance
            asset_symbol: Asset symbol
            quantity: Quantity to sell
            
        Returns:
            Dictionary with execution result
        """
        # Get account
        account = self.get_or_create_account(user)
        
        # Get asset
        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            return {'success': False, 'error': 'Asset not found'}
        
        # Check if user has sufficient position
        current_position = self.get_position(account, asset_symbol)
        if current_position < quantity:
            return {
                'success': False,
                'error': 'Insufficient position',
                'owned': float(current_position),
                'requested': float(quantity)
            }
        
        # Get current price
        try:
            current_price = self.market_data.get_current_price(asset_symbol)
            if current_price is None:
                return {'success': False, 'error': 'Price not available'}
        except Exception as e:
            return {'success': False, 'error': f'Error fetching price: {str(e)}'}
        
        # Calculate trade value
        trade_value = Decimal(str(current_price)) * quantity
        
        # Calculate P&L (average buy price vs current sell price)
        avg_buy_price = self.get_average_buy_price(account, asset_symbol)
        profit_loss = (Decimal(str(current_price)) - avg_buy_price) * quantity
        
        # Update win/loss tracking
        if profit_loss > 0:
            account.winning_trades += 1
        else:
            account.losing_trades += 1
        
        # Simulate slippage
        import random
        slippage = random.uniform(-0.001, 0.001)
        execution_price = Decimal(str(current_price)) * (Decimal('1') + Decimal(str(slippage)))
        
        # Execute trade within transaction
        with transaction.atomic():
            # Add cash
            account.cash_balance += trade_value
            account.total_trades += 1
            account.save()
            
            # Create trade record
            trade = PaperTrade.objects.create(
                account=account,
                asset=asset,
                trade_type='SELL',
                quantity=quantity,
                price=execution_price,
                total_value=trade_value,
                slippage=slippage * 100,
                profit_loss=profit_loss,
                is_winning=(profit_loss > 0)
            )
        
        return {
            'success': True,
            'trade_id': str(trade.id),
            'asset': asset_symbol,
            'quantity': float(quantity),
            'price': float(execution_price),
            'total_value': float(trade_value),
            'profit_loss': float(profit_loss),
            'remaining_cash': float(account.cash_balance)
        }
    
    def get_position(self, account: PaperTradingAccount, asset_symbol: str) -> Decimal:
        """
        Get current position size for an asset.
        
        Args:
            account: PaperTradingAccount instance
            asset_symbol: Asset symbol
            
        Returns:
            Current position (can be negative for short positions)
        """
        from django.db.models import Sum
        
        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            return Decimal('0')
        
        # Calculate net position (buys - sells)
        buys = PaperTrade.objects.filter(
            account=account,
            asset=asset,
            trade_type='BUY'
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        sells = PaperTrade.objects.filter(
            account=account,
            asset=asset,
            trade_type='SELL'
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        return buys - sells
    
    def get_average_buy_price(self, account: PaperTradingAccount, asset_symbol: str) -> Decimal:
        """
        Calculate average buy price for an asset.
        
        Args:
            account: PaperTradingAccount instance
            asset_symbol: Asset symbol
            
        Returns:
            Average buy price
        """
        from django.db.models import Sum, F
        
        try:
            asset = Asset.objects.get(symbol=asset_symbol.upper())
        except Asset.DoesNotExist:
            return Decimal('0')
        
        # Get all buy trades
        buy_trades = PaperTrade.objects.filter(
            account=account,
            asset=asset,
            trade_type='BUY'
        )
        
        total_value = buy_trades.aggregate(total=Sum('total_value'))['total'] or Decimal('0')
        total_quantity = buy_trades.aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        if total_quantity == 0:
            return Decimal('0')
        
        return total_value / total_quantity
    
    def calculate_portfolio_value(self, user) -> Decimal:
        """
        Calculate total portfolio value (all positions at current prices).
        
        Args:
            user: User instance
            
        Returns:
            Total portfolio value
        """
        account = self.get_or_create_account(user)
        
        # Get all unique assets in portfolio
        assets_with_positions = PaperTrade.objects.filter(
            account=account
        ).values_list('asset__symbol', flat=True).distinct()
        
        total_value = Decimal('0')
        
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
        """
        Get complete portfolio summary.
        
        Args:
            user: User instance
            
        Returns:
            Dictionary with portfolio details
        """
        account = self.get_or_create_account(user)
        
        # Get all positions
        assets_with_positions = PaperTrade.objects.filter(
            account=account
        ).values_list('asset__symbol', flat=True).distinct()
        
        positions = []
        total_cost_basis = Decimal('0')
        total_market_value = Decimal('0')
        
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
                        
                        positions.append({
                            'symbol': symbol,
                            'name': asset.name,
                            'quantity': float(position),
                            'avg_price': float(avg_buy_price),
                            'current_price': float(current_price),
                            'market_value': float(market_value),
                            'cost_basis': float(cost_basis),
                            'profit_loss': float(profit_loss),
                            'profit_loss_pct': float((profit_loss / cost_basis) * 100) if cost_basis > 0 else 0
                        })
                        
                        total_cost_basis += cost_basis
                        total_market_value += market_value
                except:
                    continue
        
        return {
            'cash_balance': float(account.cash_balance),
            'portfolio_value': float(total_market_value),
            'total_value': float(account.cash_balance + total_market_value),
            'total_return': float(((account.cash_balance + total_market_value - account.starting_balance) / account.starting_balance) * 100),
            'positions': positions,
            'total_trades': account.total_trades,
            'win_rate': account.win_rate,
            'winning_trades': account.winning_trades,
            'losing_trades': account.losing_trades
        }
    
    def get_trade_history(self, user, limit: int = 100) -> List[Dict]:
        """
        Get trade history.
        
        Args:
            user: User instance
            limit: Maximum number of trades to return
            
        Returns:
            List of trades
        """
        account = self.get_or_create_account(user)
        
        trades = PaperTrade.objects.filter(
            account=account
        ).select_related('asset').order_by('-executed_at')[:limit]
        
        return [
            {
                'id': str(trade.id),
                'asset': trade.asset.symbol,
                'type': trade.trade_type,
                'quantity': float(trade.quantity),
                'price': float(trade.price),
                'total_value': float(trade.total_value),
                'executed_at': trade.executed_at.isoformat(),
                'profit_loss': float(trade.profit_loss) if trade.profit_loss else None
            }
            for trade in trades
        ]


# QUICK TEST
if __name__ == '__main__':
    from django.contrib.auth import get_user_model
    
    service = PaperTradingService()
    
    # Get test user
    User = get_user_model()
    user = User.objects.first()
    
    # Execute test buy
    result = service.execute_buy_order(user, 'AAPL', Decimal('10'))
    print(f"Buy result: {result}")
```

---

### STEP 3: Create API Endpoints (2 hours)

**File:** `apps/backend/src/trading/api/paper_trading.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal, InvalidOperation
from ..services.paper_trading_service import PaperTradingService

class PaperTradingViewSet(viewsets.ViewSet):
    """
    Paper trading API endpoints.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = PaperTradingService()
    
    def list(self, request):
        """
        GET /api/paper-trading/account
        Get paper trading account details.
        """
        account = self.service.get_or_create_account(request.user)
        summary = self.service.get_portfolio_summary(request.user)
        
        return Response({
            'account': {
                'cash_balance': float(account.cash_balance),
                'starting_balance': float(account.starting_balance),
                'total_trades': account.total_trades,
                'win_rate': account.win_rate,
                'reset_count': account.reset_count
            },
            'summary': summary
        })
    
    @action(detail=False, methods=['post'])
    def buy(self, request):
        """
        POST /api/paper-trading/buy
        Execute a buy order.
        """
        asset_symbol = request.data.get('asset')
        quantity = request.data.get('quantity')
        
        if not asset_symbol or not quantity:
            return Response(
                {'error': 'asset and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = Decimal(str(quantity))
        except (InvalidOperation, ValueError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = self.service.execute_buy_order(request.user, asset_symbol, quantity)
        
        if not result.get('success'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def sell(self, request):
        """
        POST /api/paper-trading/sell
        Execute a sell order.
        """
        asset_symbol = request.data.get('asset')
        quantity = request.data.get('quantity')
        
        if not asset_symbol or not quantity:
            return Response(
                {'error': 'asset and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = Decimal(str(quantity))
        except (InvalidOperation, ValueError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = self.service.execute_sell_order(request.user, asset_symbol, quantity)
        
        if not result.get('success'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def reset(self, request):
        """
        POST /api/paper-trading/reset
        Reset paper trading account.
        """
        account = self.service.get_or_create_account(request.user)
        account.reset_account()
        
        return Response({
            'success': True,
            'message': 'Account reset successfully',
            'new_balance': float(account.cash_balance)
        })
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        GET /api/paper-trading/history
        Get trade history.
        """
        limit = int(request.query_params.get('limit', 100))
        trades = self.service.get_trade_history(request.user, limit)
        
        return Response({'trades': trades})
    
    @action(detail=False, methods=['get'])
    def performance(self, request):
        """
        GET /api/paper-trading/performance
        Get performance metrics.
        """
        summary = self.service.get_portfolio_summary(request.user)
        
        return Response({
            'total_return': summary['total_return'],
            'win_rate': summary['win_rate'],
            'total_trades': summary['total_trades'],
            'winning_trades': summary['winning_trades'],
            'losing_trades': summary['losing_trades']
        })
```

---

### STEP 4: Auto-Create Accounts (1 hour)

**File:** `apps/backend/src/users/signals.py`

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from trading.services.paper_trading_service import PaperTradingService

User = get_user_model()

@receiver(post_save, sender=User)
def create_paper_trading_account(sender, instance, created, **kwargs):
    """
    Auto-create paper trading account when user is created.
    """
    if created:
        service = PaperTradingService()
        service.get_or_create_account(instance)
```

---

## 📚 COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Not Validating Sufficient Funds
```python
# WRONG - Allows negative cash balance
account.cash_balance -= trade_value
account.save()

# CORRECT - Validate first
if trade_value > account.cash_balance:
    raise ValidationError("Insufficient funds")
account.cash_balance -= trade_value
account.save()
```

### ❌ Mistake 2: Not Using Database Transactions
```python
# WRONG - Cash deducted but trade record creation fails
account.cash_balance -= trade_value
account.save()
trade = PaperTrade.objects.create(...)  # If this fails, money is lost!

# CORRECT - Use atomic transaction
with transaction.atomic():
    account.cash_balance -= trade_value
    account.save()
    trade = PaperTrade.objects.create(...)  # All or nothing
```

### ❌ Mistake 3: Forgetting to Check Position Before Selling
```python
# WRONG - Allows selling more than owned
service.execute_sell_order(user, 'AAPL', Decimal('1000'))

# CORRECT - Check position first
current_position = service.get_position(account, 'AAPL')
if current_position < quantity:
    raise ValidationError("Insufficient position")
```

### ❌ Mistake 4: Not Calculating Average Buy Price Correctly
```python
# WRONG - Simple average (wrong for multiple buys at different prices)
avg_price = sum(prices) / len(prices)

# CORRECT - Weighted average by quantity
total_value = sum(quantity * price for each buy)
total_quantity = sum(quantities)
avg_price = total_value / total_quantity
```

### ❌ Mistake 5: Not Handling Decimal Precision
```python
# WRONG - Uses float (rounding errors)
price = 150.123456789

# CORRECT - Uses Decimal for financial calculations
price = Decimal('150.12')
```

---

## ❓ FAQ

**Q: Should paper trading use real-time or delayed data?**  
A: Real-time data is best for realistic simulation. Use your existing MarketDataService.

**Q: How much starting balance should users get?**  
A: $100,000 is standard. Make it configurable in user settings.

**Q: Should paper trading have slippage?**  
A: YES! Small random slippage (±0.1%) makes it more realistic.

**Q: Should we track margin/short selling?**  
A: Start with cash-only. Add margin in v2 (more complex).

**Q: How long should we keep trade history?**  
A: Forever for user analysis, but only show last 1000 in API.

**Q: Should paper trading have commissions?**  
A: NO! Paper trading should be free. Commissions would discourage practice.

**Q: Can users have multiple paper accounts?**  
A: Start with one per user. Add multiple accounts in v2.

---

## 📦 FRONTEND IMPLEMENTATION GUIDE

### File: `apps/frontend/src/components/paper-trading/PaperTradeForm.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface PaperTradeFormProps {
  onSuccess: () => void;
}

export function PaperTradeForm({ onSuccess }: PaperTradeFormProps) {
  const [asset, setAsset] = useState('');
  const [quantity, setQuantity] = useState('');
  const [tradeType, setTradeType] = useState<'BUY' | 'SELL'>('BUY');
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    const endpoint = tradeType === 'BUY'
      ? '/api/paper-trading/buy'
      : '/api/paper-trading/sell';
    
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset, quantity: parseFloat(quantity) })
      });
      
      const data = await response.json();
      
      if (data.success) {
        onSuccess();
        setAsset('');
        setQuantity('');
      } else {
        alert(data.error || 'Trade failed');
      }
    } catch (error) {
      alert('Error executing trade');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">
          Trade Type
        </label>
        <div className="flex gap-2">
          <Button
            type="button"
            variant={tradeType === 'BUY' ? 'default' : 'outline'}
            onClick={() => setTradeType('BUY')}
            className={tradeType === 'BUY' ? 'bg-green-600' : ''}
          >
            BUY
          </Button>
          <Button
            type="button"
            variant={tradeType === 'SELL' ? 'default' : 'outline'}
            onClick={() => setTradeType('SELL')}
            className={tradeType === 'SELL' ? 'bg-red-600' : ''}
          >
            SELL
          </Button>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium mb-1">
          Asset Symbol
        </label>
        <Input
          type="text"
          value={asset}
          onChange={(e) => setAsset(e.target.value.toUpperCase())}
          placeholder="AAPL"
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium mb-1">
          Quantity
        </label>
        <Input
          type="number"
          step="0.0001"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          placeholder="10"
          required
        />
      </div>
      
      <Button
        type="submit"
        disabled={loading}
        className={tradeType === 'BUY' ? 'bg-green-600' : 'bg-red-600'}
      >
        {loading ? 'Executing...' : `${tradeType} ${asset || 'Asset'}`}
      </Button>
    </form>
  );
}
```

---

## 📋 CHECKLIST BEFORE SUBMITTING

- [ ] All models created with base classes
- [ ] Migration created and applied
- [ ] Buy/sell validation working
- [ ] Sufficient funds check implemented
- [ ] Sufficient position check implemented
- [ ] Database transactions used
- [ ] Slippage simulation working
- [ ] Portfolio calculation accurate
- [ ] API endpoints have authentication
- [ ] Trade form submits correctly
- [ ] Real-time updates working
- [ ] Reset functionality working
- [ ] Performance metrics accurate

---

## 🎯 SUCCESS CRITERIA

1. ✅ Paper account auto-creates on signup
2. ✅ Buy/sell executes in < 100ms
3. ✅ Portfolio value updates in real-time
4. ✅ Trade history shows all trades
5. ✅ Reset functionality works
6. ✅ Users can practice without real money
7. ✅ Clear distinction from real trading

---

**Start with Step 1 (models) and work through each step sequentially.**
