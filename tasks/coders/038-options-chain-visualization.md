# Task C-038: Options Chain Visualization

**Priority:** P1 HIGH  
**Estimated Time:** 16-20 hours  
**Assigned To:** Backend Coder + Frontend Coder  
**Status:** PENDING

## Overview
Implement a comprehensive options chain visualization tool with implied volatility skew, Greeks display, and options analytics for traders.

## User Story
As an options trader, I want to view and analyze complete options chains with IV skew and Greeks so I can make informed options trading decisions.

## Acceptance Criteria

### Backend (10-12 hours)
- [ ] **Options Data Model**
  - OptionContract model - Store individual option contracts
  - OptionsChain model - Grouped options by expiration
  - ImpliedVolatility model - IV surface data
  - Greeks model - Calculated Greeks values

- [ ] **Options Data Provider**
  - Fetch options chains from Yahoo Finance API
  - Fetch from Interactive Brokers (if available)
  - Fetch from TD Ameritrade (if available)
  - Cache options data (expirations change daily)
  - Update Greeks in real-time

- [ ] **Greeks Calculator**
  - Calculate Delta, Gamma, Theta, Vega, Rho
  - Use Black-Scholes model
  - Calculate Implied Volatility
  - Calculate historical volatility
  - Calculate probability of ITM

- [ ] **Options Analytics**
  - Calculate IV rank (percentile over 1 year)
  - Calculate IV percentile
  - Calculate IV skew (smile curve)
  - Calculate put/call ratio
  - Calculate max pain price
  - Calculate expected move

- [ ] **API Endpoints**
  - `GET /api/options/{symbol}/chain` - Get full options chain
  - `GET /api/options/{symbol}/expirations` - Get expiration dates
  - `GET /api/options/{symbol}/strikes/{expiration}` - Get strikes for date
  - `GET /api/options/{symbol}/iv-skew` - Get IV skew data
  - `GET /api/options/{symbol}/greeks` - Get Greeks snapshot
  - `GET /api/options/{symbol}/analytics` - Get options analytics

### Frontend (6-8 hours)
- [ ] **Options Chain Table**
  - Display calls and puts side-by-side
  - Columns: Strike, Last, Change, Bid, Ask, Volume, OI, IV
  - Greeks columns: Delta, Gamma, Theta, Vega
  - Color coding: ITM/OTM highlighting
  - Sortable columns
  - Filter by strike range, delta range

- [ ] **IV Skew Chart**
  - Line chart showing IV vs strike price
  - Plot calls and puts separately
  - Show smile or skew shape
  - Highlight current spot price
  - Historical IV skew comparison

- [ ] **Options Analytics Dashboard**
  - Display IV rank and percentile
  - Display put/call ratio
  - Display max pain price
  - Display expected move (with confidence intervals)
  - 30-day HV vs IV comparison
  - Historical IV chart

- [ ] **Options Detail Page**
  - `/options/{symbol}` route
  - Expiration date selector
  - Strikes filter
  - Quick view: ITM, OTM, Near-the-Money
  - Greeks calculator
  - Strategy builder (vertical spreads, iron condors, etc.)

- [ ] **Options Strategy Tool**
  - Build options strategies visually
  - Single leg, vertical spread, iron condor, butterfly
  - Show P&L diagram
  - Show breakeven points
  - Show max profit/loss
  - Show Greeks for the entire position

## Technical Requirements

### Backend
- **Files to Create:**
  - `apps/backend/src/options/models/option_contract.py`
  - `apps/backend/src/options/providers/yahoo_options.py`
  - `apps/backend/src/options/services/greeks_calculator.py`
  - `apps/backend/src/options/services/options_analytics.py`
  - `apps/backend/src/options/api/options.py`

- **Database Schema:**
  ```python
  class OptionContract(UUIDModel, TimestampedModel):
      underlying_asset = ForeignKey(Asset, on_delete=CASCADE)
      option_type = CharField(choices=[('CALL', 'Call'), ('PUT', 'Put')])
      strike_price = DecimalField(max_digits=12, decimal_places=2)
      expiration_date = DateField()
      last_price = DecimalField(max_digits=12, decimal_places=2)
      bid = DecimalField(max_digits=12, decimal_places=2)
      ask = DecimalField(max_digits=12, decimal_places=2)
      volume = BigIntegerField()
      open_interest = BigIntegerField()
      implied_volatility = FloatField()
      delta = FloatField(null=True)
      gamma = FloatField(null=True)
      theta = FloatField(null=True)
      vega = FloatField(null=True)
      rho = FloatField(null=True)
      
  class OptionsChain(UUIDModel):
      asset = ForeignKey(Asset, on_delete=CASCADE)
      snapshot_date = DateTimeField(auto_now_add=True)
      spot_price = DecimalField(max_digits=12, decimal_places=2)
      iv_rank = FloatField()
      iv_percentile = FloatField()
      put_call_ratio = FloatField()
      max_pain_price = DecimalField(max_digits=12, decimal_places=2)
  ```

- **Libraries:**
  - `yfinance` - Options data from Yahoo Finance
  - `scipy` - Black-Scholes calculation
  - `numpy` - Numerical calculations
  - `pandas` - Data manipulation

- **Greeks Calculation (Black-Scholes):**
  ```python
  def calculate_greeks(S, K, T, r, sigma, option_type):
      # S: Spot price
      # K: Strike price
      # T: Time to expiration (years)
      # r: Risk-free rate
      # sigma: Implied volatility
      # Returns: delta, gamma, theta, vega, rho
  ```

### Frontend
- **Files to Create:**
  - `apps/frontend/src/app/(dashboard)/options/[symbol]/page.tsx`
  - `apps/frontend/src/components/options/OptionsChainTable.tsx`
  - `apps/frontend/src/components/options/IVSkewChart.tsx`
  - `apps/frontend/src/components/options/OptionsAnalytics.tsx`
  - `apps/frontend/src/components/options/StrategyBuilder.tsx`
  - `apps/frontend/src/lib/api/options.ts`

- **UI Components:**
  - Use TanStack Table for options chain
  - Use Recharts for IV skew chart
  - Use existing PriceDisplay component
  - Filter controls (range sliders, dropdowns)

- **State Management:**
  - `optionsStore.ts` for options state
  - React Query for data fetching
  - Real-time updates (polling every 10 seconds)

## Dependencies
- **Prerequisites:** C-001 (User System), C-002 (Asset Management), C-005 (Portfolio Core)
- **Related Tasks:** C-023 (Options Greeks Calculator)
- **External APIs:** Yahoo Finance (free), Interactive Brokers (optional)

## Testing Requirements
- **Backend:**
  - Test options chain data fetching
  - Test Greeks calculation accuracy
  - Test IV skew calculation
  - Test options analytics calculations
  - Test API response times

- **Frontend:**
  - Test options chain table rendering
  - Test sorting and filtering
  - Test IV skew chart display
  - Test strategy builder
  - Test responsive design

## Performance Considerations
- Cache options chains (15-minute TTL)
- Use database indexes on (underlying, expiration, strike)
- Limit to 50 strikes around spot price
- Pagination for large options chains
- Compress options data in API responses

## Success Metrics
- Options chains load in < 2 seconds
- Greeks calculations are accurate
- IV skew chart renders smoothly
- Users can build options strategies
- Traders find options tool valuable

## Notes
- Options data is complex, start with basic chain
- Greeks are computationally expensive, cache them
- IV skew is a powerful leading indicator
- Consider adding "unusual options activity" scanner
- Consider adding "options flow" (large block trades)
- Yahoo Finance API is free but has rate limits
- For production, consider paid data provider (Polygon.io, Intrinio)

## Future Enhancements
- Options backtesting
- Options profit calculator
- Options probability calculator
- Options earnings plays
- Options volatility surface (3D visualization)
- Options flow scanner (whales activity)
