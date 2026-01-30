# Task C-039: Multi-Currency Portfolio Support

**Priority:** P2 MEDIUM  
**Estimated Time:** 14-18 hours  
**Assigned To:** Backend Coder + Frontend Coder  
**Status:** PENDING

## Overview
Implement multi-currency portfolio support allowing users to hold assets in different currencies (USD, EUR, GBP, JPY, etc.) with automatic currency conversion and FX rate tracking.

## User Story
As a global investor, I want to hold assets in multiple currencies so I can diversify currency risk and invest in international markets.

## Acceptance Criteria

### Backend (10-12 hours)
- [ ] **Currency Model**
  - Currency model - Supported currencies (USD, EUR, GBP, JPY, CAD, AUD, CHF, etc.)
  - ExchangeRate model - Historical and real-time FX rates
  - CurrencyPreference model - User's base currency preference
  - FXPosition model - Track currency exposures

- [ ] **FX Data Provider**
  - Fetch FX rates from Yahoo Finance
  - Fetch from exchangerate-api.com
  - Support 20+ major currencies
  - Real-time rate updates
  - Historical FX rates (for P&L calculation)

- [ ] **Currency Conversion Service**
  - Convert amount between any two currencies
  - Use real-time FX rates
  - Cache rates for 5 minutes
  - Handle inverse pairs (EUR/USD vs USD/EUR)
  - Calculate cross rates (EUR/GBP via EUR/USD and USD/GBP)

- [ ] **Portfolio Currency Support**
  - Track asset currency in Position model
  - Calculate portfolio value in base currency
  - Calculate currency P&L (FX gain/loss)
  - Calculate currency allocation breakdown
  - Calculate currency hedging requirements

- [ ] **Multi-Currency Analytics**
  - Currency allocation pie chart
  - Currency exposure table
  - FX gain/loss calculation
  - Currency contribution to portfolio return
  - Currency risk metrics (volatility, VaR by currency)

- [ ] **API Endpoints**
  - `GET /api/fx/rates` - Get all current FX rates
  - `GET /api/fx/convert` - Convert amount between currencies
  - `GET /api/fx/rates/{pair}/history` - Historical FX rates
  - `GET /api/portfolio/currency-allocation` - Currency breakdown
  - `GET /api/portfolio/currency-pnl` - FX P&L
  - `PUT /api/settings/base-currency` - Set base currency

### Frontend (4-6 hours)
- [ ] **Currency Selector Component**
  - Dropdown to select currency (USD, EUR, GBP, etc.)
  - Flag icons for each currency
  - Display current FX rate
  - Show last update time

- [ ] **Portfolio Currency Dashboard**
  - Currency allocation pie chart
  - Currency exposure table (position, P&L, %)
  - FX gain/loss summary
  - Base currency selector in settings

- [ ] **Asset Detail Currency Display**
  - Show asset price in native currency
  - Show converted price in base currency
  - Display current FX rate
  - Show FX rate chart (30-day history)

- [ ] **Settings - Base Currency**
  - User can select default/base currency
  - All portfolio values display in base currency
  - All analytics calculated in base currency
  - Currency switcher on dashboard

- [ ] **FX Rate Converter Tool**
  - Quick converter tool
  - Input amount, select from/to currency
  - Show conversion result
  - Show historical rate chart
  - Link to FX analysis

## Technical Requirements

### Backend
- **Files to Create:**
  - `apps/backend/src/fx/models/currency.py`
  - `apps/backend/src/fx/providers/fx_provider.py`
  - `apps/backend/src/fx/services/currency_converter.py`
  - `apps/backend/src/fx/api/fx.py`
  - `apps/backend/src/portfolio/services/currency_analytics.py`

- **Database Schema:**
  ```python
  class Currency(UUIDModel, TimestampedModel):
      code = CharField(max_length=3, unique=True)  # USD, EUR, GBP
      name = CharField(max_length=50)  # US Dollar, Euro, British Pound
      symbol = CharField(max_length=5)  # $, €, £
      is_active = BooleanField(default=True)
      
  class ExchangeRate(UUIDModel, TimestampedModel):
      from_currency = ForeignKey(Currency, related_name='rates_from')
      to_currency = ForeignKey(Currency, related_name='rates_to')
      rate = DecimalField(max_digits=18, decimal_places=8)
      fetched_at = DateTimeField(auto_now_add=True)
      
  class CurrencyPreference(UUIDModel):
      user = OneToOneField(User, on_delete=CASCADE)
      base_currency = ForeignKey(Currency, on_delete=PROTECT)
      auto_convert = BooleanField(default=True)
  ```

- **FX Data Sources:**
  - Yahoo Finance (free, reliable)
  - exchangerate-api.com (free tier: 1,500 requests/month)
  - Fixer.io (paid)
  - CurrencyLayer (paid)

- **Supported Currencies:**
  - USD (US Dollar)
  - EUR (Euro)
  - GBP (British Pound)
  - JPY (Japanese Yen)
  - CAD (Canadian Dollar)
  - AUD (Australian Dollar)
  - CHF (Swiss Franc)
  - CNY (Chinese Yuan)
  - INR (Indian Rupee)
  - + 10 more popular currencies

### Frontend
- **Files to Create:**
  - `apps/frontend/src/components/fx/CurrencySelector.tsx`
  - `apps/frontend/src/components/fx/FXConverter.tsx`
  - `apps/frontend/src/components/fx/CurrencyAllocation.tsx`
  - `apps/frontend/src/components/fx/FXRatesChart.tsx`
  - `apps/frontend/src/lib/api/fx.ts`

- **Currency Formatting:**
  - Use `Intl.NumberFormat` for currency display
  - Format: $1,234.56, €1.234,56, £1,234.56
  - Handle currency symbols positioning
  - Handle decimal separators (US vs EU)

- **State Management:**
  - `fxStore.ts` for FX rates
  - `currencyStore.ts` for user currency preferences
  - React Query for FX data fetching

- **Visualizations:**
  - Currency allocation pie chart
  - FX rate line chart
  - Currency P&L bar chart
  - Use Recharts or Chart.js

## Dependencies
- **Prerequisites:** C-001 (User System), C-002 (Asset Management), C-005 (Portfolio Core)
- **Related Tasks:** C-011 (Portfolio Analytics), C-026 (VaR Calculator)
- **External APIs:** Yahoo Finance FX, exchangerate-api.com

## Testing Requirements
- **Backend:**
  - Test currency conversion accuracy
  - Test FX rate fetching
  - Test cross-rate calculation
  - Test portfolio currency allocation
  - Test FX P&L calculation

- **Frontend:**
  - Test currency selector
  - Test FX converter tool
  - Test currency allocation chart
  - Test base currency switching
  - Test currency formatting

## Performance Considerations
- Cache FX rates (5-minute TTL)
- Use Redis for hot currency pairs
- Batch FX rate requests
- Update FX rates every 5 minutes
- Archive historical FX rates older than 1 year

## Success Metrics
- FX rates update every 5 minutes
- Currency conversions are accurate
- Portfolio values display correctly in base currency
- Users can switch base currency
- Currency risk analysis is accurate

## Notes
- FX rates are relatively stable (update every 5 minutes is fine)
- Always display the native currency alongside converted price
- Consider adding currency hedging calculator
- Consider adding "currency overlay" strategies
- Consider adding FX alerts (rate threshold)
- For simplicity, assume base currency = user's home currency
- For production, consider professional FX data provider (OANDA, XE.com)

## Future Enhancements
- Cryptocurrency support as "currency"
- Forward rates and FX futures
- Currency options
- FX trading capabilities
- Currency volatility index
- Central bank interest rates
- Inflation-adjusted returns
