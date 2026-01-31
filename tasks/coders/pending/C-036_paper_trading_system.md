# 📊 TASK: C-036 - Paper Trading System

**Task ID:** C-036
**Created:** February 1, 2026
**Assigned To:** Backend Coder (Linus) + Frontend Coder (Turing)
**Status:** ⏳ PENDING
**Priority:** P1 HIGH
**Estimated Time:** 16-20 hours
**Deadline:** March 1, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Create a realistic paper trading (simulated trading) system that allows users to:
- Practice trading without real money
- Test investment strategies
- Track paper trading performance
- Compare paper trading vs real portfolios
- Simulate market conditions

---

## 📋 REQUIREMENTS

### 1. Paper Trading Models

```python
# apps/backend/src/trading/models/paper_trading.py
class PaperTradingAccount(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    name = CharField()  # e.g., "My Practice Portfolio"
    starting_cash = DecimalField(max_digits=12, decimal_places=2)
    current_cash = DecimalField(max_digits=12, decimal_places=2)
    portfolio_value = DecimalField(max_digits=12, decimal_places=2)
    total_value = DecimalField(max_digits=12, decimal_places=2)
    total_return = DecimalField(max_digits=8, decimal_places=4)
    created_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True)

class PaperTrade(models.Model):
    account = ForeignKey(PaperTradingAccount)
    symbol = CharField()
    trade_type = CharField()  # 'buy', 'sell', 'short', 'cover'
    quantity = DecimalField(max_digits=12, decimal_places=4)
    price = DecimalField(max_digits=12, decimal_places=4)
    commission = DecimalField(max_digits=8, decimal_places=2, default=0)
    executed_at = DateTimeField(auto_now_add=True)
    order_type = CharField()  # 'market', 'limit', 'stop'
    status = CharField()  # 'pending', 'filled', 'cancelled'

class PaperPosition(models.Model):
    account = ForeignKey(PaperTradingAccount)
    symbol = CharField()
    quantity = DecimalField(max_digits=12, decimal_places=4)
    average_cost = DecimalField(max_digits=12, decimal_places=4)
    current_price = DecimalField(max_digits=12, decimal_places=4)
    market_value = DecimalField(max_digits=12, decimal_places=4)
    cost_basis = DecimalField(max_digits=12, decimal_places=4)
    unrealized_gains = DecimalField(max_digits=12, decimal_places=2)
    unrealized_gains_pct = DecimalField(max_digits=8, decimal_places=4)
    realized_gains = DecimalField(max_digits=12, decimal_places=2)
    updated_at = DateTimeField(auto_now=True)

class PaperTransaction(models.Model):
    account = ForeignKey(PaperTradingAccount)
    position = ForeignKey(PaperPosition)
    transaction_type = CharField()  # 'buy', 'sell', 'dividend'
    quantity = DecimalField(max_digits=12, decimal_places=4)
    price = DecimalField(max_digits=12, decimal_places=4)
    amount = DecimalField(max_digits=12, decimal_places=2)
    timestamp = DateTimeField(auto_now_add=True)

class PaperTradingPerformance(models.Model):
    account = ForeignKey(PaperTradingAccount)
    date = DateField()
    portfolio_value = DecimalField(max_digits=12, decimal_places=2)
    daily_return = DecimalField(max_digits=8, decimal_places=4)
    total_return = DecimalField(max_digits=8, decimal_places=4)
    benchmark_return = DecimalField(max_digits=8, decimal_places=4)
    sharpe_ratio = DecimalField(max_digits=8, decimal_places=4)
    max_drawdown = DecimalField(max_digits=8, decimal_places=4)
    win_rate = DecimalField(max_digits=5, decimal_places=2)
```

### 2. Paper Trading Service

```python
# apps/backend/src/trading/services/paper_trading_service.py
class PaperTradingService:
    def create_account(self, user_id: int, name: str,
                      starting_cash: Decimal) -> PaperTradingAccount:
        """Create new paper trading account"""
        pass

    def execute_trade(self, account_id: int, symbol: str,
                     trade_type: str, quantity: Decimal,
                     order_type: str = 'market',
                     limit_price: Decimal = None) -> PaperTrade:
        """
        Execute a paper trade:
        - Check if sufficient funds (for buys)
        - Check if sufficient position (for sells)
        - Execute at current market price
        - Update cash and positions
        - Record trade
        """
        pass

    def get_account_value(self, account_id: int) -> Decimal:
        """
        Calculate total account value:
        - Cash + Position values
        - Real-time pricing
        """
        pass

    def calculate_returns(self, account: PaperTradingAccount):
        """
        Calculate performance metrics:
        - Total return
        - Daily return
        - Benchmark comparison
        - Sharpe ratio
        - Max drawdown
        """
        pass

    def get_positions(self, account_id: int):
        """Get all positions in paper trading account"""
        pass

    def get_trade_history(self, account_id: int, days: int = 30):
        """Get trade history"""
        pass

    def close_position(self, account_id: int, symbol: str,
                      quantity: Decimal = None):
        """Close entire position or partial"""
        pass

    def reset_account(self, account_id: int):
        """Reset account to starting cash, clear positions"""
        pass

    def compare_with_real_portfolio(self, paper_account_id: int,
                                    real_portfolio_id: int):
        """Compare paper trading performance with real portfolio"""
        pass
```

### 3. API Endpoints

```python
# apps/backend/src/trading/api/paper_trading.py
from ninja import Router

router = Router()

@router.post("/paper-trading/accounts")
def create_account(request, name: str, starting_cash: float):
    """Create new paper trading account"""
    pass

@router.get("/paper-trading/accounts")
def list_accounts(request):
    """List user's paper trading accounts"""
    pass

@router.get("/paper-trading/accounts/{account_id}")
def get_account(request, account_id: int):
    """Get account details with positions"""
    pass

@router.post("/paper-trading/accounts/{account_id}/trade")
def execute_trade(request, account_id: int, symbol: str,
                 trade_type: str, quantity: float,
                 order_type: str = 'market'):
    """Execute a paper trade"""
    pass

@router.get("/paper-trading/accounts/{account_id}/positions")
def get_positions(request, account_id: int):
    """Get all positions"""
    pass

@router.get("/paper-trading/accounts/{account_id}/trades")
def get_trade_history(request, account_id: int):
    """Get trade history"""
    pass

@router.get("/paper-trading/accounts/{account_id}/performance")
def get_performance(request, account_id: int):
    """Get performance metrics"""
    pass

@router.post("/paper-trading/accounts/{account_id}/reset")
def reset_account(request, account_id: int):
    """Reset account to starting state"""
    pass

@router.delete("/paper-trading/accounts/{account_id}")
def delete_account(request, account_id: int):
    """Delete paper trading account"""
    pass
```

### 4. Frontend Components

```typescript
// apps/frontend/src/app/(dashboard)/paper-trading/page.tsx
export function PaperTradingPage() {
  // List user's paper trading accounts
  // Create new account button
  // Show account summary
  // Performance chart
  // Link to account detail
}

// apps/frontend/src/components/paper-trading/PaperTradingAccountDetail.tsx
export function PaperTradingAccountDetail({ accountId }: Props) {
  // Account value, cash, positions
  // Performance metrics
  // Trade history table
  // Buy/Sell form
  // Position list
  // Comparison with real portfolio
}

// apps/frontend/src/components/paper-trading/TradeForm.tsx
export function TradeForm({ accountId }: Props) {
  // Symbol search
  // Buy/Sell buttons
  // Quantity input
  // Order type selector (market/limit)
  // Current price display
  // Estimated total
  // Execute trade button
}

// apps/frontend/src/components/paper-trading/PerformanceChart.tsx
export function PerformanceChart({ accountId }: Props) {
  // Account value over time
  // Benchmark comparison (S&P 500)
  - Total return
  - Daily return
  - Drawdown visualization
  - Win rate display
}
```

### 5. Real-Time Pricing Integration

**Market Data Integration:**
- Use existing real-time market data API
- Update position values in real-time
- Execute trades at current market price
- Handle after-hours pricing

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Create paper trading account with custom starting cash
- [ ] Execute buy/sell orders
- [ ] Market orders execute immediately at current price
- [ ] Limit orders (future enhancement)
- [ ] Position tracking (unrealized/realized gains)
- [ ] Cash balance tracking
- [ ] Portfolio value calculation
- [ ] Performance metrics (return, Sharpe, drawdown)
- [ ] Trade history log
- [ ] Reset account functionality
- [ ] Compare paper vs real portfolio
- [ ] Real-time position updates
- [ ] API endpoints for all operations
- [ ] Responsive UI for trading
- [ ] Tests for trading service
- [ ] Prevent negative cash balance

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/backend/src/trading/models/paper_trading.py`
- `apps/backend/src/trading/services/paper_trading_service.py`
- `apps/backend/src/trading/api/paper_trading.py`
- `apps/backend/src/trading/tests/test_paper_trading.py`
- `apps/frontend/src/app/(dashboard)/paper-trading/page.tsx`
- `apps/frontend/src/components/paper-trading/PaperTradingAccountDetail.tsx`
- `apps/frontend/src/components/paper-trading/TradeForm.tsx`
- `apps/frontend/src/components/paper-trading/PerformanceChart.tsx`

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- User authentication
- Real-time market data API
- Portfolio models (for comparison)

**Related Tasks:**
- C-030: Broker API Integration (real trading)

---

## 🎯 TRADING FEATURES

### Order Types
1. **Market Order** (Phase 1)
   - Execute immediately at current price
   - No price guarantees

2. **Limit Order** (Phase 2)
   - Execute only at specified price or better
   - Good-till-cancelled or day order

3. **Stop Order** (Phase 3)
   - Trigger when price reaches stop price
   - Become market order

### Trade Types
- **Buy** (long)
- **Sell** (close long)
- **Short** (future)
- **Cover** (future)

### Commission
- Configurable commission per trade
- Default: $0 (free trading)
- Can simulate real broker commissions

---

## 📊 PERFORMANCE METRICS

### Account-Level
- **Total Return** = (Current Value - Starting Cash) / Starting Cash
- **Daily Return** = (Today Value - Yesterday Value) / Yesterday Value
- **Sharpe Ratio** = (Return - Risk Free Rate) / Standard Deviation
- **Max Drawdown** = Largest peak-to-trough decline
- **Win Rate** = Winning Trades / Total Trades

### Position-Level
- **Unrealized Gains** = (Current Price - Cost) × Quantity
- **Unrealized Gains %** = (Current Price - Cost) / Cost
- **Realized Gains** = Sum of closed position gains
- **Cost Basis** = Average purchase price

---

## 📊 DELIVERABLES

1. **Models:** PaperTradingAccount, PaperTrade, PaperPosition
2. **Service:** PaperTradingService with trading logic
3. **API:** All paper trading endpoints
4. **Frontend:** Account list, detail page, trade form, performance chart
5. **Tests:** Unit tests for trading service
6. **Documentation:** User guide for paper trading

---

## 💬 NOTES

**Implementation Approach:**
- Separate paper trading from real portfolios
- Use same market data API for pricing
- No actual money or broker API involved
- Realistic market conditions simulation

**Safety Features:**
- Prevent negative cash balance
- Validate trade before execution
- Confirm trade before executing (future)
- Set maximum daily loss limit (future)

**Market Data:**
- Use existing `/api/market/quote` endpoint
- Cache quotes for performance
- Update positions every 5 seconds (real-time)
- Handle market closed hours

**User Experience:**
- Show paper trading banner to distinguish from real
- Clear visual indicators for paper accounts
- Easy reset functionality
- Share paper trading results (future)

**Future Enhancements:**
- Options paper trading
- Margin trading
- Short selling
- Complex order types (OCO, trailing stops)
- Trading competitions
- Strategy backtesting integration

**Libraries:**
- Backend: Existing market data API
- Frontend: Real-time updates (WebSocket or polling)

---

**Status:** ⏳ READY TO START
**Assigned To:** Backend Coder (Linus) + Frontend Coder (Turing)
**User Value:** HIGH - users want to practice trading

---

📊 *C-036: Paper Trading System*
*Practice trading without real money - test strategies risk-free*
