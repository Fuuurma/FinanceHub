# 💰 TASK: C-031 - Bond Yield Calculator

**Task ID:** C-031
**Created:** February 1, 2026
**Assigned To:** Backend Coder (Linus)
**Status:** ⏳ PENDING
**Priority:** P2 MEDIUM
**Estimated Time:** 12-16 hours
**Deadline:** February 20, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Create a comprehensive bond yield calculator that supports:
- Current yield calculation
- Yield to Maturity (YTM)
- Yield to Call (YTC)
- Zero-coupon bond yield
- Treasury bill yield
- Bond price calculation

---

## 📋 REQUIREMENTS

### 1. Bond Calculations Service

**Models:**
```python
# apps/backend/src/investments/models/bonds.py
class Bond(models.Model):
    symbol = CharField()
    bond_type = CharField()  # 'treasury', 'corporate', 'municipal', 'agency'
    face_value = DecimalField()  # Par value (usually $1000)
    coupon_rate = DecimalField()  # Annual coupon rate
    current_price = DecimalField()
    maturity_date = DateField()
    call_date = DateField(null=True)
    call_price = DecimalField(null=True)
    frequency = IntegerField()  # Coupons per year (1, 2, or 4)
    rating = CharField()  # Credit rating (AAA, AA, A, BBB, etc.)

class BondCalculation(models.Model):
    bond = ForeignKey(Bond)
    calculation_type = CharField()  # 'current_yield', 'ytm', 'ytc'
    yield_value = DecimalField()
    calculated_at = DateTimeField(auto_now_add=True)
```

**Service:**
```python
# apps/backend/src/investments/services/bond_calculator_service.py
from decimal import Decimal
import math

class BondCalculatorService:
    def current_yield(self, bond: Bond) -> Decimal:
        """
        Current Yield = Annual Coupon Payment / Current Price
        """
        annual_coupon = bond.face_value * bond.coupon_rate
        return (annual_coupon / bond.current_price) * 100

    def yield_to_maturity(self, bond: Bond) -> Decimal:
        """
        Yield to Maturity (YTM) using Newton-Raphson method
        Approximates the discount rate that equates PV of cash flows to price
        """
        # Implementation requires numerical method
        # Solve for YTM in: Price = Σ(Coupon/(1+YTM)^t) + Face/(1+YTM)^n
        pass

    def yield_to_call(self, bond: Bond) -> Decimal:
        """
        Yield to Call (YTC) if bond is callable
        Similar to YTM but uses call date and call price
        """
        pass

    def zero_coupon_yield(self, price: Decimal, face_value: Decimal,
                         years_to_maturity: float) -> Decimal:
        """
        Zero-Coupon Bond Yield = (Face/Price)^(1/n) - 1
        """
        return ((face_value / price) ** (1 / years_to_maturity) - 1) * 100

    def treasury_bill_yield(self, discount_rate: Decimal, days_to_maturity: int) -> Decimal:
        """
        T-Bill Yield = (360 * Discount) / (360 - (Discount * Days))
        Bank Discount Yield to Investment Yield conversion
        """
        pass

    def bond_price(self, face_value: Decimal, coupon_rate: Decimal,
                   ytm: Decimal, years: int, frequency: int) -> Decimal:
        """
        Calculate bond price given YTM
        Price = Σ(Coupon/(1+YTM/frequency)^t) + Face/(1+YTM/frequency)^n
        """
        pass
```

### 2. API Endpoints

```python
# apps/backend/src/investments/api/bonds.py
from ninja import Router

router = Router()

@router.get("/bonds/calculate/yield")
def calculate_yield(request, bond_id: int, calculation_type: str):
    """Calculate specified yield type for bond"""
    pass

@router.post("/bonds/calculate/custom")
def calculate_custom_yield(request, data: BondCalculationInput):
    """Calculate yield for custom bond parameters"""
    pass

@router.get("/bonds/compare")
def compare_bonds(request, bond_ids: List[int]):
    """Compare yields across multiple bonds"""
    pass
```

### 3. Frontend Component

```typescript
// apps/frontend/src/components/bonds/BondYieldCalculator.tsx
interface BondInput {
  faceValue: number;
  couponRate: number;
  currentPrice: number;
  maturityDate: Date;
  callDate?: Date;
  callPrice?: number;
  frequency: number; // 1, 2, or 4
}

interface BondResults {
  currentYield: number;
  ytm: number;
  ytc?: number;
  bondPrice: number;
}

export function BondYieldCalculator() {
  // Form inputs for bond parameters
  // Calculate yields on button click
  // Display results with explanations
  // Compare multiple bonds feature
}
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Current yield calculated correctly
- [ ] YTM calculated with <0.1% error
- [ ] YTC calculated for callable bonds
- [ ] Zero-coupon bond yield supported
- [ ] T-Bill yield conversion (discount to investment yield)
- [ ] Bond price calculator (inverse of YTM)
- [ ] API endpoints for all calculations
- [ ] Frontend calculator with input validation
- [ ] Bond comparison feature (compare 2+ bonds)
- [ ] Tests for all calculation methods
- [ ] Error handling for invalid inputs
- [ ] Decimal precision maintained (4 decimal places)

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/backend/src/investments/models/bonds.py`
- `apps/backend/src/investments/services/bond_calculator_service.py`
- `apps/backend/src/investments/api/bonds.py`
- `apps/backend/src/investments/tests/test_bond_calculator.py`
- `apps/frontend/src/components/bonds/BondYieldCalculator.tsx`

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- Decimal precision handling (S-009 should be complete)
- REST API framework (Django Ninja)

**Related Tasks:**
- S-009: Float Precision Fix (CRITICAL dependency)

---

## 📐 CALCULATION FORMULAS

### Current Yield
```
Current Yield = (Annual Coupon Payment / Current Price) × 100
```

### Yield to Maturity (Approximation)
```
YTM ≈ [C + (F - P) / n] / [(F + P) / 2]

Where:
C = Annual coupon payment
F = Face value
P = Current price
n = Years to maturity
```

### Zero-Coupon Yield
```
Yield = (Face Value / Current Price)^(1 / n) - 1

Where:
n = Years to maturity
```

### T-Bill Discount to Yield
```
Investment Yield = (360 × Discount) / (360 - (Discount × Days))

Where:
Discount = Bank discount rate
Days = Days to maturity
```

---

## 📊 DELIVERABLES

1. **Models:** Bond, BondCalculation
2. **Service:** BondCalculatorService with all calculation methods
3. **API:** Calculate, compare endpoints
4. **Frontend:** Bond yield calculator component
5. **Tests:** Unit tests for all calculations
6. **Documentation:** Formula explanations in UI

---

## 💬 NOTES

**Implementation Approach:**
- Use `decimal.Decimal` for all financial calculations
- Implement Newton-Raphson iteration for YTM precision
- Cache calculation results for performance
- Support annual, semi-annual, quarterly coupon payments

**Edge Cases:**
- Handle bonds with <1 year to maturity
- Handle zero-coupon bonds
- Handle callable bonds (YTC)
- Handle negative yields (possible in some markets)
- Handle very long-dated bonds (30+ years)

**Libraries:**
- `numpy` for numerical calculations (optional)
- `decimal` for precision (required)

---

**Status:** ⏳ READY TO START
**Assigned To:** Backend Coder (Linus)
**Dependency:** S-009 (Float Precision) must be complete first

---

💰 *C-031: Bond Yield Calculator*
*Calculate bond yields with precision - YTM, YTC, current yield*
