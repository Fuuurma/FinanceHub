# C-023: Options Greeks Calculator & Analysis

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 12-16 hours  
**Dependencies:** None  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive options analysis tools including Greeks calculation (delta, gamma, theta, vega), P&L charts, implied volatility surface, and options strategy builder.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 5.3 - Derivatives Risk):**

- Options Greeks (delta, gamma, theta, vega)
- Options P&L chart
- Implied volatility surface
- Historical volatility vs implied volatility
- Options strategy builder

**From Features Specification (Section 9.3 - Derivatives):**

- Options (calls, puts)
- Options chains visualization
- Implied volatility skew
- Futures term structure

---

## ✅ CURRENT STATE

**What exists:**
- Basic asset tracking
- Portfolio management
- Price data for underlying assets

**What's missing:**
- Options pricing models
- Greeks calculation
- Options chain data
- Volatility surface
- Strategy analysis tools

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Options Pricing Models** (4-5 hours)

**Create `apps/backend/src/investments/lib/options_pricing.py`:**

```python
import numpy as np
from scipy.stats import norm
from typing import Dict, Tuple
from datetime import datetime, timedelta

class OptionsPricing:
    """
    Options pricing using Black-Scholes model
    Supports European options on stocks without dividends
    """
    
    @staticmethod
    def black_scholes(
        S: float,  # Current stock price
        K: float,  # Strike price
        T: float,  # Time to maturity (years)
        r: float,  # Risk-free rate
        sigma: float,  # Volatility
        option_type: str = 'call'  # 'call' or 'put'
    ) -> Dict[str, float]:
        """
        Calculate option price and Greeks using Black-Scholes model
        
        Returns: {price, delta, gamma, theta, vega, rho}
        """
        # Calculate d1 and d2
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Calculate price
        if option_type == 'call':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            delta = norm.cdf(d1)
        else:  # put
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            delta = -norm.cdf(-d1)
        
        # Calculate Greeks
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # Per 1% change in volatility
        
        if option_type == 'call':
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                     r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        else:
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + 
                     r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        
        rho = (K * T * np.exp(-r * T) * norm.cdf(d2) / 100) if option_type == 'call' else \
              (-K * T * np.exp(-r * T) * norm.cdf(-d2) / 100)
        
        return {
            'price': price,
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho,
            'd1': d1,
            'd2': d2
        }
    
    @staticmethod
    def calculate_implied_volatility(
        market_price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        option_type: str = 'call',
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> float:
        """
        Calculate implied volatility using Newton-Raphson method
        
        Returns: Implied volatility (sigma)
        """
        sigma = 0.5  # Initial guess
        
        for i in range(max_iterations):
            # Calculate price and vega at current sigma
            result = OptionsPricing.black_scholes(S, K, T, r, sigma, option_type)
            price = result['price']
            vega = result['vega'] * 100  # Convert back from per 1%
            
            # Check convergence
            diff = price - market_price
            if abs(diff) < tolerance:
                return sigma
            
            # Newton-Raphson update
            sigma = sigma - diff / vega
            
            # Ensure sigma stays positive
            if sigma < 0.01:
                sigma = 0.01
        
        return sigma
    
    @staticmethod
    def calculate_profit_loss(
        option_type: str,
        position_type: str,  # 'long' or 'short'
        premium: float,
        S: float,  # Current stock price
        K: float,  # Strike price
        contracts: int = 1,
        multiplier: int = 100  # Contract size (usually 100 shares)
    ) -> Dict[str, float]:
        """
        Calculate P&L for options position at expiration
        
        Returns: {pnl, intrinsic_value, profit, loss}
        """
        contract_size = contracts * multiplier
        
        if option_type == 'call':
            intrinsic_value = max(0, S - K)
        else:  # put
            intrinsic_value = max(0, K - S)
        
        if position_type == 'long':
            pnl = (intrinsic_value - premium) * contract_size
        else:  # short
            pnl = (premium - intrinsic_value) * contract_size
        
        return {
            'pnl': pnl,
            'intrinsic_value': intrinsic_value,
            'premium_paid': premium * contract_size if position_type == 'long' else -premium * contract_size,
            'breakeven': K + premium if option_type == 'call' and position_type == 'long' else \
                        K - premium if option_type == 'put' and position_type == 'long' else \
                        K + premium if option_type == 'put' and position_type == 'short' else \
                        K - premium
        }
    
    @staticmethod
    def generate_payoff_diagram(
        strategy: Dict,
        price_range: Tuple[float, float],
        num_points: int = 100
    ) -> Dict:
        """
        Generate P&L data for options strategy
        
        strategy: {
            'legs': [
                {'type': 'call', 'position': 'long', 'strike': 100, 'premium': 5, 'contracts': 1},
                {'type': 'put', 'position': 'long', 'strike': 95, 'premium': 3, 'contracts': 1}
            ]
        }
        
        Returns: {prices, pnl, breakeven_points, max_profit, max_loss}
        """
        prices = np.linspace(price_range[0], price_range[1], num_points)
        total_pnl = []
        
        for price in prices:
            position_pnl = 0
            for leg in strategy['legs']:
                result = OptionsPricing.calculate_profit_loss(
                    leg['type'],
                    leg['position'],
                    leg['premium'],
                    price,
                    leg['strike'],
                    leg.get('contracts', 1)
                )
                position_pnl += result['pnl']
            
            total_pnl.append(position_pnl)
        
        # Find breakeven points
        breakeven_points = []
        for i in range(len(prices) - 1):
            if (total_pnl[i] < 0 and total_pnl[i + 1] > 0) or \
               (total_pnl[i] > 0 and total_pnl[i + 1] < 0):
                # Linear interpolation for breakeven price
                x1, x2 = prices[i], prices[i + 1]
                y1, y2 = total_pnl[i], total_pnl[i + 1]
                breakeven = x1 - y1 * (x2 - x1) / (y2 - y1)
                breakeven_points.append(breakeven)
        
        # Calculate max profit/loss
        max_profit = max(total_pnl) if max(total_pnl) != float('inf') else None
        max_loss = min(total_pnl) if min(total_pnl) != float('-inf') else None
        
        return {
            'prices': prices.tolist(),
            'pnl': total_pnl,
            'breakeven_points': breakeven_points,
            'max_profit': max_profit,
            'max_loss': max_loss
        }
```

---

### **Phase 2: Options Data Models** (2-3 hours)

**Create `apps/backend/src/investments/models/options.py`:**

```python
from django.db import models
from .asset import Asset

class OptionContract(models.Model):
    """Options contract data"""
    
    OPTION_TYPE_CHOICES = [
        ('call', 'Call'),
        ('put', 'Put'),
    ]
    
    # Basic info
    underlying_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='options')
    option_type = models.CharField(max_length=4, choices=OPTION_TYPE_CHOICES)
    strike_price = models.DecimalField(max_digits=20, decimal_places=4)
    
    # Expiration
    expiration_date = models.DateTimeField()
    days_to_expiration = models.IntegerField()
    
    # Pricing data
    bid = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    ask = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    last_price = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    volume = models.IntegerField(null=True)
    open_interest = models.IntegerField(null=True)
    
    # Greeks
    implied_volatility = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    delta = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    gamma = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    theta = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    vega = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    
    # Market data
    iv_rank = models.DecimalField(max_digits=5, decimal_places=2, null=True)  # IV rank (0-100)
    iv_percentile = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['underlying_asset', 'option_type', 'strike_price', 'expiration_date']]
        indexes = [
            models.Index(fields=['underlying_asset', 'expiration_date']),
            models.Index(fields=['strike_price']),
        ]

class VolatilitySurface(models.Model):
    """Implied volatility surface data"""
    
    underlying_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='volatility_surfaces')
    
    # Surface data (JSON grid of strike x expiry -> IV)
    surface_data = models.JSONField()  # {strike: {expiry_date: iv}}
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    base_volatility = models.DecimalField(max_digits=10, decimal_places=6)  # ATM volatility
    
    class Meta:
        ordering = ['-calculated_at']

class OptionsPosition(models.Model):
    """User's options positions"""
    
    POSITION_TYPE_CHOICES = [
        ('long', 'Long'),
        ('short', 'Short'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='options_positions')
    contract = models.ForeignKey(OptionContract, on_delete=models.CASCADE)
    
    position_type = models.CharField(max_length=10, choices=POSITION_TYPE_CHOICES)
    contracts = models.IntegerField(default=1)
    
    # Entry details
    entry_price = models.DecimalField(max_digits=20, decimal_places=4)
    entry_date = models.DateTimeField(auto_now_add=True)
    
    # Current value
    current_price = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    current_value = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    
    # P&L
    unrealized_pnl = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    unrealized_pnl_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # Greeks (portfolio level)
    portfolio_delta = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    portfolio_gamma = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    portfolio_theta = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    portfolio_vega = models.DecimalField(max_digits=20, decimal_digits=6, null=True)
    
    # Status
    is_open = models.BooleanField(default=True)
    exit_date = models.DateTimeField(null=True, blank=True)
    exit_price = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    realized_pnl = models.DecimalField(max_digits=20, decimal_digits=2, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_open']),
        ]
```

---

### **Phase 3: Options Analysis Service** (4-5 hours)

**Create `apps/backend/src/investments/services/options_service.py`:**

```python
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from investments.models.options import OptionContract, VolatilitySurface, OptionsPosition
from investments.lib.options_pricing import OptionsPricing

class OptionsAnalysisService:
    
    def __init__(self):
        self.pricing = OptionsPricing()
    
    def calculate_greeks(self, contract_id: int) -> Dict:
        """
        Calculate Greeks for options contract
        
        Returns: {delta, gamma, theta, vega, rho, price}
        """
        contract = OptionContract.objects.get(id=contract_id)
        
        # Get underlying price
        S = float(contract.underlying_asset.current_price)
        K = float(contract.strike_price)
        
        # Calculate time to expiration (in years)
        T = (contract.expiration_date - timezone.now()).days / 365.25
        
        # Risk-free rate (use 10-year Treasury as proxy)
        r = 0.045  # 4.5%
        
        # Use implied volatility if available, else estimate
        sigma = float(contract.implied_volatility) if contract.implied_volatility else 0.25
        
        # Calculate Greeks
        greeks = self.pricing.black_scholes(
            S=S,
            K=K,
            T=T,
            r=r,
            sigma=sigma,
            option_type=contract.option_type
        )
        
        # Update contract with Greeks
        contract.delta = greeks['delta']
        contract.gamma = greeks['gamma']
        contract.theta = greeks['theta']
        contract.vega = greeks['vega']
        contract.save()
        
        return greeks
    
    def calculate_portfolio_greeks(self, user_id: int) -> Dict:
        """
        Calculate portfolio-level Greeks for all open options positions
        
        Returns: {total_delta, total_gamma, total_theta, total_vega, by_position}
        """
        positions = OptionsPosition.objects.filter(
            user_id=user_id,
            is_open=True
        ).select_related('contract__underlying_asset')
        
        total_delta = 0
        total_gamma = 0
        total_theta = 0
        total_vega = 0
        
        by_position = []
        
        for position in positions:
            contract = position.contract
            multiplier = 100  # Standard US options contract
            
            # Calculate position Greeks
            position_delta = float(contract.delta or 0) * position.contracts * multiplier
            position_gamma = float(contract.gamma or 0) * position.contracts * multiplier
            position_theta = float(contract.theta or 0) * position.contracts * multiplier
            position_vega = float(contract.vega or 0) * position.contracts * multiplier
            
            # Adjust for long/short
            if position.position_type == 'short':
                position_delta *= -1
                position_gamma *= -1
                position_theta *= -1
                position_vega *= -1
            
            # Update totals
            total_delta += position_delta
            total_gamma += position_gamma
            total_theta += position_theta
            total_vega += position_vega
            
            # Update position
            position.portfolio_delta = position_delta
            position.portfolio_gamma = position_gamma
            position.portfolio_theta = position_theta
            position.portfolio_vega = position_vega
            position.save()
            
            by_position.append({
                'contract_id': contract.id,
                'symbol': contract.underlying_asset.symbol,
                'type': contract.option_type,
                'strike': float(contract.strike_price),
                'expiration': contract.expiration_date.isoformat(),
                'delta': position_delta,
                'gamma': position_gamma,
                'theta': position_theta,
                'vega': position_vega
            })
        
        return {
            'total_delta': total_delta,
            'total_gamma': total_gamma,
            'total_theta': total_theta,
            'total_vega': total_vega,
            'by_position': by_position
        }
    
    def generate_options_chain(self, underlying_id: int, expiration: str) -> List[Dict]:
        """
        Generate options chain with Greeks
        
        Returns: [{strike, call_bid, call_ask, call_iv, put_bid, put_ask, put_iv}, ...]
        """
        contracts = OptionContract.objects.filter(
            underlying_asset_id=underlying_id,
            expiration_date=expiration
        ).order_by('strike_price')
        
        chain = {}
        
        for contract in contracts:
            strike = float(contract.strike_price)
            
            if strike not in chain:
                chain[strike] = {
                    'strike': strike,
                    'call_bid': None,
                    'call_ask': None,
                    'call_iv': None,
                    'call_delta': None,
                    'put_bid': None,
                    'put_ask': None,
                    'put_iv': None,
                    'put_delta': None
                }
            
            if contract.option_type == 'call':
                chain[strike]['call_bid'] = float(contract.bid) if contract.bid else None
                chain[strike]['call_ask'] = float(contract.ask) if contract.ask else None
                chain[strike]['call_iv'] = float(contract.implied_volatility) if contract.implied_volatility else None
                chain[strike]['call_delta'] = float(contract.delta) if contract.delta else None
            else:
                chain[strike]['put_bid'] = float(contract.bid) if contract.bid else None
                chain[strike]['put_ask'] = float(contract.ask) if contract.ask else None
                chain[strike]['put_iv'] = float(contract.implied_volatility) if contract.implied_volatility else None
                chain[strike]['put_delta'] = float(contract.delta) if contract.delta else None
        
        return list(chain.values())
    
    def analyze_strategy(
        self,
        strategy: Dict,
        underlying_price: float
    ) -> Dict:
        """
        Analyze options strategy
        
        strategy: {
            'name': 'iron_condor',
            'legs': [
                {'type': 'call', 'position': 'short', 'strike': 110, 'premium': 3},
                ...
            ]
        }
        
        Returns: {payoff_diagram, greeks, max_profit, max_loss, breakeven}
        """
        # Generate payoff diagram
        price_range = (
            underlying_price * 0.8,
            underlying_price * 1.2
        )
        
        payoff = self.pricing.generate_payoff_diagram(strategy, price_range)
        
        # Calculate portfolio Greeks
        total_delta = 0
        total_gamma = 0
        total_theta = 0
        total_vega = 0
        
        for leg in strategy['legs']:
            T = 30 / 365.25  # Assume 30 days to expiration
            r = 0.045
            sigma = 0.25
            
            greeks = self.pricing.black_scholes(
                S=underlying_price,
                K=leg['strike'],
                T=T,
                r=r,
                sigma=sigma,
                option_type=leg['type']
            )
            
            multiplier = 100
            if leg['position'] == 'short':
                multiplier *= -1
            
            total_delta += greeks['delta'] * multiplier
            total_gamma += greeks['gamma'] * multiplier
            total_theta += greeks['theta'] * multiplier
            total_vega += greeks['vega'] * multiplier
        
        return {
            'strategy_name': strategy.get('name', 'custom'),
            'payoff_diagram': payoff,
            'portfolio_greeks': {
                'delta': total_delta,
                'gamma': total_gamma,
                'theta': total_theta,
                'vega': total_vega
            },
            'max_profit': payoff['max_profit'],
            'max_loss': payoff['max_loss'],
            'breakeven_points': payoff['breakeven_points']
        }
```

---

### **Phase 4: API Endpoints** (2-3 hours)

**Create `apps/backend/src/api/options.py`:**

```python
from ninja import Router
from investments.services.options_service import OptionsAnalysisService

router = Router(tags=['options'])
service = OptionsAnalysisService()

@router.get("/options/{contract_id}/greeks")
def calculate_greeks(request, contract_id: int):
    """Calculate Greeks for options contract"""
    greeks = service.calculate_greeks(contract_id)
    return greeks

@router.get("/options/portfolio/greeks")
def portfolio_greeks(request):
    """Calculate portfolio-level Greeks"""
    greeks = service.calculate_portfolio_greeks(request.auth.id)
    return greeks

@router.get("/options/{underlying_id}/chain")
def options_chain(request, underlying_id: int, expiration: str):
    """Get options chain with Greeks"""
    chain = service.generate_options_chain(underlying_id, expiration)
    return chain

@router.post("/options/analyze-strategy")
def analyze_strategy(request, strategy: dict):
    """Analyze options strategy"""
    underlying_price = strategy.get('underlying_price', 100)
    result = service.analyze_strategy(strategy, underlying_price)
    return result

@router.get("/options/strategies")
def list_strategies(request):
    """List common options strategies"""
    strategies = [
        {
            'name': 'long_call',
            'description': 'Profit from bullish move',
            'legs': [{'type': 'call', 'position': 'long', 'strike': 100, 'premium': 5}]
        },
        {
            'name': 'long_put',
            'description': 'Profit from bearish move',
            'legs': [{'type': 'put', 'position': 'long', 'strike': 100, 'premium': 3}]
        },
        {
            'name': 'iron_condor',
            'description': 'Profit from low volatility',
            'legs': [
                {'type': 'put', 'position': 'short', 'strike': 90, 'premium': 2},
                {'type': 'put', 'position': 'long', 'strike': 85, 'premium': 1},
                {'type': 'call', 'position': 'short', 'strike': 110, 'premium': 2},
                {'type': 'call', 'position': 'long', 'strike': 115, 'premium': 1}
            ]
        }
    ]
    return strategies
```

---

## 📋 DELIVERABLES

- [ ] OptionsPricing library with Black-Scholes model
- [ ] Implied volatility calculation (Newton-Raphson)
- [ ] P&L calculator for options positions
- [ ] Payoff diagram generator
- [ ] OptionContract, VolatilitySurface, OptionsPosition models
- [ ] OptionsAnalysisService with 4 methods
- [ ] 5 API endpoints
- [ ] Unit tests

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Black-Scholes pricing accurate to 4 decimal places
- [ ] Greeks calculated correctly (delta, gamma, theta, vega, rho)
- [ ] Implied volatility converges in <20 iterations
- [ ] Payoff diagrams generated for strategies
- [ ] Portfolio Greeks aggregate correctly
- [ ] Options chain formatted properly
- [ ] 3 preset strategies available
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Greeks calculation time <100ms
- Support for 1000+ options contracts
- IV calculation accuracy ±0.5%
- Payoff diagram generation <500ms

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/023-options-greeks-calculator.md
