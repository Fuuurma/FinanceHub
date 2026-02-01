# C-036 Paper Trading - Security Review Package

**For:** Charo (Security Specialist)
**From:** Linus (Backend Developer)
**Date:** February 1, 2026

---

## Overview

Paper Trading backend implementation complete. Requesting security audit before merging to main branch.

## Components to Review

### 1. Models (`apps/backend/src/trading/models/`)

#### PaperPosition (`paper_position.py`)
- Tracks user positions in paper trading
- Fields: `portfolio`, `asset`, `quantity`, `avg_price`
- Security note: Foreign key relationships properly protected

#### PaperTradingOrder (`paper_order.py`)
- Handles order lifecycle (pending/filled/cancelled/rejected)
- Order types: market, limit, stop
- Validation in `clean()` method:
  - Quantity must be > 0
  - Limit/stop orders require price
  - Buy orders check sufficient funds
- Fields: `quantity`, `price`, `status`, `rejection_reason`

### 2. Services (`apps/backend/src/trading/services/`)

#### PaperTradingEngine (`paper_trading_engine.py`)
- **Key Methods to Audit:**
  - `execute_market_order()` - Line 58
  - `execute_limit_order()` - Line 155
  - `cancel_order()` - Line 185
  - `calculate_portfolio_value()` - Line 197
  - `reset_portfolio()` - Line 235

- **Transaction Safety:**
  - All order executions wrapped in `@transaction.atomic`
  - Prevents data races on cash/position updates

- **Input Validation:**
  - Asset existence checks
  - Price availability checks
  - Sufficient funds validation
  - Position availability validation

- **WebSocket Broadcasting:**
  - `WebSocketBroadcaster` class handles real-time updates
  - Channel layer group names based on user_id
  - Potential broadcast security: only broadcasts to user's group

### 3. WebSocket Consumer (`apps/backend/src/trading/consumers/`)

#### PaperTradingConsumer (`paper_trading.py`)
- **Authentication:** Checks `scope["user"].is_anonymous`
- **Group Management:** User-specific groups (`paper_trading_{user_id}`)
- **Event Types:** `portfolio_update`, `order_update`, `position_update`

**Security Concerns:**
- WebSocket connection validation
- User isolation in group broadcasting

### 4. API Endpoints (`apps/backend/src/trading/api/`)

#### Authentication
- All endpoints use `JWTAuth()` authentication
- User isolation: `portfolio__user_id=request.user.id`

#### Key Endpoints to Audit
- `POST /api/paper-trading/orders/market` - Order execution
- `POST /api/paper-trading/orders/limit` - Limit orders
- `POST /api/paper-trading/orders/{id}/cancel` - Order cancellation
- `POST /api/paper-trading/portfolio/reset` - Portfolio reset

### 5. Database (`apps/backend/src/trading/migrations/`)

#### Migration 0003
- Creates `paper_trading_positions` table
- Creates `paper_trading_orders` table
- Adds indexes for query optimization
- Unique constraint on `(portfolio, asset)` for positions

---

## Security Checklist

### Authentication & Authorization
- [ ] JWT authentication on all endpoints
- [ ] User isolation on all queries
- [ ] WebSocket connection authentication
- [ ] No bypass of auth middleware

### Input Validation
- [ ] Order quantity validation (must be > 0)
- [ ] Price validation for limit/stop orders
- [ ] Asset existence checks
- [ ] No SQL injection (ORM usage)
- [ ] No XSS in error messages

### Data Integrity
- [ ] Atomic transactions for order execution
- [ ] Race condition prevention on cash updates
- [ ] Position quantity calculations correct
- [ ] No negative balances possible

### WebSocket Security
- [ ] Anonymous user rejection
- [ ] User-specific message groups
- [ ] No sensitive data in broadcasts

### Error Handling
- [ ] No sensitive info in error responses
- [ ] Graceful degradation
- [ ] No information leakage

---

## Files Changed

```
apps/backend/src/trading/models/paper_position.py     (NEW)
apps/backend/src/trading/models/paper_order.py        (NEW)
apps/backend/src/trading/services/paper_trading_engine.py  (NEW)
apps/backend/src/trading/consumers/paper_trading.py   (NEW)
apps/backend/src/trading/api/paper_trading.py         (MODIFIED)
apps/backend/src/trading/migrations/0003_add_paper_trading_models.py  (NEW)
apps/backend/src/trading/tests/test_paper_trading.py  (NEW)
```

---

## Testing Notes

- Unit tests created at `apps/backend/src/trading/tests/test_paper_trading.py`
- Tests cover: models, engine methods, validation, order lifecycle
- Integration tests recommended for full API testing

---

## Known Limitations

1. **Limit Order Execution:** Currently limit orders are created but require a background task to check and execute them (not implemented yet)
2. **Stop Orders:** Stop order trigger logic not implemented
3. **Historical Performance:** Performance history tracking not yet implemented

---

## Questions for Security Audit

1. WebSocket authentication best practices?
2. Rate limiting recommendations?
3. Any additional input sanitization needed?
4. Best practices for handling decimal precision in financial calculations?

---

**Review Status:** 🔴 Pending Charo Audit
**Branch:** `feature/c-036-paper-trading-frontend`
**PR URL:** https://github.com/Fuuurma/FinanceHub/pull/new/feature/c-036-paper-trading-frontend
