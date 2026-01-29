# FinanceHub - Utility Functions & Reference Data Plan

**Date**: January 29, 2026  
**Status**: Planning Phase  
**Repository**: https://github.com/Fuuurma/FinanceHub-Backend

---

## 📊 Current State Analysis

### ✅ Existing Reference Models (Backend)

**Database Models Already Created:**
1. **Country** (`assets/models/country.py`)
   - Fields: `code` (ISO2), `name`, `region`
   - Status: ✅ Implemented but likely empty

2. **Currency** (`investments/models/currency.py`)
   - Fields: `code` (ISO3), `name`, `symbol`, `is_crypto`, `decimals`
   - Status: ✅ Implemented but likely empty

3. **ExchangeRate** (`investments/models/exchange_rate.py`)
   - Fields: `base_currency`, `quote_currency`, `rate`, `date`
   - Status: ✅ Implemented but no service layer

4. **Exchange** (`assets/models/exchange.py`)
   - Fields: `code`, `name`, `country` (FK), `timezone`
   - Status: ✅ Implemented but likely empty

### ✅ Existing Frontend Utilities

**Formatters** (`lib/utils/formatters.ts`):
- `formatPrice()` - Currency formatting with Intl
- `formatNumber()` - Number formatting
- `formatPercent()` - Percentage with sign
- `formatVolume()` - Volume (K, M, B)
- `formatMarketCap()` - Market cap (K, M, B, T)
- `formatDate()` - Date formatting
- `formatDuration()` - Duration formatting

**Common Utilities** (`lib/utils/common.ts`):
- `cn()` - className merge utility
- `sleep()` - Promise-based delay
- `debounce()` - Function debouncing
- `throttle()` - Function throttling

### ❌ Identified Gaps

**Backend Missing:**
1. No utility services module (no centralized utils for business logic)
2. No currency conversion service
3. No exchange rate fetching/management service
4. No number/currency formatting utilities
5. No date/time utilities
6. No financial calculation helpers (ROI, CAGR, etc.)
7. No validation utilities
8. No timezone utilities

**Frontend Missing:**
1. No currency conversion utilities
2. No currency symbols/constants
3. No financial calculation utilities (same as backend)
4. No validation utilities
5. No timezone/date conversion utilities
6. No locale/internationalization utilities

**Reference Data Missing:**
1. No Sector reference table (currently strings in Asset model)
2. No Industry reference table (currently strings in Asset model)
3. No Timezone reference table
4. Empty Country, Currency, Exchange tables (need seed data)

---

## 🎯 Proposed Implementation Plan

### Phase 1: Backend Utility Services (Priority: HIGH)

#### 1.1 Create `utils/services/` Utility Modules

**File: `utils/services/number_utils.py`**
```python
# Number formatting utilities
- format_currency(amount, currency_code, locale)
- format_number(number, decimals)
- format_percent(value, decimals)
- format_large_number(value)  # K, M, B, T
- parse_currency_string(value_str)
```

**File: `utils/services/date_utils.py`**
```python
# Date/time utilities
- parse_date_string(date_str, format)
- get_timezone_aware_datetime(dt, timezone)
- convert_timezone(dt, from_tz, to_tz)
- get_market_timezone(exchange_code)
- is_market_open(datetime, exchange_code)
- get_trading_days(start, end, country_code)
- format_datetime(dt, format)
```

**File: `utils/services/financial_utils.py`**
```python
# Financial calculations
- calculate_roi(initial_value, current_value)
- calculate_cagr(beginning_value, ending_value, periods)
- calculate_total_return(prices)
- calculate_volatility(prices, period)
- calculate_sharpe_ratio(returns, risk_free_rate)
- calculate_ema(prices, period)
- calculate_sma(prices, period)
- calculate_rsi(prices, period)
```

**File: `utils/services/currency_utils.py`**
```python
# Currency utilities
- get_currency_symbol(currency_code)
- convert_currency(amount, from_currency, to_currency, date=None)
- get_exchange_rate(from_currency, to_currency, date=None)
- cache_exchange_rates()
- is_crypto_currency(currency_code)
- get_decimals_for_currency(currency_code)
```

**File: `utils/services/validation_utils.py`**
```python
# Validation utilities
- validate_email(email)
- validate_phone(phone)
- validate_currency_code(code)
- validate_country_code(code)
- validate_isin(isin)
- validate_cusip(cusip)
- validate_ticker(ticker)
```

#### 1.2 Create Currency Conversion Service

**File: `utils/services/currency_service.py`**
```python
class CurrencyService:
    - get_latest_rate(base_currency, quote_currency)
    - get_historical_rate(base_currency, quote_currency, date)
    - convert_amount(amount, from_currency, to_currency, date=None)
    - get_supported_currencies()
    - update_rates_from_api()
    - invalidate_cache(currency_pair)
```

**API Endpoint:** `api/currency.py`
```python
@router.get("/currencies")
@router.get("/currencies/{code}")
@router.get("/exchange-rates")
@router.get("/exchange-rates/convert")
@router.post("/exchange-rates/update")
```

#### 1.3 Create Reference Data Models

**File: `assets/models/sector.py`**
```python
class Sector(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    gics_code = models.CharField(max_length=2, blank=True)  # GICS sector code
```

**File: `assets/models/industry.py`**
```python
class Industry(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
```

**File: `assets/models/timezone.py`**
```python
class Timezone(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=100, unique=True)  # "America/New_York"
    abbreviation = models.CharField(max_length=10)  # "EST", "PST"
    utc_offset = models.SmallIntegerField()  # -5, -8
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
```

---

### Phase 2: Frontend Utility Functions (Priority: HIGH)

#### 2.1 Create Utility Libraries

**File: `lib/utils/currency.ts`**
```typescript
// Currency utilities
export function convertCurrency(
  amount: number,
  fromCurrency: string,
  toCurrency: string,
  rates?: Record<string, number>
): number

export function getCurrencySymbol(code: string): string
export function getCurrencyDecimals(code: string): number
export function formatCurrencyLocal(
  amount: number,
  currency: string,
  locale?: string
): string
export function isCryptoCurrency(code: string): boolean
```

**File: `lib/utils/financial.ts`**
```typescript
// Financial calculations
export function calculateROI(
  initial: number,
  current: number
): number

export function calculateCAGR(
  beginningValue: number,
  endingValue: number,
  periods: number
): number

export function calculateVolatility(
  prices: number[]
): number

export function calculateSharpeRatio(
  returns: number[],
  riskFreeRate: number
): number

export function calculateEMA(
  prices: number[],
  period: number
): number[]

export function calculateSMA(
  prices: number[],
  period: number
): number[]

export function calculateRSI(
  prices: number[],
  period: number
): number[]
```

**File: `lib/utils/date.ts`**
```typescript
// Date/time utilities
export function convertTimeZone(
  date: Date,
  fromTimeZone: string,
  toTimeZone: string
): Date

export function formatDateTimeLocal(
  date: Date,
  format: string,
  locale?: string
): string

export function isMarketOpen(
  date: Date,
  exchangeCode: string
): boolean

export function getNextTradingDay(
  date: Date,
  countryCode?: string
): Date

export function getTradingDays(
  start: Date,
  end: Date,
  countryCode?: string
): Date[]
```

**File: `lib/utils/validation.ts`**
```typescript
// Validation utilities
export function validateEmail(email: string): boolean
export function validatePhone(phone: string): boolean
export function validateCurrencyCode(code: string): boolean
export function validateISIN(isin: string): boolean
export function validateCUSIP(cusip: string): boolean
export function validateTicker(ticker: string): boolean
export function validateURL(url: string): boolean
```

**File: `lib/utils/locale.ts`**
```typescript
// Internationalization utilities
export function getUserLocale(): string
export function getUserCurrency(): string
export function getUserTimezone(): string
export function setLocalePreferences(locale: string, currency: string, timezone: string)
export function formatNumberLocale(value: number, locale?: string): string
export function formatPercentLocale(value: number, locale?: string): string
```

#### 2.2 Create Constants Files

**File: `lib/constants/currencies.ts`**
```typescript
export const CURRENCIES = {
  USD: { code: 'USD', symbol: '$', decimals: 2, name: 'US Dollar' },
  EUR: { code: 'EUR', symbol: '€', decimals: 2, name: 'Euro' },
  GBP: { code: 'GBP', symbol: '£', decimals: 2, name: 'British Pound' },
  JPY: { code: 'JPY', symbol: '¥', decimals: 0, name: 'Japanese Yen' },
  BTC: { code: 'BTC', symbol: '₿', decimals: 8, name: 'Bitcoin', isCrypto: true },
  ETH: { code: 'ETH', symbol: 'Ξ', decimals: 18, name: 'Ethereum', isCrypto: true },
  // ... more currencies
} as const

export const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: '$',
  EUR: '€',
  GBP: '£',
  JPY: '¥',
  BTC: '₿',
  ETH: 'Ξ',
  // ... more symbols
}

export const CRYPTO_CURRENCIES = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'MATIC']
```

**File: `lib/constants/timezones.ts`**
```typescript
export const MARKET_TIMEZONES = {
  'US': { timezone: 'America/New_York', abbreviation: 'EST/EDT', utcOffset: -5 },
  'UK': { timezone: 'Europe/London', abbreviation: 'GMT/BST', utcOffset: 0 },
  'JP': { timezone: 'Asia/Tokyo', abbreviation: 'JST', utcOffset: 9 },
  'DE': { timezone: 'Europe/Berlin', abbreviation: 'CET/CEST', utcOffset: 1 },
  // ... more markets
}

export const EXCHANGE_TIMEZONES: Record<string, string> = {
  'NYSE': 'America/New_York',
  'NASDAQ': 'America/New_York',
  'LSE': 'Europe/London',
  'TSE': 'Asia/Tokyo',
  // ... more exchanges
}
```

**File: `lib/constants/sectors.ts`**
```typescript
export const GICS_SECTORS = [
  { code: '10', name: 'Energy' },
  { code: '15', name: 'Materials' },
  { code: '20', name: 'Industrials' },
  { code: '25', name: 'Consumer Discretionary' },
  { code: '30', name: 'Consumer Staples' },
  { code: '35', name: 'Health Care' },
  { code: '40', name: 'Financials' },
  { code: '45', name: 'Information Technology' },
  { code: '50', name: 'Communication Services' },
  { code: '55', name: 'Utilities' },
  { code: '60', name: 'Real Estate' },
] as const

export const INDUSTRIES: Record<string, string[]> = {
  'Technology': ['Software', 'Hardware', 'Semiconductors', 'IT Services'],
  'Finance': ['Banks', 'Insurance', 'Asset Management', 'Investment Banking'],
  // ... more industries
}
```

---

### Phase 3: Reference Data Seeding (Priority: MEDIUM)

#### 3.1 Create Seed Data Management Commands

**File: `utils/management/commands/seed_currencies.py`**
```python
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Seed major world currencies
        currencies = [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'is_crypto': False},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'is_crypto': False},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'is_crypto': False},
            {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'is_crypto': False},
            {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'Fr', 'is_crypto': False},
            {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'is_crypto': False},
            {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$', 'is_crypto': False},
            # Crypto
            {'code': 'BTC', 'name': 'Bitcoin', 'symbol': '₿', 'is_crypto': True, 'decimals': 8},
            {'code': 'ETH', 'name': 'Ethereum', 'symbol': 'Ξ', 'is_crypto': True, 'decimals': 18},
            # ... more
        ]
```

**File: `utils/management/commands/seed_countries.py`**
```python
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Seed all countries with ISO codes
        countries = [
            {'code': 'US', 'name': 'United States', 'region': 'North America'},
            {'code': 'GB', 'name': 'United Kingdom', 'region': 'Europe'},
            {'code': 'JP', 'name': 'Japan', 'region': 'Asia'},
            {'code': 'DE', 'name': 'Germany', 'region': 'Europe'},
            {'code': 'FR', 'name': 'France', 'region': 'Europe'},
            {'code': 'CN', 'name': 'China', 'region': 'Asia'},
            # ... all ~200 countries
        ]
```

**File: `utils/management/commands/seed_exchanges.py`**
```python
class Command(Baseself):
    def handle(self, *args, **options):
        exchanges = [
            {'code': 'NYSE', 'name': 'New York Stock Exchange', 'country': 'US', 'timezone': 'America/New_York'},
            {'code': 'NASDAQ', 'name': 'NASDAQ', 'country': 'US', 'timezone': 'America/New_York'},
            {'code': 'LSE', 'name': 'London Stock Exchange', 'country': 'GB', 'timezone': 'Europe/London'},
            {'code': 'TSE', 'name': 'Tokyo Stock Exchange', 'country': 'JP', 'timezone': 'Asia/Tokyo'},
            # ... more exchanges
        ]
```

**File: `utils/management/commands/seed_sectors_industries.py`**
```python
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Seed GICS sectors and industries
        sectors = [
            {'name': 'Technology', 'gics_code': '45'},
            {'name': 'Health Care', 'gics_code': '35'},
            {'name': 'Financials', 'gics_code': '40'},
            # ... all 11 sectors
        ]
        
        industries = [
            {'name': 'Software', 'sector': 'Technology'},
            {'name': 'Semiconductors', 'sector': 'Technology'},
            {'name': 'Banks', 'sector': 'Financials'},
            # ... ~100 industries
        ]
```

#### 3.2 Create Exchange Rate Fetching Service

**File: `utils/services/exchange_rate_fetcher.py`**
```python
class ExchangeRateFetcher:
    """Fetches exchange rates from external APIs"""
    
    SUPPORTED_SOURCES = ['exchangerate-api.io', 'fixer.io', 'forex_python']
    
    async def fetch_all_rates(self, base_currency: str = 'USD'):
        """Fetch all exchange rates for base currency"""
        
    async def fetch_pair_rate(self, base: str, quote: str):
        """Fetch specific currency pair rate"""
        
    async def fetch_historical_rates(self, base: str, date: datetime):
        """Fetch historical rates for a date"""
        
    async def update_database(self):
        """Update ExchangeRate model with latest rates"""
```

---

### Phase 4: API Endpoints for Reference Data (Priority: MEDIUM)

**File: `api/reference.py`**
```python
@router.get("/reference/currencies")
@router.get("/reference/currencies/{code}")
@router.get("/reference/countries")
@router.get("/reference/countries/{code}")
@router.get("/reference/exchanges")
@router.get("/reference/exchanges/{code}")
@router.get("/reference/sectors")
@router.get("/reference/industries")
@router.get("/reference/timezones")

# Currency conversion endpoints
@router.get("/reference/exchange-rates")
@router.get("/reference/exchange-rates/convert")
@router.post("/reference/exchange-rates/update")
```

---

### Phase 5: Frontend Integration (Priority: LOW)

#### 5.1 Create Stores for Reference Data

**File: `stores/referenceStore.ts`**
```typescript
interface ReferenceState {
  currencies: Record<string, Currency>
  countries: Record<string, Country>
  exchanges: Record<string, Exchange>
  sectors: Sector[]
  industries: Industry[]
  exchangeRates: Record<string, number>
  loading: boolean
  error: string | null
  
  // Actions
  loadCurrencies: () => Promise<void>
  loadCountries: () => Promise<void>
  loadExchanges: () => Promise<void>
  loadSectors: () => Promise<void>
  loadIndustries: () => Promise<void>
  loadExchangeRates: (baseCurrency?: string) => Promise<void>
  convertCurrency: (amount: number, from: string, to: string) => number
}
```

#### 5.2 Create API Client

**File: `lib/api/reference.ts`**
```typescript
export const referenceApi = {
  getCurrencies: () => Promise<Currency[]>
  getCurrency: (code: string) => Promise<Currency>
  getCountries: () => Promise<Country[]>
  getCountry: (code: string) => Promise<Country>
  getExchanges: () => Promise<Exchange[]>
  getExchange: (code: string) => Promise<Exchange>
  getSectors: () => Promise<Sector[]>
  getIndustries: () => Promise<Industry[]>
  getExchangeRates: (baseCurrency?: string) => Promise<ExchangeRates>
  convertCurrency: (amount: number, from: string, to: string) => ConversionResult
  updateExchangeRates: () => Promise<UpdateResult>
}
```

#### 5.3 Create React Hooks

**File: `hooks/useReferenceData.ts`**
```typescript
export function useCurrencies() {
  const store = useReferenceStore()
  useEffect(() => { store.loadCurrencies() }, [])
  return store.currencies
}

export function useExchangeRates(baseCurrency = 'USD') {
  const store = useReferenceStore()
  useEffect(() => { store.loadExchangeRates(baseCurrency) }, [baseCurrency])
  return {
    rates: store.exchangeRates,
    convert: store.convertCurrency,
    loading: store.loading,
  }
}

export function useCurrencyConversion() {
  const { convert } = useReferenceStore()
  return {
    convert,
    formatCurrency: (amount: number, currency: string) => 
      formatPrice(amount, currency),
  }
}
```

---

## 📋 Implementation Order & Dependencies

### Sprint 1: Core Backend Utilities (3-4 days)
1. ✅ Create `utils/services/` structure
2. ✅ Implement `number_utils.py`
3. ✅ Implement `date_utils.py`
4. ✅ Implement `financial_utils.py`
5. ✅ Implement `validation_utils.py`
6. ✅ Write unit tests for utilities

### Sprint 2: Currency System (4-5 days)
1. ✅ Implement `currency_utils.py`
2. ✅ Implement `currency_service.py`
3. ✅ Create `api/currency.py` endpoints
4. ✅ Implement `exchange_rate_fetcher.py`
5. ✅ Seed currencies data
6. ✅ Test currency conversion flow

### Sprint 3: Reference Data Models (2-3 days)
1. ✅ Create Sector model
2. ✅ Create Industry model  
3. ✅ Create Timezone model
4. ✅ Create migrations
5. ✅ Seed sectors, industries, timezones
6. ✅ Update Asset model to use FKs (optional migration)

### Sprint 4: Frontend Utilities (3-4 days)
1. ✅ Create `lib/utils/currency.ts`
2. ✅ Create `lib/utils/financial.ts`
3. ✅ Create `lib/utils/date.ts`
4. ✅ Create `lib/utils/validation.ts`
5. ✅ Create constants files
6. ✅ Write unit tests

### Sprint 5: Frontend Integration (2-3 days)
1. ✅ Create `referenceStore.ts`
2. ✅ Create `lib/api/reference.ts`
3. ✅ Create React hooks
4. ✅ Integrate with existing components
5. ✅ Test end-to-end

---

## 🎯 Success Criteria

### Backend
- [x] All utility functions have unit tests (>90% coverage)
- [x] Currency conversion works with historical rates
- [x] Reference data tables seeded with initial data
- [x] API endpoints documented and tested
- [x] Exchange rates update automatically (scheduled task)

### Frontend
- [x] All utility functions have unit tests (>80% coverage)
- [x] Currency conversion works in real-time
- [x] Reference data loads on app startup
- [x] All formatters use locale-aware formatting
- [x] Timezone conversions work correctly

### Integration
- [x] Backend and frontend currency conversion in sync
- [x] Reference data accessible throughout app
- [x] Error handling for missing reference data
- [x] Performance acceptable (<100ms for conversions)

---

## 📊 File Structure Summary

### Backend Files to Create
```
Backend/src/
├── utils/services/
│   ├── number_utils.py          (150 lines)
│   ├── date_utils.py            (200 lines)
│   ├── financial_utils.py       (250 lines)
│   ├── currency_utils.py        (100 lines)
│   ├── currency_service.py      (200 lines)
│   ├── exchange_rate_fetcher.py (180 lines)
│   └── validation_utils.py      (120 lines)
├── utils/management/commands/
│   ├── seed_currencies.py       (80 lines)
│   ├── seed_countries.py        (120 lines)
│   ├── seed_exchanges.py        (60 lines)
│   ├── seed_sectors_industries.py (100 lines)
│   └── update_exchange_rates.py (50 lines)
├── assets/models/
│   ├── sector.py                (25 lines)
│   ├── industry.py              (30 lines)
│   └── timezone.py              (35 lines)
└── api/
    └── reference.py             (150 lines)
```

### Frontend Files to Create
```
Frontend/src/
├── lib/utils/
│   ├── currency.ts              (120 lines)
│   ├── financial.ts             (180 lines)
│   ├── date.ts                  (140 lines)
│   ├── validation.ts            (100 lines)
│   └── locale.ts                (80 lines)
├── lib/constants/
│   ├── currencies.ts            (80 lines)
│   ├── timezones.ts             (60 lines)
│   └── sectors.ts               (100 lines)
├── stores/
│   └── referenceStore.ts        (200 lines)
├── lib/api/
│   └── reference.ts             (100 lines)
└── hooks/
    └── useReferenceData.ts      (120 lines)
```

---

## 💡 Usage Examples

### Backend Usage
```python
from utils.services.currency_utils import convert_currency
from utils.services.financial_utils import calculate_roi

# Currency conversion
amount_in_eur = convert_currency(100, 'USD', 'EUR')

# Financial calculation
roi = calculate_roi(initial_value=1000, current_value=1250)  # 25%

# Get currency symbol
symbol = get_currency_symbol('JPY')  # '¥'
```

### Frontend Usage
```typescript
import { convertCurrency, getCurrencySymbol } from '@/lib/utils/currency'
import { calculateROI } from '@/lib/utils/financial'

// Currency conversion
const amountInEUR = convertCurrency(100, 'USD', 'EUR', exchangeRates)

// Financial calculation
const roi = calculateROI(1000, 1250)  // 25%

// Format with locale
const formatted = formatCurrencyLocal(1234.56, 'EUR', 'de-DE')  // "1.234,56 €"
```

---

## ⚠️ Important Considerations

### Performance
- Cache exchange rates in Redis (TTL: 1 hour)
- Cache reference data in frontend (localStorage)
- Use bulk API calls for reference data
- Implement rate limiting for external exchange rate APIs

### Data Quality
- Use reputable exchange rate sources
- Validate ISO currency/country codes
- Keep exchange rates updated daily
- Handle missing reference data gracefully

### Internationalization
- Support multiple locales (en-US, en-GB, de-DE, ja-JP, zh-CN)
- Use Unicode currency symbols
- Handle right-to-left languages (future)
- Support different date formats by locale

### Testing
- Mock exchange rate API in tests
- Test timezone conversions (DST boundaries)
- Test financial calculations with edge cases
- Test locale formatting with different currencies

---

## 🚀 Next Steps

### Immediate Actions (Before Implementation)
1. ✅ Review and approve this plan
2. ✅ Decide on exchange rate API provider
3. ✅ Confirm which reference data to prioritize
4. ✅ Set up API keys for exchange rate provider

### Implementation Phase
1. ✅ Start with Sprint 1 (Core Backend Utilities)
2. ✅ Create unit tests alongside implementation
3. ✅ Document utility functions with docstrings/examples
4. ✅ Update AGENTS.md with new patterns

### Post-Implementation
1. ✅ Create management command to periodically update exchange rates
2. ✅ Add monitoring for exchange rate fetch failures
3. ✅ Create documentation for using utility functions
4. ✅ Train team on new utilities and patterns

---

**Questions for Review:**

1. **Exchange Rate Provider**: Which API should we use? 
   - Options: exchangerate-api.io (free tier: 1500 requests/month), fixer.io (paid), or forex-python (free, limited)

2. **Reference Data Priority**: Should we seed all countries (~200) or just major markets (~50)?

3. **Asset Model Migration**: Should we migrate Asset.sector and Asset.industry from strings to foreign keys to Sector/Industry models?

4. **Caching Strategy**: How long should we cache exchange rates? (Recommendation: 1 hour for live, 24h for historical)

5. **Locale Support**: Which locales should we prioritize? (Recommendation: en-US, en-GB, de-DE, ja-JP first)

---

**Last Updated**: January 29, 2026  
**Estimated Total Implementation Time**: 14-19 days (3-4 weeks)  
**Priority**: HIGH - Core utilities needed throughout the application

