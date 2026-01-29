# FinanceHub - Utility Functions & Reference Data
## FINAL IMPLEMENTATION PLAN

**Date**: January 29, 2026  
**Status**: Ready for Implementation  
**Total Estimated Time**: 14-19 days (3-4 weeks)

---

## ✅ User Decisions (Finalized)

1. **Exchange Rate Provider**: Use BOTH exchangerate-api.io AND forex-python
   - Primary: exchangerate-api.io (free tier: 1,500 requests/month)
   - Fallback: forex-python (free library, no API calls)

2. **Country Data**: Seed ALL ~200 countries

3. **Asset Model Migration**: YES - migrate Asset.sector and Asset.industry to FKs

4. **Cache Duration**: 4 hours (TTL: 14400 seconds)

5. **Locale Support**: en-US, en-GB, de-DE, ja-JP (4 major locales)

---

## 📋 Sprint 1: Backend Utility Services (Days 1-4)

### Day 1: Core Utilities Structure & Number Utils

**Files to Create:**

1. `Backend/src/utils/services/number_utils.py` (150 lines)
```python
"""
Number and currency formatting utilities
"""
import locale
from decimal import Decimal
from typing import Optional

def format_currency(
    amount: float,
    currency_code: str = 'USD',
    locale_str: str = 'en_US'
) -> str:
    """Format amount as currency with proper symbol and decimals"""
    # Implementation
    
def format_number(value: float, decimals: int = 2) -> str:
    """Format number with thousand separators"""
    
def format_percent(value: float, decimals: int = 2, show_sign: bool = True) -> str:
    """Format as percentage with optional sign"""
    
def format_large_number(value: float) -> str:
    """Format large numbers as K, M, B, T"""
    
def parse_currency_string(value_str: str) -> Decimal:
    """Parse currency string back to Decimal"""
```

2. `Backend/src/utils/services/date_utils.py` (200 lines)
```python
"""
Date and timezone utilities
"""
from datetime import datetime, time
from typing import List, Optional
import pytz

def get_timezone_aware_datetime(dt: datetime, timezone_str: str) -> datetime:
    """Convert naive datetime to timezone-aware"""
    
def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Convert datetime between timezones"""
    
def get_market_timezone(exchange_code: str) -> str:
    """Get timezone for a given exchange code"""
    
def is_market_open(dt: datetime, exchange_code: str) -> bool:
    """Check if market is open at given datetime"""
    
def get_trading_days(start: date, end: date, country_code: str) -> List[date]:
    """Get list of trading days excluding weekends"""
    
def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime to string"""
```

3. `Backend/src/utils/services/financial_utils.py` (250 lines)
```python
"""
Financial calculation utilities
"""
from typing import List
from decimal import Decimal
import numpy as np

def calculate_roi(initial_value: float, current_value: float) -> float:
    """Calculate Return on Investment as percentage"""
    return ((current_value - initial_value) / initial_value) * 100

def calculate_cagr(beginning_value: float, ending_value: float, periods: int) -> float:
    """Calculate Compound Annual Growth Rate"""
    
def calculate_volatility(prices: List[float], period: int = 252) -> float:
    """Calculate annualized volatility using standard deviation"""
    
def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float) -> float:
    """Calculate Sharpe ratio for risk-adjusted returns"""
    
def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Calculate Exponential Moving Average"""
    
def calculate_sma(prices: List[float], period: int) -> List[float]:
    """Calculate Simple Moving Average"""
    
def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """Calculate Relative Strength Index"""
```

### Day 2: Currency System

4. `Backend/src/utils/services/currency_utils.py` (100 lines)
```python
"""
Currency utilities
"""
from investments.models.currency import Currency
from investments.models.exchange_rate import ExchangeRate

def get_currency_symbol(currency_code: str) -> str:
    """Get currency symbol from database or defaults"""
    
def get_decimals_for_currency(currency_code: str) -> int:
    """Get number of decimals for currency"""
    
def is_crypto_currency(currency_code: str) -> bool:
    """Check if currency is cryptocurrency"""
    
def get_exchange_rate(
    base_currency: str,
    quote_currency: str,
    date: Optional[date] = None
) -> Optional[Decimal]:
    """Get exchange rate from database"""
    
def cache_exchange_rates(rates_dict: dict, ttl: int = 14400):
    """Cache exchange rates in Redis"""
```

5. `Backend/src/utils/services/currency_service.py` (200 lines)
```python
"""
Currency conversion service
"""
from typing import Optional
from decimal import Decimal
from datetime import date
import asyncio

class CurrencyService:
    """Service for currency conversion and exchange rate management"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 14400  # 4 hours
        
    async def get_latest_rate(
        self,
        base_currency: str,
        quote_currency: str
    ) -> Optional[Decimal]:
        """Get latest exchange rate with caching"""
        
    async def get_historical_rate(
        self,
        base_currency: str,
        quote_currency: str,
        date: date
    ) -> Optional[Decimal]:
        """Get historical exchange rate"""
        
    async def convert_amount(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        date: Optional[date] = None
    ) -> Optional[Decimal]:
        """Convert amount between currencies"""
        
    async def update_rates_from_api(self):
        """Update exchange rates from external API"""
        
    async def get_supported_currencies(self) -> List[str]:
        """Get list of supported currency codes"""
```

6. `Backend/src/utils/services/exchange_rate_fetcher.py` (180 lines)
```python
"""
Exchange rate fetching service with multiple providers
"""
import aiohttp
from typing import Dict, Optional
from datetime import date
import forex_python

class ExchangeRateFetcher:
    """Fetch exchange rates from multiple sources with fallback"""
    
    PRIMARY_SOURCE = 'https://api.exchangerate-api.com/v4/latest/'
    FALLBACK_SOURCE = forex_python
    
    async def fetch_all_rates(self, base_currency: str = 'USD') -> Dict[str, float]:
        """Fetch all exchange rates for base currency"""
        # Try primary source first
        # Fall back to forex_python on failure
        
    async def fetch_pair_rate(
        self,
        base: str,
        quote: str
    ) -> Optional[float]:
        """Fetch specific currency pair rate"""
        
    async def fetch_historical_rates(
        self,
        base: str,
        date: date
    ) -> Dict[str, float]:
        """Fetch historical rates for a date"""
        
    async def update_database(self, rates_dict: Dict[str, float]):
        """Update ExchangeRate model with latest rates"""
```

### Day 3: Validation & Tests

7. `Backend/src/utils/services/validation_utils.py` (120 lines)
```python
"""
Validation utilities
"""
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email format"""
    
def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    
def validate_currency_code(code: str) -> bool:
    """Validate ISO 4217 currency code"""
    
def validate_country_code(code: str) -> bool:
    """Validate ISO 3166-1 alpha-2 country code"""
    
def validate_isin(isin: str) -> bool:
    """Validate ISIN (International Securities Identification Number)"""
    
def validate_cusip(cusip: str) -> bool:
    """Validate CUSIP (Committee on Uniform Securities Identification Procedures)"""
    
def validate_ticker(ticker: str) -> bool:
    """Validate stock ticker format"""
```

8. Unit Tests: `Backend/src/tests/test_utils/test_number_utils.py` (150 lines)
9. Unit Tests: `Backend/src/tests/test_utils/test_currency_service.py` (200 lines)

### Day 4: API Endpoints

10. `Backend/src/api/currency.py` (150 lines)
```python
"""
Currency conversion API endpoints
"""
from ninja import Router
from decimal import Decimal

router = Router(tags=["Currency"])

@router.get("/currencies")
def list_currencies(request):
    """List all supported currencies"""
    
@router.get("/currencies/{code}")
def get_currency(request, code: str):
    """Get currency details"""
    
@router.get("/exchange-rates")
def get_exchange_rates(request, base: str = 'USD'):
    """Get current exchange rates for base currency"""
    
@router.get("/exchange-rates/convert")
def convert_currency(
    request,
    amount: Decimal,
    from_currency: str,
    to_currency: str
):
    """Convert amount between currencies"""
    
@router.post("/exchange-rates/update")
def update_rates(request):
    """Trigger exchange rate update from API"""
```

Register in `Backend/src/core/api.py`:
```python
from api.currency import router as currency_router
api.add_router("/currency", currency_router)
```

---

## 📋 Sprint 2: Reference Data Models (Days 5-7)

### Day 5: Create Models

11. `Backend/src/assets/models/sector.py` (25 lines)
```python
"""
Sector model for GICS sectors
"""
from django.db import models
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel

class Sector(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    gics_code = models.CharField(max_length=2, blank=True, unique=True)
    
    class Meta:
        db_table = "sectors"
        verbose_name_plural = "sectors"
    
    def __str__(self):
        return self.name
```

12. `Backend/src/assets/models/industry.py` (30 lines)
```python
"""
Industry model linked to sectors
"""
from django.db import models
from assets.models.sector import Sector
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel

class Industry(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        related_name='industries'
    )
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = "industries"
        verbose_name_plural = "industries"
    
    def __str__(self):
        return f"{self.name} ({self.sector.name if self.sector else 'No Sector'})"
```

13. `Backend/src/assets/models/timezone.py` (35 lines)
```python
"""
Timezone model for market timezones
"""
from django.db import models
from assets.models.country import Country
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel

class Timezone(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=100, unique=True)  # "America/New_York"
    abbreviation = models.CharField(max_length=10)  # "EST", "PST", "JST"
    utc_offset = models.SmallIntegerField()  # -5, -8, 9
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timezones'
    )
    
    class Meta:
        db_table = "timezones"
        verbose_name_plural = "timezones"
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"
```

14. Create migrations:
```bash
cd Backend/src
python manage.py makemigrations assets
python manage.py migrate
```

### Day 6: Asset Model Migration

15. Add foreign keys to Asset model:
```python
# In assets/models/asset.py, add:
sector_fk = models.ForeignKey(
    'assets.Sector',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='assets'
)
industry_fk = models.ForeignKey(
    'assets.Industry',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='assets'
)
```

16. Create data migration to populate FKs from existing string data:
```python
# migrations/000X_migrate_sector_industry.py
def migrate_sector_and_industry(apps, schema_editor):
    Sector = apps.get_model('assets', 'Sector')
    Industry = apps.get_model('assets', 'Industry')
    Asset = apps.get_model('assets', 'Asset')
    
    for asset in Asset.objects.all():
        if asset.sector:
            sector, _ = Sector.objects.get_or_create(name__iexact=asset.sector)
            asset.sector_fk = sector
        
        if asset.industry:
            industry, _ = Industry.objects.get_or_create(name__iexact=asset.industry)
            asset.industry_fk = industry
        
        asset.save()
```

### Day 7: Seed Data Commands

17. `Backend/src/utils/management/commands/seed_currencies.py` (150 lines)
```python
"""
Seed currencies management command
"""
from django.core.management.base import BaseCommand
from investments.models.currency import Currency

class Command(BaseCommand):
    help = 'Seed major world currencies'
    
    def handle(self, *args, **options):
        currencies = [
            # Fiat currencies
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'is_crypto': False, 'decimals': 2},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'is_crypto': False, 'decimals': 2},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'is_crypto': False, 'decimals': 2},
            {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'is_crypto': False, 'decimals': 0},
            {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'Fr', 'is_crypto': False, 'decimals': 2},
            {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'is_crypto': False, 'decimals': 2},
            {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$', 'is_crypto': False, 'decimals': 2},
            {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥', 'is_crypto': False, 'decimals': 2},
            {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'is_crypto': False, 'decimals': 2},
            {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': '$', 'is_crypto': False, 'decimals': 2},
            # Crypto currencies
            {'code': 'BTC', 'name': 'Bitcoin', 'symbol': '₿', 'is_crypto': True, 'decimals': 8},
            {'code': 'ETH', 'name': 'Ethereum', 'symbol': 'Ξ', 'is_crypto': True, 'decimals': 18},
            {'code': 'BNB', 'name': 'Binance Coin', 'symbol': 'BNB', 'is_crypto': True, 'decimals': 18},
            {'code': 'SOL', 'name': 'Solana', 'symbol': 'SOL', 'is_crypto': True, 'decimals': 18},
            {'code': 'XRP', 'name': 'XRP', 'symbol': 'XRP', 'is_crypto': True, 'decimals': 6},
            {'code': 'ADA', 'name': 'Cardano', 'symbol': 'ADA', 'is_crypto': True, 'decimals': 18},
            {'code': 'DOT', 'name': 'Polkadot', 'symbol': 'DOT', 'is_crypto': True, 'decimals': 18},
            {'code': 'DOGE', 'name': 'Dogecoin', 'symbol': 'DOGE', 'is_crypto': True, 'decimals': 8},
            {'code': 'AVAX', 'name': 'Avalanche', 'symbol': 'AVAX', 'is_crypto': True, 'decimals': 18},
            {'code': 'MATIC', 'name': 'Polygon', 'symbol': 'MATIC', 'is_crypto': True, 'decimals': 18},
        ]
        
        for currency_data in currencies:
            Currency.objects.get_or_create(
                code=currency_data['code'],
                defaults=currency_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(currencies)} currencies'))
```

18. `Backend/src/utils/management/commands/seed_countries.py` (300 lines)
```python
"""
Seed all countries (~200 countries)
"""
# Full list of countries with ISO codes
# Include all countries with proper regions
```

19. `Backend/src/utils/management/commands/seed_exchanges.py` (120 lines)
```python
"""
Seed major stock exchanges
"""
exchanges = [
    {'code': 'NYSE', 'name': 'New York Stock Exchange', 'country_code': 'US', 'timezone': 'America/New_York'},
    {'code': 'NASDAQ', 'name': 'NASDAQ', 'country_code': 'US', 'timezone': 'America/New_York'},
    {'code': 'LSE', 'name': 'London Stock Exchange', 'country_code': 'GB', 'timezone': 'Europe/London'},
    {'code': 'TSE', 'name': 'Tokyo Stock Exchange', 'country_code': 'JP', 'timezone': 'Asia/Tokyo'},
    {'code': 'SSE', 'name': 'Shanghai Stock Exchange', 'country_code': 'CN', 'timezone': 'Asia/Shanghai'},
    {'code': 'HKEX', 'name': 'HKEX', 'country_code': 'HK', 'timezone': 'Asia/Hong_Kong'},
    {'code': 'ASX', 'name': 'Australian Securities Exchange', 'country_code': 'AU', 'timezone': 'Australia/Sydney'},
    {'code': 'TSX', 'name': 'Toronto Stock Exchange', 'country_code': 'CA', 'timezone': 'America/Toronto'},
    # ... more exchanges
]
```

20. `Backend/src/utils/management/commands/seed_sectors_industries.py` (180 lines)
```python
"""
Seed GICS sectors and industries
"""
from assets.models.sector import Sector
from assets.models.industry import Industry

# 11 GICS sectors
sectors_data = [
    {'name': 'Energy', 'gics_code': '10', 'description': 'Energy sector'},
    {'name': 'Materials', 'gics_code': '15', 'description': 'Materials sector'},
    {'name': 'Industrials', 'gics_code': '20', 'description': 'Industrials sector'},
    {'name': 'Consumer Discretionary', 'gics_code': '25', 'description': 'Consumer Discretionary'},
    {'name': 'Consumer Staples', 'gics_code': '30', 'description': 'Consumer Staples'},
    {'name': 'Health Care', 'gics_code': '35', 'description': 'Health Care'},
    {'name': 'Financials', 'gics_code': '40', 'description': 'Financials'},
    {'name': 'Information Technology', 'gics_code': '45', 'description': 'Information Technology'},
    {'name': 'Communication Services', 'gics_code': '50', 'description': 'Communication Services'},
    {'name': 'Utilities', 'gics_code': '55', 'description': 'Utilities'},
    {'name': 'Real Estate', 'gics_code': '60', 'description': 'Real Estate'},
]

# ~100 industries mapped to sectors
industries_data = [
    {'name': 'Software', 'sector': 'Information Technology'},
    {'name': 'Semiconductors', 'sector': 'Information Technology'},
    {'name': 'IT Services', 'sector': 'Information Technology'},
    {'name': 'Hardware', 'sector': 'Information Technology'},
    {'name': 'Banks', 'sector': 'Financials'},
    {'name': 'Insurance', 'sector': 'Financials'},
    {'name': 'Asset Management', 'sector': 'Financials'},
    {'name': 'Investment Banking', 'sector': 'Financials'},
    {'name': 'Biotechnology', 'sector': 'Health Care'},
    {'name': 'Pharmaceuticals', 'sector': 'Health Care'},
    {'name': 'Medical Devices', 'sector': 'Health Care'},
    # ... more industries
]
```

21. `Backend/src/utils/management/commands/update_exchange_rates.py` (80 lines)
```python
"""
Management command to update exchange rates from API
"""
from django.core.management.base import BaseCommand
from utils.services.exchange_rate_fetcher import ExchangeRateFetcher

class Command(BaseCommand):
    help = 'Update exchange rates from external API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--base',
            type=str,
            default='USD',
            help='Base currency for rates (default: USD)'
        )
    
    async def handle(self, *args, **options):
        fetcher = ExchangeRateFetcher()
        base = options['base']
        
        self.stdout.write(f'Fetching exchange rates for {base}...')
        rates = await fetcher.fetch_all_rates(base)
        
        await fetcher.update_database(rates)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {len(rates)} exchange rates'))
```

---

## 📋 Sprint 3: Frontend Utilities (Days 8-11)

### Day 8: Currency & Financial Utilities

22. `Frontend/src/lib/utils/currency.ts` (120 lines)
```typescript
/**
 * Currency conversion and formatting utilities
 */

export const CURRENCIES = {
  USD: { code: 'USD', symbol: '$', decimals: 2, name: 'US Dollar', locale: 'en-US' },
  EUR: { code: 'EUR', symbol: '€', decimals: 2, name: 'Euro', locale: 'de-DE' },
  GBP: { code: 'GBP', symbol: '£', decimals: 2, name: 'British Pound', locale: 'en-GB' },
  JPY: { code: 'JPY', symbol: '¥', decimals: 0, name: 'Japanese Yen', locale: 'ja-JP' },
  BTC: { code: 'BTC', symbol: '₿', decimals: 8, name: 'Bitcoin', isCrypto: true },
  ETH: { code: 'ETH', symbol: 'Ξ', decimals: 18, name: 'Ethereum', isCrypto: true },
  // ... more currencies
} as const

export function convertCurrency(
  amount: number,
  fromCurrency: string,
  toCurrency: string,
  rates?: Record<string, number>
): number {
  const rate = rates?.[`${fromCurrency}_${toCurrency}`] || 1
  return amount * rate
}

export function getCurrencySymbol(code: string): string {
  return CURRENCIES[code]?.symbol || code
}

export function getCurrencyDecimals(code: string): number {
  return CURRENCIES[code]?.decimals || 2
}

export function formatCurrencyLocal(
  amount: number,
  currency: string,
  locale?: string
): string {
  const currencyInfo = CURRENCIES[currency]
  const userLocale = locale || currencyInfo?.locale || 'en-US'
  
  return new Intl.NumberFormat(userLocale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: currencyInfo?.decimals || 2,
    maximumFractionDigits: currencyInfo?.decimals || 2,
  }).format(amount)
}

export function isCryptoCurrency(code: string): boolean {
  return CURRENCIES[code]?.isCrypto || false
}
```

23. `Frontend/src/lib/utils/financial.ts` (180 lines)
```typescript
/**
 * Financial calculation utilities
 */

export function calculateROI(
  initial: number,
  current: number
): number {
  if (initial === 0) return 0
  return ((current - initial) / initial) * 100
}

export function calculateCAGR(
  beginningValue: number,
  endingValue: number,
  periods: number
): number {
  if (beginningValue === 0 || periods === 0) return 0
  return (Math.pow(endingValue / beginningValue, 1 / periods) - 1) * 100
}

export function calculateVolatility(
  prices: number[],
  period: number = 252
): number {
  if (prices.length < 2) return 0
  
  const returns: number[] = []
  for (let i = 1; i < prices.length; i++) {
    returns.push((prices[i] - prices[i - 1]) / prices[i - 1])
  }
  
  const mean = returns.reduce((a, b) => a + b, 0) / returns.length
  const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / returns.length
  
  return Math.sqrt(variance * period) * 100
}

export function calculateSharpeRatio(
  returns: number[],
  riskFreeRate: number = 0
): number {
  if (returns.length === 0) return 0
  
  const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
  const volatility = calculateVolatility(returns.map(r => r + 1), 1)
  
  if (volatility === 0) return 0
  
  return (avgReturn - riskFreeRate / 100) / volatility * 100
}

export function calculateEMA(prices: number[], period: number): number[] {
  if (prices.length < period) return []
  
  const multiplier = 2 / (period + 1)
  const ema: number[] = [prices[0]]
  
  for (let i = 1; i < prices.length; i++) {
    ema.push((prices[i] - ema[i - 1]) * multiplier + ema[i - 1])
  }
  
  return ema
}

export function calculateSMA(prices: number[], period: number): number[] {
  if (prices.length < period) return []
  
  const sma: number[] = []
  
  for (let i = period - 1; i < prices.length; i++) {
    const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
    sma.push(sum / period)
  }
  
  return sma
}

export function calculateRSI(prices: number[], period: number = 14): number[] {
  if (prices.length < period + 1) return []
  
  const rsi: number[] = []
  const gains: number[] = []
  const losses: number[] = []
  
  for (let i = 1; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1]
    gains.push(Math.max(0, change))
    losses.push(Math.max(0, -change))
  }
  
  for (let i = period - 1; i < gains.length; i++) {
    const avgGain = gains.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period
    const avgLoss = losses.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period
    
    if (avgLoss === 0) {
      rsi.push(100)
    } else {
      const rs = avgGain / avgLoss
      rsi.push(100 - (100 / (1 + rs)))
    }
  }
  
  return rsi
}
```

### Day 9: Date & Validation Utilities

24. `Frontend/src/lib/utils/date.ts` (140 lines)
```typescript
/**
 * Date and timezone utilities
 */

export function convertTimeZone(
  date: Date,
  fromTimeZone: string,
  toTimeZone: string
): Date {
  const dateString = date.toLocaleString('en-US', { timeZone: fromTimeZone })
  const dateInFromTz = new Date(dateString)
  
  const toDateString = dateInFromTz.toLocaleString('en-US', { timeZone: toTimeZone })
  return new Date(toDateString)
}

export function formatDateTimeLocal(
  date: Date,
  format: 'short' | 'long' | 'time' | 'full' = 'short',
  locale: string = 'en-US'
): string {
  const options: Intl.DateTimeFormatOptions = {}
  
  if (format === 'time') {
    options.hour = '2-digit'
    options.minute = '2-digit'
    options.second = '2-digit'
  } else if (format === 'short') {
    options.year = 'numeric'
    options.month = 'short'
    options.day = 'numeric'
  } else if (format === 'long') {
    options.year = 'numeric'
    options.month = 'long'
    options.day = 'numeric'
  } else if (format === 'full') {
    options.year = 'numeric'
    options.month = 'long'
    options.day = 'numeric'
    options.hour = '2-digit'
    options.minute = '2-digit'
  }
  
  return new Intl.DateTimeFormat(locale, options).format(date)
}

export function isMarketOpen(
  date: Date,
  exchangeCode: string
): boolean {
  // Implement based on exchange trading hours
  // NYSE: 9:30 AM - 4:00 PM ET, Mon-Fri
  // LSE: 8:00 AM - 4:30 PM GMT, Mon-Fri
  // etc.
  
  const hour = date.getHours()
  const day = date.getDay()
  
  if (day === 0 || day === 6) return false  // Weekend
  
  if (exchangeCode === 'NYSE' || exchangeCode === 'NASDAQ') {
    return hour >= 9 && hour < 16 && date.getMinutes() >= 30
  }
  
  // Add more exchanges
  return false
}

export function getNextTradingDay(date: Date, countryCode?: string): Date {
  const nextDay = new Date(date)
  nextDay.setDate(date.getDate() + 1)
  
  // Skip weekends
  while (nextDay.getDay() === 0 || nextDay.getDay() === 6) {
    nextDay.setDate(nextDay.getDate() + 1)
  }
  
  return nextDay
}

export function getTradingDays(
  start: Date,
  end: Date,
  countryCode?: string
): Date[] {
  const days: Date[] = []
  const current = new Date(start)
  
  while (current <= end) {
    if (current.getDay() !== 0 && current.getDay() !== 6) {
      days.push(new Date(current))
    }
    current.setDate(current.getDate() + 1)
  }
  
  return days
}
```

25. `Frontend/src/lib/utils/validation.ts` (100 lines)
```typescript
/**
 * Validation utilities
 */

export function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

export function validatePhone(phone: string): boolean {
  const regex = /^\+?[\d\s\-\(\)]+$/
  return regex.test(phone) && phone.replace(/\D/g, '').length >= 10
}

export function validateCurrencyCode(code: string): boolean {
  return /^[A-Z]{3}$/.test(code)
}

export function validateISIN(isin: string): boolean {
  // ISIN format: 2 letters + 9 digits + 1 check digit
  const regex = /^[A-Z]{2}[A-Z0-9]{9}[0-9]$/
  if (!regex.test(isin)) return false
  
  // Validate check digit
  const digits = isin.slice(0, 11).replace(/[A-Z]/g, (c) => (c.charCodeAt(0) - 55).toString())
  let sum = 0
  for (let i = 0; i < digits.length; i++) {
    sum += parseInt(digits[i]) * (i % 2 === 0 ? 1 : 2)
  }
  const checkDigit = (10 - (sum % 10)) % 10
  
  return checkDigit === parseInt(isin[11])
}

export function validateCUSIP(cusip: string): boolean {
  // CUSIP: 9 characters (8 digits + 1 check digit)
  const regex = /^[0-9A-Z]{9}$/
  if (!regex.test(cusip)) return false
  
  // Validate check digit
  const digits = cusip.slice(0, 8).replace(/[A-Z]/g, (c) => (c.charCodeAt(0) - 55).toString())
  let sum = 0
  for (let i = 0; i < digits.length; i++) {
    sum += parseInt(digits[i]) * ((i + 1) % 2 === 0 ? 2 : 1)
  }
  const checkDigit = (10 - (sum % 10)) % 10
  
  return checkDigit === parseInt(cusip[8])
}

export function validateTicker(ticker: string): boolean {
  return /^[A-Z]{1,5}$/.test(ticker)
}

export function validateURL(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}
```

### Day 10: Constants & Locale

26. `Frontend/src/lib/constants/currencies.ts` (100 lines) - Already shown above
27. `Frontend/src/lib/constants/timezones.ts` (80 lines)
```typescript
/**
 * Timezone constants for markets
 */

export const MARKET_TIMEZONES = {
  'US': {
    timezone: 'America/New_York',
    abbreviation: 'EST/EDT',
    utcOffset: -5,
    locale: 'en-US'
  },
  'UK': {
    timezone: 'Europe/London',
    abbreviation: 'GMT/BST',
    utcOffset: 0,
    locale: 'en-GB'
  },
  'JP': {
    timezone: 'Asia/Tokyo',
    abbreviation: 'JST',
    utcOffset: 9,
    locale: 'ja-JP'
  },
  'DE': {
    timezone: 'Europe/Berlin',
    abbreviation: 'CET/CEST',
    utcOffset: 1,
    locale: 'de-DE'
  },
} as const

export const EXCHANGE_TIMEZONES: Record<string, string> = {
  'NYSE': 'America/New_York',
  'NASDAQ': 'America/New_York',
  'LSE': 'Europe/London',
  'TSE': 'Asia/Tokyo',
  'SSE': 'Asia/Shanghai',
  'HKEX': 'Asia/Hong_Kong',
  'ASX': 'Australia/Sydney',
  'TSX': 'America/Toronto',
  // ... more exchanges
}

export const COUNTRY_TIMEZONES: Record<string, string> = {
  'US': 'America/New_York',
  'GB': 'Europe/London',
  'JP': 'Asia/Tokyo',
  'DE': 'Europe/Berlin',
  'FR': 'Europe/Paris',
  'CN': 'Asia/Shanghai',
  'IN': 'Asia/Kolkata',
  'AU': 'Australia/Sydney',
  // ... more countries
}
```

28. `Frontend/src/lib/constants/sectors.ts` (100 lines)
```typescript
/**
 * Sector and industry constants (GICS)
 */

export const GICS_SECTORS = [
  { code: '10', name: 'Energy', description: 'Energy sector' },
  { code: '15', name: 'Materials', description: 'Materials sector' },
  { code: '20', name: 'Industrials', description: 'Industrials sector' },
  { code: '25', name: 'Consumer Discretionary', description: 'Consumer Discretionary' },
  { code: '30', name: 'Consumer Staples', description: 'Consumer Staples' },
  { code: '35', name: 'Health Care', description: 'Health Care' },
  { code: '40', name: 'Financials', description: 'Financials' },
  { code: '45', name: 'Information Technology', description: 'Information Technology' },
  { code: '50', name: 'Communication Services', description: 'Communication Services' },
  { code: '55', name: 'Utilities', description: 'Utilities' },
  { code: '60', name: 'Real Estate', description: 'Real Estate' },
] as const

export const INDUSTRIES: Record<string, string[]> = {
  'Information Technology': [
    'Software',
    'Semiconductors',
    'IT Services',
    'Hardware',
    'Electronic Equipment',
    'Communications Equipment'
  ],
  'Financials': [
    'Banks',
    'Insurance',
    'Asset Management',
    'Investment Banking',
    'Consumer Finance',
    'Capital Markets'
  ],
  'Health Care': [
    'Biotechnology',
    'Pharmaceuticals',
    'Medical Devices',
    'Health Care Providers',
    'Health Care Equipment'
  ],
  'Consumer Discretionary': [
    'Automobiles',
    'Retail',
    'Media',
    'Consumer Services',
    'Hotels, Restaurants & Leisure'
  ],
  // ... more industries
}

export const SECTOR_ICONS: Record<string, string> = {
  'Technology': '💻',
  'Health Care': '🏥',
  'Financials': '💰',
  'Energy': '⛽',
  'Consumer': '🛒',
  'Industrials': '🏭',
  'Utilities': '⚡',
  'Real Estate': '🏠',
  'Materials': '🔧',
  'Communication': '📡',
}
```

29. `Frontend/src/lib/utils/locale.ts` (80 lines)
```typescript
/**
 * Internationalization utilities
 */

const LOCALE_CURRENCIES: Record<string, string> = {
  'en-US': 'USD',
  'en-GB': 'GBP',
  'de-DE': 'EUR',
  'ja-JP': 'JPY',
  'zh-CN': 'CNY',
}

const LOCALE_TIMEZONES: Record<string, string> = {
  'en-US': 'America/New_York',
  'en-GB': 'Europe/London',
  'de-DE': 'Europe/Berlin',
  'ja-JP': 'Asia/Tokyo',
  'zh-CN': 'Asia/Shanghai',
}

export function getUserLocale(): string {
  if (typeof window === 'undefined') return 'en-US'
  return navigator.language || localStorage.getItem('locale') || 'en-US'
}

export function getUserCurrency(): string {
  return localStorage.getItem('currency') || LOCALE_CURRENCIES[getUserLocale()] || 'USD'
}

export function getUserTimezone(): string {
  return localStorage.getItem('timezone') || LOCALE_TIMEZONES[getUserLocale()] || 'America/New_York'
}

export function setLocalePreferences(locale: string, currency: string, timezone: string): void {
  localStorage.setItem('locale', locale)
  localStorage.setItem('currency', currency)
  localStorage.setItem('timezone', timezone)
}

export function formatNumberLocale(value: number, locale?: string): string {
  const userLocale = locale || getUserLocale()
  return new Intl.NumberFormat(userLocale).format(value)
}

export function formatPercentLocale(value: number, locale?: string): string {
  const userLocale = locale || getUserLocale()
  return new Intl.NumberFormat(userLocale, {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value / 100)
}
```

### Day 11: Tests

30. `Frontend/src/tests/utils/currency.test.ts` (120 lines)
31. `Frontend/src/tests/utils/financial.test.ts` (150 lines)
32. `Frontend/src/tests/utils/validation.test.ts` (80 lines)

---

## 📋 Sprint 4: Frontend Integration (Days 12-14)

### Day 12: Store & API

33. `Frontend/src/stores/referenceStore.ts` (200 lines)
```typescript
/**
 * Reference data store (Zustand)
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ReferenceState {
  currencies: Record<string, Currency>
  countries: Record<string, Country>
  exchanges: Record<string, Exchange>
  sectors: Sector[]
  industries: Industry[]
  exchangeRates: Record<string, number>
  loading: boolean
  error: string | null
  lastUpdated: Date | null
  
  // Actions
  loadCurrencies: () => Promise<void>
  loadCountries: () => Promise<void>
  loadExchanges: () => Promise<void>
  loadSectors: () => Promise<void>
  loadIndustries: () => Promise<void>
  loadExchangeRates: (baseCurrency?: string) => Promise<void>
  convertCurrency: (amount: number, from: string, to: string) => number
  invalidateCache: () => void
}

export const useReferenceStore = create<ReferenceState>()(
  persist(
    (set, get) => ({
      currencies: {},
      countries: {},
      exchanges: {},
      sectors: [],
      industries: [],
      exchangeRates: {},
      loading: false,
      error: null,
      lastUpdated: null,
      
      loadCurrencies: async () => {
        set({ loading: true, error: null })
        try {
          const response = await referenceApi.getCurrencies()
          const currenciesMap = response.reduce((acc, curr) => ({ ...acc, [curr.code]: curr }), {})
          set({ currencies: currenciesMap, loading: false })
        } catch (error) {
          set({ error: error.message, loading: false })
        }
      },
      
      loadExchangeRates: async (baseCurrency = 'USD') => {
        set({ loading: true, error: null })
        try {
          const response = await referenceApi.getExchangeRates(baseCurrency)
          set({ exchangeRates: response.rates, lastUpdated: new Date(), loading: false })
        } catch (error) {
          set({ error: error.message, loading: false })
        }
      },
      
      convertCurrency: (amount, from, to) => {
        const rates = get().exchangeRates
        const rate = rates[`${from}_${to}`] || 1
        return amount * rate
      },
      
      invalidateCache: () => {
        set({ exchangeRates: {}, lastUpdated: null })
      },
    }),
    {
      name: 'reference-storage',
      partialize: (state) => ({
        currencies: state.currencies,
        countries: state.countries,
        lastUpdated: state.lastUpdated,
      }),
    }
  )
)
```

34. `Frontend/src/lib/api/reference.ts` (100 lines)
```typescript
/**
 * Reference data API client
 */
import { apiClient } from './client'

export interface Currency {
  code: string
  name: string
  symbol: string
  is_crypto: boolean
  decimals: number
}

export interface Country {
  code: string
  name: string
  region: string
}

export interface Exchange {
  code: string
  name: string
  country: string
  timezone: string
}

export const referenceApi = {
  getCurrencies: (): Promise<Currency[]> =>
    apiClient.get<Currency[]>('/reference/currencies'),
    
  getCurrency: (code: string): Promise<Currency> =>
    apiClient.get<Currency>(`/reference/currencies/${code}`),
    
  getCountries: (): Promise<Country[]> =>
    apiClient.get<Country[]>('/reference/countries'),
    
  getExchanges: (): Promise<Exchange[]> =>
    apiClient.get<Exchange[]>('/reference/exchanges'),
    
  getSectors: (): Promise<Sector[]> =>
    apiClient.get<Sector[]>('/reference/sectors'),
    
  getIndustries: (): Promise<Industry[]> =>
    apiClient.get<Industry[]>('/reference/industries'),
    
  getExchangeRates: (baseCurrency?: string): Promise<ExchangeRatesResponse> =>
    apiClient.get<ExchangeRatesResponse>('/reference/exchange-rates', { base: baseCurrency }),
  
  convertCurrency: (
    amount: number,
    from: string,
    to: string
  ): Promise<ConversionResult> =>
    apiClient.get<ConversionResult>('/reference/exchange-rates/convert', {
      amount,
      from: from.toUpperCase(),
      to: to.toUpperCase(),
    }),
  
  updateExchangeRates: (): Promise<UpdateResult> =>
    apiClient.post<UpdateResult>('/reference/exchange-rates/update'),
}
```

### Day 13: React Hooks

35. `Frontend/src/hooks/useReferenceData.ts` (120 lines)
```typescript
/**
 * React hooks for reference data
 */
import { useEffect } from 'react'
import { useReferenceStore } from '@/stores/referenceStore'

export function useCurrencies() {
  const { currencies, loadCurrencies, loading, error } = useReferenceStore()
  
  useEffect(() => {
    if (Object.keys(currencies).length === 0) {
      loadCurrencies()
    }
  }, [])
  
  return { currencies, loading, error, reload: loadCurrencies }
}

export function useCountries() {
  const { countries, loadCountries, loading, error } = useReferenceStore()
  
  useEffect(() => {
    if (Object.keys(countries).length === 0) {
      loadCountries()
    }
  }, [])
  
  return { countries, loading, error, reload: loadCountries }
}

export function useExchangeRates(baseCurrency = 'USD') {
  const { exchangeRates, loadExchangeRates, convertCurrency, loading, error } = useReferenceStore()
  
  useEffect(() => {
    // Load rates if not loaded or expired (> 4 hours)
    const lastUpdated = useReferenceStore.getState().lastUpdated
    const now = new Date()
    const fourHours = 4 * 60 * 60 * 1000
    
    if (!lastUpdated || (now.getTime() - lastUpdated.getTime()) > fourHours) {
      loadExchangeRates(baseCurrency)
    }
  }, [baseCurrency])
  
  return {
    rates: exchangeRates,
    convert: convertCurrency,
    loading,
    error,
    refresh: () => loadExchangeRates(baseCurrency)
  }
}

export function useCurrencyConversion() {
  const { convert } = useReferenceStore()
  const { currencies } = useCurrencies()
  const { rates } = useExchangeRates()
  
  const formatCurrency = (amount: number, currency: string) => {
    const curr = currencies[currency]
    if (!curr) return `${amount.toFixed(2)} ${currency}`
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: curr.decimals,
      maximumFractionDigits: curr.decimals,
    }).format(amount)
  }
  
  return {
    convert,
    formatCurrency,
    currencies,
    rates
  }
}
```

### Day 14: Integration Testing

36. Update existing components to use new utilities
37. Test currency conversion in components
38. Test locale formatting across different currencies
39. Verify timezone conversions work correctly
40. Test error handling for missing data

---

## 📋 Sprint 5: API & Reference Endpoints (Days 15-16)

### Day 15: Backend Reference API

41. `Backend/src/api/reference.py` (150 lines)
```python
"""
Reference data API endpoints
"""
from ninja import Router
from django.shortcuts import get_object_or_404

router = Router(tags=["Reference Data"])

@router.get("/currencies")
def list_currencies(request):
    """List all currencies"""
    from investments.models.currency import Currency
    return Currency.objects.all()

@router.get("/currencies/{code}")
def get_currency(request, code: str):
    """Get currency by code"""
    from investments.models.currency import Currency
    return get_object_or_404(Currency, code__iexact=code)

@router.get("/countries")
def list_countries(request):
    """List all countries"""
    from assets.models.country import Country
    return Country.objects.all()

@router.get("/countries/{code}")
def get_country(request, code: str):
    """Get country by ISO code"""
    from assets.models.country import Country
    return get_object_or_404(Country, code__iexact=code)

@router.get("/exchanges")
def list_exchanges(request):
    """List all exchanges"""
    from assets.models.exchange import Exchange
    return Exchange.objects.all()

@router.get("/sectors")
def list_sectors(request):
    """List all sectors"""
    from assets.models.sector import Sector
    return Sector.objects.all()

@router.get("/industries")
def list_industries(request, sector: str = None):
    """List all industries, optionally filtered by sector"""
    from assets.models.industry import Industry
    
    if sector:
        return Industry.objects.filter(sector__name__iexact=sector)
    
    return Industry.objects.all()
```

Register in `Backend/src/core/api.py`:
```python
from api.reference import router as reference_router
api.add_router("/reference", reference_router)
```

### Day 16: Exchange Rate Endpoints

42. Add to `Backend/src/api/currency.py`:
```python
@router.get("/exchange-rates")
def get_exchange_rates(request, base: str = 'USD'):
    """Get current exchange rates for base currency"""
    from utils.services.currency_service import CurrencyService
    
    service = CurrencyService()
    rates = service.get_latest_rates(base)
    
    return {
        'base': base,
        'rates': rates,
        'timestamp': datetime.now().isoformat()
    }

@router.get("/exchange-rates/convert")
def convert_currency_endpoint(
    request,
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    date: Optional[date] = None
):
    """Convert amount between currencies"""
    from utils.services.currency_service import CurrencyService
    
    service = CurrencyService()
    converted = service.convert_amount(amount, from_currency.upper(), to_currency.upper(), date)
    
    if converted is None:
        return {'error': 'Unable to convert between these currencies'}, 404
    
    return {
        'from': from_currency.upper(),
        'to': to_currency.upper(),
        'amount': float(amount),
        'converted': float(converted),
        'rate': float(converted / amount)
    }

@router.post("/exchange-rates/update")
async def update_rates(request):
    """Trigger exchange rate update from API"""
    from utils.services.exchange_rate_fetcher import ExchangeRateFetcher
    
    fetcher = ExchangeRateFetcher()
    await fetcher.update_database()
    
    return {
        'success': True,
        'message': 'Exchange rates updated successfully',
        'timestamp': datetime.now().isoformat()
    }
```

---

## 📋 Sprint 6: Scheduled Tasks & Finalization (Days 17-19)

### Day 17: Celery Task for Exchange Rates

43. `Backend/src/tasks/exchange_rates.py` (80 lines)
```python
"""
Celery task for automatic exchange rate updates
"""
from celery import shared_task
from django.utils import timezone
from utils.services.exchange_rate_fetcher import ExchangeRateFetcher

@shared_task
def update_exchange_rates():
    """
    Update exchange rates from API
    Runs every 4 hours
    """
    fetcher = ExchangeRateFetcher()
    
    try:
        # Update USD rates
        asyncio.run(fetcher.update_database())
        
        # Update EUR rates
        asyncio.run(fetcher.update_database('EUR'))
        
        return {'status': 'success', 'updated': timezone.now()}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@shared_task
def update_all_currency_rates():
    """Update all major currency rates"""
    from utils.services.currency_service import CurrencyService
    
    service = CurrencyService()
    
    base_currencies = ['USD', 'EUR', 'GBP', 'JPY']
    results = []
    
    for base in base_currencies:
        try:
            result = service.update_rates_from_api()
            results.append({'base': base, 'status': 'success'})
        except Exception as e:
            results.append({'base': base, 'status': 'error', 'message': str(e)})
    
    return results
```

44. Configure Celery beat schedule in `Backend/src/celeryconfig.py`:
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'update-exchange-rates': {
        'task': 'tasks.exchange_rates.update_exchange_rates',
        'schedule': crontab(minute=0),  # Every hour
    },
    'update-all-rates': {
        'task': 'tasks.exchange_rates.update_all_currency_rates',
        'schedule': crab(minute=0, hour='*/4'),  # Every 4 hours
    },
}
```

### Day 18: Documentation

45. Update `AGENTS.md` with new utility patterns
46. Create utility usage documentation
47. Add example code snippets

### Day 19: Testing & Bug Fixes

48. End-to-end testing of currency conversion
49. Test locale formatting (en-US, en-GB, de-DE, ja-JP)
50. Test timezone conversions
51. Test exchange rate updates
52. Performance testing
53. Bug fixes and refinements

---

## 📊 Final Deliverables Summary

### Backend Files (28 files, ~4,000 lines)
```
utils/services/
├── number_utils.py          (150 lines)
├── date_utils.py            (200 lines)
├── financial_utils.py       (250 lines)
├── currency_utils.py        (100 lines)
├── currency_service.py      (200 lines)
├── exchange_rate_fetcher.py (180 lines)
└── validation_utils.py      (120 lines)

utils/management/commands/
├── seed_currencies.py       (150 lines)
├── seed_countries.py        (300 lines)
├── seed_exchanges.py        (120 lines)
├── seed_sectors_industries.py (180 lines)
└── update_exchange_rates.py (80 lines)

assets/models/
├── sector.py                (25 lines)
├── industry.py              (30 lines)
└── timezone.py              (35 lines)

api/
├── currency.py              (150 lines)
└── reference.py             (150 lines)

tasks/
└── exchange_rates.py        (80 lines)
```

### Frontend Files (18 files, ~2,000 lines)
```
lib/utils/
├── currency.ts              (120 lines)
├── financial.ts             (180 lines)
├── date.ts                  (140 lines)
├── validation.ts            (100 lines)
└── locale.ts                (80 lines)

lib/constants/
├── currencies.ts            (100 lines)
├── timezones.ts             (80 lines)
└── sectors.ts               (100 lines)

stores/
└── referenceStore.ts        (200 lines)

lib/api/
└── reference.ts             (100 lines)

hooks/
└── useReferenceData.ts      (120 lines)

tests/utils/
├── currency.test.ts         (120 lines)
├── financial.test.ts        (150 lines)
└── validation.test.ts       (80 lines)
```

---

## 🎯 Implementation Checklist

### Sprint 1: Backend Utilities ✅
- [ ] number_utils.py
- [ ] date_utils.py
- [ ] financial_utils.py
- [ ] currency_utils.py
- [ ] currency_service.py
- [ ] exchange_rate_fetcher.py
- [ ] validation_utils.py
- [ ] Unit tests (backend utils)
- [ ] api/currency.py

### Sprint 2: Reference Models ✅
- [ ] Sector model
- [ ] Industry model
- [ ] Timezone model
- [ ] Migrations
- [ ] Asset model migration (sector/industry FKs)
- [ ] Seed currencies command
- [ ] Seed countries command
- [ ] Seed exchanges command
- [ ] Seed sectors/industries command

### Sprint 3: Frontend Utilities ✅
- [ ] lib/utils/currency.ts
- [ ] lib/utils/financial.ts
- [ ] lib/utils/date.ts
- [ ] lib/utils/validation.ts
- [ ] lib/utils/locale.ts
- [ ] lib/constants/currencies.ts
- [ ] lib/constants/timezones.ts
- [ ] lib/constants/sectors.ts
- [ ] Unit tests (frontend utils)

### Sprint 4: Frontend Integration ✅
- [ ] stores/referenceStore.ts
- [ ] lib/api/reference.ts
- [ ] hooks/useReferenceData.ts
- [ ] Integration testing

### Sprint 5: API Endpoints ✅
- [ ] api/reference.py
- [ ] Currency API endpoints
- [ ] Exchange rate endpoints
- [ ] API documentation

### Sprint 6: Finalization ✅
- [ ] Celery scheduled tasks
- [ ] Documentation
- [ ] End-to-end testing
- [ ] Bug fixes

---

## 🚀 Quick Start Commands

### Backend Setup
```bash
# Create migrations
python manage.py makemigrations assets
python manage.py makemigrations investments

# Run migrations
python manage.py migrate

# Seed reference data
python manage.py seed_currencies
python manage.py seed_countries
python manage.py seed_exchanges
python manage.py seed_sectors_industries

# Update exchange rates manually
python manage.py update_exchange_rates --base=USD

# Run tests
pytest tests/test_utils/
```

### Frontend Setup
```bash
# Install dependencies
npm install

# Run tests
npm run test

# Type check
npx tsc --noEmit
```

---

**Status**: READY FOR IMPLEMENTATION  
**Total Estimated Time**: 14-19 days  
**Priority**: HIGH - Core utilities needed throughout the application  
**Next Step**: Start Sprint 1 - Backend Utility Services

