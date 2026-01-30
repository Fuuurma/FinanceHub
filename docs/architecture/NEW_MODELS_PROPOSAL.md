# FinanceHub New Model Proposals

**Date:** January 30, 2026  
**Status:** PROPOSAL  
**Purpose:** Identify gaps and propose new models

---

## Current Models Summary

| Module | Models | Status |
|--------|--------|--------|
| ai_advisor | 1 | OK |
| assets | 10 | Missing: AssetCorrelation, MarketIndex |
| charts | 1 | OK |
| investments | 20 | Missing: ScreenerCriteria, PriceTarget |
| portfolios | 4 | Missing: TaxLot, RebalancingRule |
| trading | 2 | Missing: Trade, OrderExecution |
| users | 9 | Missing: LearningProgress, UserPreferences |

---

## Priority 1: Portfolio Management

### 1. TaxLot (P1)
Track tax lots for holdings (FIFO, LIFO, Specific ID).

### 1.2 RebalancingRule (P1)
Automated rebalancing strategies.

### 1.3 PortfolioAllocation (P1)
Target asset allocation and drift tracking.

### 1.4 PaperPortfolio (P2)
Enhanced paper trading simulation.

---

## Priority 2: Trading

### 2.1 Trade (P1)
Detailed trade records beyond transactions.

### 2.2 OrderExecution (P1)
Track partial fills and execution details.

### 2.3 PnLRecord (P2)
Profit and loss tracking at multiple levels.

---

## Priority 3: Market Data

### 3.1 ScreenerCriteria (P2)
Custom stock screener criteria.

### 3.2 MarketIndex (P2)
S&P 500, Dow Jones, etc.

### 3.3 PriceTarget (P3)
Analyst price targets.

### 3.4 MarketSentiment (P3)
Daily market sentiment scores.

---

## Priority 4: User Features

### 4.1 UserPreferences (P3)
Comprehensive user settings.

### 4.2 LearningProgress (P3)
Track user education progress.

---

## Files to Create

1. `portfolios/models/tax_lot.py`
2. `portfolios/models/rebalancing_rule.py`
3. `trading/models/trade.py`
4. `trading/models/order_execution.py`
5. `investments/models/screener_criteria.py`
6. `users/models/user_preferences.py`
