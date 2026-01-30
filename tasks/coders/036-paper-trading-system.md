# Task C-036: Paper Trading System

**Priority:** P1 HIGH  
**Estimated Time:** 16-20 hours  
**Assigned To:** Backend Coder + Frontend Coder  
**Status:** PENDING

## Overview
Implement a complete paper trading system that allows users to practice trading strategies with virtual money without risking real capital. This is essential for users to test strategies before live trading.

## User Story
As a user, I want to practice trading with a virtual portfolio so I can test my strategies and learn to use the platform without risking real money.

## Acceptance Criteria

### Backend (12-15 hours)
- [ ] **PaperTradingAccount Model**
  - Virtual cash balance (starting with $100,000 default)
  - Virtual portfolio positions
  - Track paper trades separately from real trades
  - Performance metrics (total return, win rate, etc.)
  - Reset functionality (start over with fresh virtual money)

- [ ] **Paper Trading API Endpoints**
  - `GET /api/paper-trading/account` - Get paper account details
  - `POST /api/paper-trading/buy` - Execute virtual buy order
  - `POST /api/paper-trading/sell` - Execute virtual sell order
  - `POST /api/paper-trading/reset` - Reset paper account
  - `GET /api/paper-trading/history` - Get paper trade history
  - `GET /api/paper-trading/performance` - Get performance metrics

- [ ] **Trade Execution Simulation**
  - Use real-time market prices for execution
  - Simulate slippage (small random price variation)
  - No actual broker API calls
  - Instant execution (no order queue)
  - Validate sufficient funds before buying
  - Validate sufficient position before selling

- [ ] **Portfolio Tracking**
  - Track virtual positions separately from real portfolio
  - Real-time P&L calculation
  - Paper trading dashboard data

### Frontend (4-5 hours)
- [ ] **Paper Trading Dashboard Page**
  - Display virtual cash balance
  - Show virtual portfolio value
  - Real-time P&L display
  - Performance metrics (total return, win rate, profit factor)
  - Trade history table with filters

- [ ] **Paper Trading Interface**
  - Buy/Sell forms for any asset
  - Quick trade buttons from asset detail page
  - Order confirmation modal
  - Position size calculator integration
  - Real-time updates when trades execute

- [ ] **Paper Trading Components**
  - `PaperTradingDashboard.tsx` - Main dashboard
  - `PaperTradeForm.tsx` - Buy/sell form
  - `PaperTradeHistory.tsx` - Trade history table
  - `PaperPortfolioSummary.tsx` - Virtual portfolio summary
  - `PaperTradingResetButton.tsx` - Reset account button

- [ ] **Badges & Indicators**
  - "PAPER TRADING" badge prominently displayed
  - Clear distinction from real trading
  - Warning banners when switching between real/paper

- [ ] **Navigation**
  - Add "Paper Trading" to main navigation
  - Separate route: `/paper-trading`
  - Link from dashboard: "Try Paper Trading"

## Technical Requirements

### Backend
- **Files to Create:**
  - `apps/backend/src/trading/models/paper_trading.py`
  - `apps/backend/src/trading/api/paper_trading.py`
  - `apps/backend/src/trading/services/paper_trading_service.py`

- **Database Schema:**
  ```python
  class PaperTradingAccount(UUIDModel, TimestampedModel):
      user = ForeignKey(User, on_delete=CASCADE)
      cash_balance = DecimalField(max_digits=12, decimal_places=2)
      starting_balance = DecimalField(max_digits=12, decimal_places=2)
      total_trades = IntegerField(default=0)
      winning_trades = IntegerField(default=0)
      
  class PaperTrade(UUIDModel, TimestampedModel):
      account = ForeignKey(PaperTradingAccount, on_delete=CASCADE)
      asset = ForeignKey(Asset, on_delete=PROTECT)
      trade_type = CharField(choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
      quantity = DecimalField(max_digits=10, decimal_places=4)
      price = DecimalField(max_digits=12, decimal_places=2)
      executed_at = DateTimeField(auto_now_add=True)
  ```

- **API Integration:**
  - Use existing `MarketDataService` for real-time prices
  - No broker API calls
  - Use existing `AssetService` for asset lookup

### Frontend
- **Files to Create:**
  - `apps/frontend/src/app/(dashboard)/paper-trading/page.tsx`
  - `apps/frontend/src/components/paper-trading/PaperTradingDashboard.tsx`
  - `apps/frontend/src/components/paper-trading/PaperTradeForm.tsx`
  - `apps/frontend/src/components/paper-trading/PaperTradeHistory.tsx`
  - `apps/frontend/src/components/paper-trading/PaperPortfolioSummary.tsx`
  - `apps/frontend/src/lib/api/paper-trading.ts`

- **State Management:**
  - Use Zustand store for paper trading state
  - `paperTradingStore.ts` with actions and selectors
  - Real-time updates via polling or WebSocket

- **UI Components:**
  - Use existing Button, Input, Select components
  - Reuse AssetSearch component for trade form
  - Reuse PriceDisplay component for real-time prices
  - Green/red colors for P&L display

## Dependencies
- **Prerequisites:** C-001 (User System), C-002 (Asset Management), C-005 (Portfolio Core)
- **Related Tasks:** C-015 (Position Size Calculator), C-022 (Strategy Backtesting)
- **Blocks:** None

## Testing Requirements
- **Backend:**
  - Test paper trading account creation
  - Test buy/sell execution logic
  - Test insufficient funds validation
  - Test portfolio calculation accuracy
  - Test performance metrics calculation

- **Frontend:**
  - Test trade form submission
  - Test real-time updates
  - Test reset functionality
  - Test navigation between real/paper trading
  - Test responsive design

## Performance Considerations
- Cache paper account data (5-minute TTL)
- Optimize trade history queries (pagination)
- Use database indexes on user_id
- Limit history to last 1000 trades

## Success Metrics
- Users can create paper trading account with one click
- Trades execute in < 100ms
- Real-time updates work smoothly
- Users report high satisfaction with paper trading feature
- Reduced support requests from new users (they practice first)

## Notes
- Paper trading is CRITICAL for user onboarding
- Users want to test before risking real money
- Consider adding paper trading competitions/leaderboards
- Consider adding "copy successful paper traders" feature
- Starting balance should be configurable in settings
