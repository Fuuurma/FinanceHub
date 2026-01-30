# C-031: Bond Yield Calculator & Fixed Income Tools

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 12-16 hours  
**Dependencies:** C-005 (Backend Improvements), C-027 (Universal Search)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive bond yield calculator with YTM (Yield to Maturity), duration, convexity calculations, and fixed income analytics tools for government, corporate, and municipal bonds.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 9.2 - Fixed Income):**

- Government bonds (US Treasuries, global)
- Corporate bonds
- Municipal bonds
- Bond yields & curves
- Bond calculators (YTM, duration, convexity)

---

## ✅ CURRENT STATE

**What exists:**
- Basic asset tracking for stocks/crypto
- Price data models

**What's missing:**
- Bond-specific calculations (YTM, duration, convexity)
- Bond yield curve visualization
- Fixed income analytics
- Bond pricing models
- Fixed income instrument support

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (3-4 hours)

**Create `apps/backend/src/investments/models/fixed_income.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from .asset import Asset

User = get_user_model()

class Bond(models.Model):
    """Fixed income securities"""
    
    BOND_TYPE_CHOICES = [
        ('government', 'Government Bond'),
        ('corporate', 'Corporate Bond'),
        ('municipal', 'Municipal Bond'),
        ('agency', 'Agency Bond'),
        ('treasury', 'US Treasury'),
    ]
    
    COUPON_TYPE_CHOICES = [
        ('fixed', 'Fixed Rate'),
        ('floating', 'Floating Rate'),
        ('zero', 'Zero Coupon'),
        ('inflation_linked', 'Inflation-Linked (TIPS)'),
    ]
    
    # Link to asset
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='bond_details')
    
    # Bond type
    bond_type = models.CharField(max_length=20, choices=BOND_TYPE_CHOICES)
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPE_CHOICES)
    
    # Bond terms
    face_value = models.DecimalField(max_digits=20, decimal_places=2)  # Par value
    coupon_rate = models.DecimalField(max_digits=10, decimal_places=6)  # Annual coupon rate
    issue_date = models.DateField()
    maturity_date = models.DateField()
    
    # Pricing
    current_price = models.DecimalField(max_digits=20, decimal_places=4)  # % of par
    yield_to_maturity = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    yield_to_call = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    
    # Call features
    callable = models.BooleanField(default=False)
    call_date = models.DateField(null=True, blank=True)
    call_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # Credit rating
    credit_rating_moody = models.CharField(max_length=10, blank=True)
    credit_rating_sp = models.CharField(max_length=10, blank=True)
    credit_rating_fitch = models.CharField(max_length=10, blank=True)
    
    # Additional features
    sinking_fund = models.BooleanField(default=False)
    convertible = models.BooleanField(default=False)
    conversion_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Tax treatment
    tax_exempt = models.BooleanField(default=False)  # Municipal bonds
    federal_tax_exempt = models.BooleanField(default=False)
    state_tax_exempt = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['bond_type', 'maturity_date']),
            models.Index(fields=['maturity_date']),
            models.Index(fields=['credit_rating_sp']),
        ]
        ordering = ['maturity_date']

class BondYieldCurve(models.Model):
    """Yield curve data points"""
    
    curve_date = models.DateField()
    tenor_days = models.IntegerField()  # Time to maturity in days
    tenor_label = models.CharField(max_length=20)  # e.g., "2Y", "5Y", "10Y"
    yield_rate = models.DecimalField(max_digits=10, decimal_places=6)
    
    # Curve type
    curve_type = models.CharField(max_length=20)  # treasury, corporate_aaa, corporate_bbb, municipal
    
    class Meta:
        indexes = [
            models.Index(fields=['curve_date', 'curve_type', 'tenor_days']),
        ]
        ordering = ['curve_date', 'tenor_days']

class BondCalculation(models.Model):
    """Cached bond calculations"""
    
    bond = models.ForeignKey(Bond, on_delete=models.CASCADE, related_name='calculations')
    
    # Calculation parameters
    calculation_date = models.DateTimeField(auto_now_add=True)
    settlement_date = models.DateField()
    
    # Results
    yield_to_maturity = models.DecimalField(max_digits=10, decimal_places=6)
    yield_to_call = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    
    # Duration measures
    macaulay_duration = models.DecimalField(max_digits=10, decimal_places=4)
    modified_duration = models.DecimalField(max_digits=10, decimal_places=4)
    effective_duration = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # Convexity
    convexity = models.DecimalField(max_digits=15, decimal_places=6)
    effective_convexity = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    
    # Risk metrics
    pv01 = models.DecimalField(max_digits=10, decimal_places=2)  # Price value of 1 basis point
    dv01 = models.DecimalField(max_digits=10, decimal_places=2)  # Dollar value of 1 basis point
    
    # Cash flow summary
    total_cash_flows = models.IntegerField()
    total_coupon_payments = models.DecimalField(max_digits=20, decimal_places=2)
    
    class Meta:
        indexes = [
            models.Index(fields=['bond', '-calculation_date']),
        ]
        ordering = ['-calculation_date']

class TreasuryRate(models.Model):
    """Current Treasury rates for benchmarking"""
    
    TENOR_CHOICES = [
        ('1M', '1 Month'),
        ('3M', '3 Month'),
        ('6M', '6 Month'),
        ('1Y', '1 Year'),
        ('2Y', '2 Year'),
        ('3Y', '3 Year'),
        ('5Y', '5 Year'),
        ('7Y', '7 Year'),
        ('10Y', '10 Year'),
        ('20Y', '20 Year'),
        ('30Y', '30 Year'),
    ]
    
    tenor = models.CharField(max_length=5, choices=TENOR_CHOICES, unique=True)
    rate = models.DecimalField(max_digits=10, decimal_places=6)
    rate_date = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['tenor']
```

---

### **Phase 2: Bond Calculation Service** (5-6 hours)

**Create `apps/backend/src/investments/services/bond_service.py`:**

```python
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import date, timedelta
from decimal import Decimal
from django.db import transaction
from investments.models.fixed_income import Bond, BondYieldCurve, BondCalculation, TreasuryRate
from investments.models.asset import Asset

class BondCalculationService:
    
    def calculate_ytm(
        self,
        bond: Bond,
        current_price: float,
        settlement_date: date
    ) -> Dict:
        """
        Calculate Yield to Maturity using Newton-Raphson method
        
        YTM = discount rate that equates PV of cash flows to current price
        """
        face_value = float(bond.face_value)
        coupon_rate = float(bond.coupon_rate)
        coupon_payment = face_value * coupon_rate / 2  # Semi-annual
        
        # Calculate time to maturity in years
        years_to_maturity = (bond.maturity_date - settlement_date).days / 365.25
        periods = int(years_to_maturity * 2)  # Semi-annual periods
        
        # Newton-Raphson iteration
        ytm = coupon_rate  # Initial guess
        tolerance = 1e-8
        max_iterations = 100
        
        for i in range(max_iterations):
            # Calculate price with current YTM guess
            price = 0
            for period in range(1, periods + 1):
                coupon_pv = coupon_payment / ((1 + ytm/2) ** period)
                price += coupon_pv
            
            # Add principal repayment
            price += face_value / ((1 + ytm/2) ** periods)
            
            # Calculate derivative (price duration)
            derivative = 0
            for period in range(1, periods + 1):
                derivative += -period * coupon_payment / (2 * ((1 + ytm/2) ** (period + 1)))
            derivative += -periods * face_value / (2 * ((1 + ytm/2) ** (periods + 1)))
            
            # Update YTM
            new_ytm = ytm - (price - current_price * face_value / 100) / derivative
            
            if abs(new_ytm - ytm) < tolerance:
                ytm = new_ytm
                break
            
            ytm = new_ytm
        
        return {
            'yield_to_maturity': ytm,
            'price': price,
            'iterations': i + 1
        }
    
    def calculate_macaulay_duration(
        self,
        bond: Bond,
        ytm: float,
        settlement_date: date
    ) -> Dict:
        """
        Calculate Macaulay Duration
        Measures weighted average time to receive cash flows
        """
        face_value = float(bond.face_value)
        coupon_rate = float(bond.coupon_rate)
        coupon_payment = face_value * coupon_rate / 2
        
        years_to_maturity = (bond.maturity_date - settlement_date).days / 365.25
        periods = int(years_to_maturity * 2)
        
        # Calculate weighted present value
        weighted_pv = 0
        pv = 0
        
        for period in range(1, periods + 1):
            years = period / 2  # Semi-annual
            discount_factor = 1 / ((1 + ytm/2) ** period)
            
            coupon_pv = coupon_payment * discount_factor
            weighted_pv += years * coupon_pv
            pv += coupon_pv
        
        # Add principal
        principal_pv = face_value * discount_factor
        years_maturity = periods / 2
        weighted_pv += years_maturity * principal_pv
        pv += principal_pv
        
        macaulay_duration = weighted_pv / pv
        modified_duration = macaulay_duration / (1 + ytm/2)
        
        return {
            'macaulay_duration': macaulay_duration,
            'modified_duration': modified_duration,
            'present_value': pv
        }
    
    def calculate_convexity(
        self,
        bond: Bond,
        ytm: float,
        settlement_date: date
    ) -> float:
        """
        Calculate convexity
        Measures the curvature of the price-yield relationship
        """
        face_value = float(bond.face_value)
        coupon_rate = float(bond.coupon_rate)
        coupon_payment = face_value * coupon_rate / 2
        
        years_to_maturity = (bond.maturity_date - settlement_date).days / 365.25
        periods = int(years_to_maturity * 2)
        
        convexity = 0
        pv = 0
        
        for period in range(1, periods + 1):
            years = period / 2
            discount_factor = 1 / ((1 + ytm/2) ** period)
            
            cash_flow = coupon_payment
            if period == periods:
                cash_flow += face_value
            
            cf_pv = cash_flow * discount_factor
            pv += cf_pv
            
            # Convexity contribution
            convexity += (period * (period + 1) * cf_pv) / ((1 + ytm/2) ** 2)
        
        convexity = convexity / (pv * 4)  # Convert to annual
        
        return convexity
    
    def calculate_pv01(
        self,
        bond: Bond,
        modified_duration: float
    ) -> Dict:
        """
        Calculate PV01 and DV01
        Price change for 1 basis point change in yield
        """
        face_value = float(bond.face_value)
        current_price = float(bond.current_price)
        
        # PV01: Price value of 1 bp (for $100 face value)
        pv01 = -modified_duration * current_price * 0.0001
        
        # DV01: Dollar value of 1 bp (for actual face value)
        dv01 = pv01 * face_value / 100
        
        return {
            'pv01': abs(pv01),
            'dv01': abs(dv01)
        }
    
    @transaction.atomic
    def calculate_bond_metrics(
        self,
        bond_id: int,
        settlement_date: Optional[date] = None
    ) -> Dict:
        """
        Calculate all bond metrics and cache results
        """
        if settlement_date is None:
            settlement_date = date.today()
        
        bond = Bond.objects.get(id=bond_id)
        current_price = float(bond.current_price)
        
        # Calculate YTM
        ytm_result = self.calculate_ytm(bond, current_price, settlement_date)
        ytm = ytm_result['yield_to_maturity']
        
        # Calculate duration
        duration_result = self.calculate_macaulay_duration(bond, ytm, settlement_date)
        
        # Calculate convexity
        convexity = self.calculate_convexity(bond, ytm, settlement_date)
        
        # Calculate PV01/DV01
        price_value_result = self.calculate_pv01(
            bond, 
            duration_result['modified_duration']
        )
        
        # Calculate YTC if callable
        ytc = None
        if bond.callable and bond.call_date:
            ytc_result = self._calculate_ytc(bond, current_price, settlement_date)
            ytc = ytc_result['yield_to_call']
        
        # Cache results
        calculation = BondCalculation.objects.create(
            bond=bond,
            settlement_date=settlement_date,
            yield_to_maturity=Decimal(str(ytm)),
            yield_to_call=Decimal(str(ytc)) if ytc else None,
            macaulay_duration=Decimal(str(duration_result['macaulay_duration'])),
            modified_duration=Decimal(str(duration_result['modified_duration'])),
            convexity=Decimal(str(convexity)),
            pv01=Decimal(str(price_value_result['pv01'])),
            dv01=Decimal(str(price_value_result['dv01'])),
            total_cash_flows=int((bond.maturity_date - settlement_date).days / 182.5),  # Approx
            total_coupon_payments=Decimal(str(float(bond.face_value) * float(bond.coupon_rate) * 
                ((bond.maturity_date - settlement_date).days / 365.25)))
        )
        
        return {
            'calculation_id': calculation.id,
            'yield_to_maturity': ytm,
            'yield_to_call': ytc,
            'macaulay_duration': duration_result['macaulay_duration'],
            'modified_duration': duration_result['modified_duration'],
            'convexity': convexity,
            'pv01': price_value_result['pv01'],
            'dv01': price_value_result['dv01']
        }
    
    def _calculate_ytc(
        self,
        bond: Bond,
        current_price: float,
        settlement_date: date
    ) -> Dict:
        """Calculate Yield to Call"""
        face_value = float(bond.face_value)
        coupon_rate = float(bond.coupon_rate)
        coupon_payment = face_value * coupon_rate / 2
        
        # Time to call
        years_to_call = (bond.call_date - settlement_date).days / 365.25
        periods = int(years_to_call * 2)
        
        # Newton-Raphson
        ytc = coupon_rate
        tolerance = 1e-8
        max_iterations = 100
        
        for i in range(max_iterations):
            price = 0
            for period in range(1, periods + 1):
                price += coupon_payment / ((1 + ytc/2) ** period)
            
            # Add call price
            call_price = float(bond.call_price) if bond.call_price else face_value
            price += call_price / ((1 + ytc/2) ** periods)
            
            if abs(price - current_price * face_value / 100) < tolerance:
                break
            
            ytc = ytc * (price / (current_price * face_value / 100))
        
        return {'yield_to_call': ytc}
    
    def get_yield_curve(
        self,
        curve_type: str = 'treasury',
        curve_date: Optional[date] = None
    ) -> List[Dict]:
        """Get yield curve data"""
        if curve_date is None:
            curve_date = date.today()
        
        curve_points = BondYieldCurve.objects.filter(
            curve_type=curve_type,
            curve_date=curve_date
        ).order_by('tenor_days')
        
        return [
            {
                'tenor_label': point.tenor_label,
                'tenor_days': point.tenor_days,
                'yield_rate': float(point.yield_rate)
            }
            for point in curve_points
        ]
    
    def calculate_spot_rates(
        self,
        coupon_bonds: List[Bond],
        settlement_date: date
    ) -> Dict:
        """
        Bootstrap spot rates from coupon bonds
        Uses bootstrapping method to derive zero-coupon yield curve
        """
        spot_rates = {}
        
        # Sort bonds by maturity
        sorted_bonds = sorted(coupon_bonds, key=lambda b: b.maturity_date)
        
        for bond in sorted_bonds:
            periods = int((bond.maturity_date - settlement_date).days / 182.5)
            face_value = float(bond.face_value)
            coupon_payment = face_value * float(bond.coupon_rate) / 2
            price = float(bond.current_price) * face_value / 100
            
            # Calculate present value of known coupon payments
            pv_known_coupons = 0
            for period, spot_rate in spot_rates.items():
                if period < periods:
                    pv_known_coupons += coupon_payment / ((1 + spot_rate/2) ** period)
            
            # Solve for spot rate
            remaining_cash_flows = price - pv_known_coupons
            final_cash_flow = face_value + coupon_payment
            
            spot_rate = (final_cash_flows / remaining_cash_flows) ** (1/periods) - 1
            spot_rates[periods] = spot_rate
        
        return spot_rates
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/bonds.py`:**

```python
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from investments.services.bond_service import BondCalculationService
from investments.models.fixed_income import Bond, TreasuryRate

router = Router(tags=['bonds'])
bond_service = BondCalculationService()

class BondCalculationSchema(Schema):
    settlement_date: str = None  # YYYY-MM-DD format

@router.post("/bonds/{bond_id}/calculate")
def calculate_bond_metrics(request, bond_id: int, data: BondCalculationSchema):
    """Calculate all bond metrics (YTM, duration, convexity)"""
    bond = get_object_or_404(Bond, id=bond_id)
    
    from datetime import datetime
    settlement_date = None
    if data.settlement_date:
        settlement_date = datetime.strptime(data.settlement_date, '%Y-%m-%d').date()
    
    result = bond_service.calculate_bond_metrics(bond_id, settlement_date)
    return result

@router.get("/bonds/{bond_id}/ytm")
def calculate_ytm(request, bond_id: int):
    """Calculate Yield to Maturity"""
    bond = get_object_or_404(Bond, id=bond_id)
    result = bond_service.calculate_ytm(bond, float(bond.current_price), date.today())
    return result

@router.get("/bonds/{bond_id}/duration")
def calculate_duration(request, bond_id: int):
    """Calculate Macaulay and Modified Duration"""
    bond = get_object_or_404(Bond, id=bond_id)
    ytm = float(bond.yield_to_maturity) if bond.yield_to_maturity else 0.05
    result = bond_service.calculate_macaulay_duration(bond, ytm, date.today())
    return result

@router.get("/bonds/curve/{curve_type}")
def get_yield_curve(request, curve_type: str = 'treasury'):
    """Get yield curve data"""
    return bond_service.get_yield_curve(curve_type)

@router.get("/bonds/treasury-rates")
def get_treasury_rates(request):
    """Get current Treasury rates"""
    rates = TreasuryRate.objects.all()
    return [
        {
            'tenor': rate.tenor,
            'rate': float(rate.rate),
            'rate_date': rate.rate_date.isoformat()
        }
        for rate in rates
    ]

@router.post("/bonds/spot-rates")
def calculate_spot_rates(request, bond_ids: list):
    """Bootstrap spot rates from coupon bonds"""
    bonds = Bond.objects.filter(id__in=bond_ids)
    spot_rates = bond_service.calculate_spot_rates(list(bonds), date.today())
    return spot_rates
```

---

## 📋 DELIVERABLES

- [ ] Bond, BondYieldCurve, BondCalculation, TreasuryRate models
- [ ] BondCalculationService with YTM, duration, convexity calculations
- [ ] 6 API endpoints for bond analysis
- [ ] Database migrations
- [ ] Unit tests (coverage >80%)
- [ ] API documentation
- [ ] Sample bond data seeding

---

## ✅ ACCEPTANCE CRITERIA

- [ ] YTM calculated accurately using Newton-Raphson method
- [ ] Macaulay duration matches manual calculations
- [ ] Modified duration = Macaulay / (1 + YTM/2)
- [ ] Convexity correctly measures curvature
- [ ] PV01/DV01 accurate to 2 decimal places
- [ ] Yield curve data retrieved correctly
- [ ] Spot rate bootstrapping working
- [ ] All bond types supported (government, corporate, municipal)
- [ ] Callable bonds include YTC calculation
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- YTM calculation converges in <50 iterations
- Duration accurate to 4 decimal places
- API response time <500ms
- Support for bonds with 30+ year maturity
- Spot rate bootstrapping handles 10+ bonds

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/031-bond-yield-calculator.md
