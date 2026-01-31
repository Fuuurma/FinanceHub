# 💱 TASK: C-039 - Multi-Currency Portfolio Support

**Task ID:** C-039
**Created:** February 1, 2026
**Assigned To:** Backend Coder (Guido)
**Status:** ⏳ PENDING
**Priority:** P2 MEDIUM
**Estimated Time:** 14-18 hours
**Deadline:** March 10, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Enable portfolios to hold assets in multiple currencies with:
- Multi-currency positions
- Automatic currency conversion
- FX gains/losses tracking
- Base currency selection
- Real-time FX rates
- Currency allocation breakdown

---

## 📋 REQUIREMENTS

### 1. Currency Models

```python
# apps/backend/src/investments/models/currency.py
class Currency(models.Model):
    code = CharField(primary_key=True)  # 'USD', 'EUR', 'GBP', 'JPY', etc.
    name = CharField()  # 'US Dollar', 'Euro', etc.
    symbol = CharField(max_length=3)  # '$', '€', '£', '¥'
    exchange_rate_to_usd = DecimalField(max_digits=12, decimal_places=6)
    last_updated = DateTimeField(auto_now_add=True)

class Position(models.Model):
    # ... existing fields ...
    currency = CharField(max_length=3, default='USD')  # NEW
    original_cost_basis = DecimalField(max_digits=12, decimal_places=4)  # In original currency
    original_quantity = DecimalField(max_digits=12, decimal_places=4)  # Unchanged

class CurrencyConversion(models.Model):
    position = ForeignKey(Position)
    from_currency = CharField(max_length=3)
    to_currency = CharField(max_length=3)  # Usually USD or base currency
    exchange_rate = DecimalField(max_digits=12, decimal_places=6)
    converted_amount = DecimalField(max_digits=12, decimal_places=2)
    conversion_date = DateField()
    created_at = DateTimeField(auto_now_add=True)

class FXGainLoss(models.Model):
    position = ForeignKey(Position)
    currency = CharField(max_length=3)
    original_cost_local = DecimalField(max_digits=12, decimal_places=2)  # In local currency
    original_cost_base = DecimalField(max_digits=12, decimal_places=2)  # In base currency
    current_value_local = DecimalField(max_digits=12, decimal_places=2)
    current_value_base = DecimalField(max_digits=12, decimal_places=2)
    fx_gain_loss = DecimalField(max_digits=12, decimal_places=2)
    fx_gain_loss_pct = DecimalField(max_digits=8, decimal_places=4)
    calculated_at = DateTimeField(auto_now_add=True)
```

### 2. Currency Service

```python
# apps/backend/src/investments/services/currency_service.py
import requests

class CurrencyService:
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """
        Get current exchange rate
        Uses external FX API (e.g., exchangerate-api.io)
        """
        if from_currency == to_currency:
            return Decimal('1.0')

        # Cache rates for 1 hour
        cached = Currency.objects.filter(
            code=f"{from_currency}_{to_currency}"
        ).first()

        if cached and cached.last_updated > timezone.now() - timedelta(hours=1):
            return cached.exchange_rate_to_usd

        # Fetch from API
        rate = self._fetch_rate_from_api(from_currency, to_currency)

        # Update cache
        Currency.objects.update_or_create(
            code=f"{from_currency}_{to_currency}",
            defaults={'exchange_rate_to_usd': rate}
        )

        return rate

    def _fetch_rate_from_api(self, from_currency: str, to_currency: str) -> Decimal:
        """
        Fetch from external FX API
        Example: exchangerate-api.io
        """
        # Use free tier API or paid service
        url = f"https://api.exchangerate-api.io/v4/latest/{from_currency}"
        response = requests.get(url)
        data = response.json()

        if to_currency in data['rates']:
            return Decimal(str(data['rates'][to_currency]))

        raise ValueError(f"Currency {to_currency} not found")

    def convert_to_base_currency(self, amount: Decimal,
                                 from_currency: str,
                                 base_currency: str) -> Decimal:
        """
        Convert amount from one currency to another
        """
        rate = self.get_exchange_rate(from_currency, base_currency)
        return amount * rate

    def calculate_fx_gains(self, position: Position,
                           base_currency: str) -> FXGainLoss:
        """
        Calculate FX gains/losses for position
        FX Gain = Current Value (base) - Cost Basis (base)
        """
        # Convert original cost to base currency
        # (using historical rate or current rate if historical not available)
        original_cost_base = self.convert_to_base_currency(
            position.original_cost_basis,
            position.currency,
            base_currency
        )

        # Convert current value to base currency
        current_value_local = position.quantity * position.current_price
        current_value_base = self.convert_to_base_currency(
            current_value_local,
            position.currency,
            base_currency
        )

        # Calculate FX gain/loss
        fx_gain = current_value_base - original_cost_base
        fx_gain_pct = (fx_gain / original_cost_base * 100) if original_cost_base else 0

        return FXGainLoss.objects.create(
            position=position,
            currency=position.currency,
            original_cost_local=position.original_cost_basis,
            original_cost_base=original_cost_base,
            current_value_local=current_value_local,
            current_value_base=current_value_base,
            fx_gain_loss=fx_gain,
            fx_gain_loss_pct=fx_gain_pct
        )

    def get_currency_allocation(self, portfolio: Portfolio):
        """
        Get portfolio allocation by currency
        Returns breakdown of value by currency
        """
        positions = portfolio.positions.all()

        allocation = {}
        total_value = Decimal('0')

        for position in positions:
            # Convert to base currency (usually USD)
            value = position.quantity * position.current_price
            value_base = self.convert_to_base_currency(
                value,
                position.currency,
                'USD'
            )

            currency = position.currency
            allocation[currency] = allocation.get(currency, Decimal('0')) + value_base
            total_value += value_base

        # Calculate percentages
        allocation_pct = {
            currency: (value / total_value * 100)
            for currency, value in allocation.items()
        }

        return {
            'allocation': allocation,
            'allocation_pct': allocation_pct,
            'total_value': total_value
        }

    def update_exchange_rates(self):
        """
        Background task to update exchange rates
        Runs every hour
        """
        # Major currencies: USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY']

        for base in currencies:
            for quote in currencies:
                if base != quote:
                    try:
                        rate = self._fetch_rate_from_api(base, quote)
                        Currency.objects.update_or_create(
                            code=f"{base}_{quote}",
                            defaults={
                                'name': f"{base} to {quote}",
                                'exchange_rate_to_usd': rate
                            }
                        )
                    except Exception as e:
                        logger.error(f"Failed to fetch rate for {base}/{quote}: {e}")
```

### 3. API Endpoints

```python
# apps/backend/src/investments/api/currency.py
from ninja import Router

router = Router()

@router.get("/currencies/rates")
def get_exchange_rates(request, base: str = 'USD'):
    """Get all exchange rates for base currency"""
    pass

@router.get("/currencies/convert")
def convert_currency(request, amount: float, from: str, to: str):
    """Convert amount between currencies"""
    pass

@router.get("/portfolios/{portfolio_id}/currency-allocation")
def get_currency_allocation(request, portfolio_id: int):
    """Get portfolio breakdown by currency"""
    pass

@router.get("/positions/{position_id}/fx-gains")
def get_fx_gains(request, position_id: int):
    """Get FX gains/losses for position"""
    pass

@router.post("/positions/{position_id}/set-currency")
def set_position_currency(request, position_id: int, currency: str):
    """Set currency for position (for existing positions)"""
    pass
```

### 4. Frontend Components

```typescript
// apps/frontend/src/components/portfolio/CurrencyAllocationChart.tsx
export function CurrencyAllocationChart({ portfolioId }: Props) {
  // Pie chart of portfolio by currency
  - Show value in each currency
  - Show percentage allocation
  - List positions in each currency
  - FX gains/losses summary
}

// apps/frontend/src/components/portfolio/CurrencyConverter.tsx
export function CurrencyConverter() {
  // Simple currency calculator
  // Amount input, from/to currency
  // Show conversion result
  // Show exchange rate used
}

// apps/frontend/src/components/portfolio/PositionCurrencyBadge.tsx
export function PositionCurrencyBadge({ position }: Props) {
  // Show currency symbol (€, £, ¥)
  - Hover to see FX gains/losses
  - Click to convert to base currency
}

// apps/frontend/src/components/portfolio/MultiCurrencySummary.tsx
export function MultiCurrencySummary({ portfolioId }: Props) {
  // Summary table:
  // Currency | Positions | Value (Local) | Value (Base) | FX Gain/Loss
  // Total portfolio value in base currency
  // Currency allocation percentages
}
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Positions can have different currencies
- [ ] Automatic currency conversion
- [ ] FX gains/losses calculated and tracked
- [ ] Real-time exchange rates (hourly updates)
- [ ] Currency allocation breakdown
- [ ] Portfolio value in base currency
- [ ] Convert individual position values
- [ ] Multi-currency summary table
- [ ] Currency badges on positions
- [ ] Historical FX rate tracking (if possible)
- [ ] API endpoints for all operations
- [ ] Frontend currency visualization
- [ ] Tests for currency service
- [ ] Support for major currencies (USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY)

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/backend/src/investments/models/currency.py`
- `apps/backend/src/investments/services/currency_service.py`
- `apps/backend/src/investments/api/currency.py`
- `apps/backend/src/investments/tests/test_currency.py`
- `apps/frontend/src/components/portfolio/CurrencyAllocationChart.tsx`
- `apps/frontend/src/components/portfolio/CurrencyConverter.tsx`
- `apps/frontend/src/components/portfolio/MultiCurrencySummary.tsx`

### Modify:
- `apps/backend/src/investments/models/position.py` (add currency field)
- All portfolio display components (show currency)

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- Position model exists
- Portfolio model exists
- External FX API access

**Related Tasks:**
- None (standalone feature)

---

## 💱 SUPPORTED CURRENCIES

### Major Currencies (Phase 1)
- **USD** - US Dollar ($)
- **EUR** - Euro (€)
- **GBP** - British Pound (£)
- **JPY** - Japanese Yen (¥)
- **CAD** - Canadian Dollar (C$)
- **AUD** - Australian Dollar (A$)
- **CHF** - Swiss Franc (Fr)
- **CNY** - Chinese Yuan (¥)

### Minor Currencies (Phase 2)
- INR, SGD, HKD, NZD, SEK, NOK, DKK, MXN, BRL, KRW

### Crypto (Phase 3)
- BTC, ETH (if portfolio supports crypto)

---

## 💱 FX API OPTIONS

### Free Tier APIs
1. **exchangerate-api.io**
   - Free tier: 1,500 requests/month
   - Major currencies only
   - Hourly updates

2. **fixer.io**
   - Free tier: 1,000 requests/month
   - Historical rates available
   - EUR base only on free tier

3. **currencyapi.com**
   - Free tier: 300 requests/month
   - Real-time rates
   - Good documentation

### Paid APIs (Future)
- **OANDA** - More currencies, historical data
- **XE.com** - Business rates
- **CurrencyCloud** - Enterprise solution

---

## 📊 DELIVERABLES

1. **Models:** Currency, CurrencyConversion, FXGainLoss
2. **Service:** CurrencyService with conversion, FX calculations
3. **API:** All currency-related endpoints
4. **Frontend:** Allocation chart, converter, summary table
5. **Background Task:** Hourly rate updates
6. **Tests:** Unit tests for currency conversion
7. **Documentation:** Currency support guide

---

## 💬 NOTES

**Implementation Approach:**
- Add currency field to existing Position model (nullable initially)
- Default all existing positions to USD
- Store FX rates in database with timestamp
- Background task to update rates hourly

**FX Gains Calculation:**
- Track when position acquired (for historical rate)
- If historical rate unavailable, use current rate
- Show FX gains separate from investment gains

**User Experience:**
- Display position values in both local and base currency
- Show currency symbol prominently
- Currency allocation pie chart
- FX gains/losses highlighted

**Data Accuracy:**
- Exchange rates are mid-market (not bid/ask)
- Real-world trading would use broker FX rates
- Add disclaimer about rate accuracy

**Libraries:**
- Backend: `requests` for FX API
- Frontend: Charts for currency allocation

---

**Status:** ⏳ READY TO START
**Assigned To:** Backend Coder (Guido)
**User Value:** MEDIUM - international investors need this

---

💱 *C-039: Multi-Currency Portfolio Support*
*Hold assets in multiple currencies - EUR, GBP, JPY, with automatic conversion*
