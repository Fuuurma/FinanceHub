# Task C-038: Options Chain Visualization

**Priority:** P1 HIGH  
**Estimated Time:** 16-20 hours  
**Assigned To:** Backend Coder + Frontend Coder  
**Status:** PENDING

## ⚡ Quick Start Guide

**What to do FIRST (in order):**

1. **Setup (Step 1):** Install dependencies (15m) - yfinance, scipy, numpy
2. **Backend (Step 2):** Create models (2h) - OptionContract, OptionsChain
3. **Backend (Step 3):** Create Greeks calculator (4h) - Black-Scholes implementation ⭐
4. **Backend (Step 4):** Create options provider (2h) - Yahoo Finance integration
5. **Backend (Step 5):** Create analytics service (2h) - IV rank, max pain, skew
6. **Backend (Step 6):** Create API endpoints (1.5h) - 6 REST endpoints
7. **Frontend (Step 7):** Create options chain table (2h) - Side-by-side calls/puts
8. **Frontend (Step 8):** Create IV skew chart (1h) - Line chart visualization
9. **Frontend (Step 9):** Create analytics dashboard (1h) - IV rank, put/call ratio
10. **Frontend (Step 10):** Create options page (1h) - Integration and polish

**Total: 17 hours (estimate)**

---

## Overview
Implement a comprehensive options chain visualization tool with implied volatility skew, Greeks display, and options analytics for traders.

## User Story
As an options trader, I want to view and analyze complete options chains with IV skew and Greeks so I can make informed options trading decisions.

---

## 🔧 STEP-BY-STEP IMPLEMENTATION GUIDE

### STEP 1: Install Dependencies (15 minutes)

```bash
pip install yfinance scipy numpy pandas
```

---

### STEP 2: Create Database Models (2 hours)

**File:** `apps/backend/src/options/models/__init__.py`

```python
from .option_contract import OptionContract, OptionsChain

__all__ = ['OptionContract', 'OptionsChain']
```

**File:** `apps/backend/src/options/models/option_contract.py`

```python
from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.common.models import UUIDModel, TimestampedModel, SoftDeleteModel
from apps.investments.models import Asset

class OptionContract(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Individual option contract (call or put).
    """
    underlying_asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='option_contracts'
    )
    
    option_type = models.CharField(
        max_length=10,
        choices=[('CALL', 'Call'), ('PUT', 'Put')]
    )
    
    strike_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Strike price of the option"
    )
    
    expiration_date = models.DateField(
        help_text="Expiration date of the option"
    )
    
    # Price data
    last_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    bid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    ask = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Volume and open interest
    volume = models.BigIntegerField(
        default=0,
        help_text="Today's trading volume"
    )
    
    open_interest = models.BigIntegerField(
        default=0,
        help_text="Total open interest"
    )
    
    # Volatility
    implied_volatility = models.FloatField(
        null=True,
        blank=True,
        help_text="Implied volatility (decimal, e.g., 0.25 for 25%)"
    )
    
    # Greeks (calculated)
    delta = models.FloatField(
        null=True,
        blank=True,
        help_text="Option delta"
    )
    
    gamma = models.FloatField(
        null=True,
        blank=True,
        help_text="Option gamma"
    )
    
    theta = models.FloatField(
        null=True,
        blank=True,
        help_text="Option theta (per day)"
    )
    
    vega = models.FloatField(
        null=True,
        blank=True,
        help_text="Option vega (per 1% vol change)"
    )
    
    rho = models.FloatField(
        null=True,
        blank=True,
        help_text="Option rho"
    )
    
    # Additional data
    in_the_money = models.BooleanField(
        default=False,
        help_text="Is option currently ITM?"
    )
    
    class Meta:
        db_table = 'option_contracts'
        indexes = [
            models.Index(fields=['underlying_asset', 'expiration_date', 'strike_price']),
            models.Index(fields=['expiration_date']),
            models.Index(fields=['implied_volatility']),
        ]
        unique_together = [
            ['underlying_asset', 'option_type', 'strike_price', 'expiration_date']
        ]
    
    def __str__(self):
        return f"{self.underlying_asset.symbol} {self.option_type} ${self.strike_price} {self.expiration_date}"
    
    @property
    def days_to_expiration(self) -> int:
        """Calculate days to expiration."""
        from datetime import date
        delta = self.expiration_date - date.today()
        return max(0, delta.days)


class OptionsChain(UUIDModel, TimestampedModel):
    """
    Snapshot of complete options chain for an asset.
    """
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='options_chains'
    )
    
    snapshot_date = models.DateTimeField(auto_now_add=True)
    
    spot_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Current spot price of underlying"
    )
    
    # Analytics
    iv_rank = models.FloatField(
        null=True,
        blank=True,
        help_text="IV rank (0-100)"
    )
    
    iv_percentile = models.FloatField(
        null=True,
        blank=True,
        help_text="IV percentile (0-100)"
    )
    
    put_call_ratio = models.FloatField(
        null=True,
        blank=True,
        help_text="Put/Call volume ratio"
    )
    
    max_pain_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    expected_move = models.FloatField(
        null=True,
        blank=True,
        help_text="Expected move for nearest expiration"
    )
    
    class Meta:
        db_table = 'options_chains'
        ordering = ['-snapshot_date']
        indexes = [
            models.Index(fields=['asset', 'snapshot_date']),
        ]
    
    def __str__(self):
        return f"{self.asset.symbol} Options Chain - {self.snapshot_date}"
```

**CREATE MIGRATION:**
```bash
python manage.py makemigrations options
python manage.py migrate options
```

---

### STEP 3: Create Greeks Calculator (4 hours) ⭐ CRITICAL

**File:** `apps/backend/src/options/services/greeks_calculator.py`

```python
import numpy as np
from scipy.stats import norm
from typing import Tuple
from datetime import date

class GreeksCalculator:
    """
    Calculate option Greeks using the Black-Scholes model.
    
    Black-Scholes Formulas:
    
    Call Option:
    - d1 = (ln(S/K) + (r + σ²/2)T) / (σ√T)
    - d2 = d1 - σ√T
    - Price = S·N(d1) - K·e^(-rT)·N(d2)
    
    Put Option:
    - d1 = (ln(S/K) + (r + σ²/2)T) / (σ√T)
    - d2 = d1 - σ√T
    - Price = K·e^(-rT)·N(-d2) - S·N(-d1)
    
    Greeks:
    - Delta (Δ): Rate of change of option price wrt underlying price
      - Call: N(d1)
      - Put: N(d1) - 1
    
    - Gamma (Γ): Rate of change of delta wrt underlying price
      - Call & Put: φ(d1) / (S·σ√T)
    
    - Theta (Θ): Rate of change of option price wrt time
      - Call: -(S·φ(d1)·σ) / (2√T) - r·K·e^(-rT)·N(d2)
      - Put: -(S·φ(d1)·σ) / (2√T) + r·K·e^(-rT)·N(-d2)
    
    - Vega (ν): Rate of change of option price wrt volatility
      - Call & Put: S·φ(d1)·√T
    
    - Rho (ρ): Rate of change of option price wrt interest rate
      - Call: K·T·e^(-rT)·N(d2)
      - Put: -K·T·e^(-rT)·N(-d2)
    
    Where:
    - S = Spot price
    - K = Strike price
    - T = Time to expiration (years)
    - r = Risk-free rate
    - σ = Volatility
    - N(x) = Cumulative normal distribution
    - φ(x) = Standard normal probability density
    """
    
    def __init__(self, risk_free_rate: float = 0.05):
        """
        Initialize calculator.
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 5%)
        """
        self.r = risk_free_rate
    
    def calculate_d1_d2(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float
    ) -> Tuple[float, float]:
        """
        Calculate d1 and d2 for Black-Scholes.
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            
        Returns:
            Tuple of (d1, d2)
        """
        # Avoid division by zero
        if T == 0:
            T = 0.0001
        
        d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        return d1, d2
    
    def calculate_delta(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str
    ) -> float:
        """
        Calculate option delta.
        
        Delta is the rate of change of option price with respect to
        the underlying price. It measures the option's sensitivity to
        price changes in the underlying asset.
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'CALL' or 'PUT'
            
        Returns:
            Delta value
        """
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)
        
        if option_type == 'CALL':
            return norm.cdf(d1)
        else:  # PUT
            return norm.cdf(d1) - 1
    
    def calculate_gamma(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float
    ) -> float:
        """
        Calculate option gamma.
        
        Gamma is the rate of change of delta with respect to the
        underlying price. It measures the curvature of the option's
        value relative to the underlying.
        
        Gamma is the same for both calls and puts.
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            
        Returns:
            Gamma value
        """
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)
        
        return norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    def calculate_theta(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str
    ) -> float:
        """
        Calculate option theta (per day).
        
        Theta is the rate of change of option value with respect to
        time. It measures time decay - how much value an option loses
        each day as it approaches expiration.
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'CALL' or 'PUT'
            
        Returns:
            Theta value (per day)
        """
        d1, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        
        # First term (common to both call and put)
        term1 = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        
        if option_type == 'CALL':
            term2 = -r * K * np.exp(-r * T) * norm.cdf(d2)
        else:  # PUT
            term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
        
        # Convert from annual to daily (divide by 365)
        return (term1 + term2) / 365
    
    def calculate_vega(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float
    ) -> float:
        """
        Calculate option vega.
        
        Vega is the rate of change of option value with respect to
        volatility. It measures the option's sensitivity to changes
        in implied volatility.
        
        Vega is the same for both calls and puts, and is expressed
        per 1% change in volatility (or 0.01 in decimal).
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            
        Returns:
            Vega value (per 1% vol change)
        """
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)
        
        # Vega is per 1% change in volatility
        return S * norm.pdf(d1) * np.sqrt(T) * 0.01
    
    def calculate_rho(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str
    ) -> float:
        """
        Calculate option rho.
        
        Rho is the rate of change of option value with respect to
        the interest rate. It measures the option's sensitivity to
        changes in the risk-free rate.
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'CALL' or 'PUT'
            
        Returns:
            Rho value (per 1% rate change)
        """
        _, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        
        if option_type == 'CALL':
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        else:  # PUT
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        
        # Convert to per 1% rate change
        return rho * 0.01
    
    def calculate_all_greeks(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str
    ) -> dict:
        """
        Calculate all Greeks at once.
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'CALL' or 'PUT'
            
        Returns:
            Dictionary with all Greeks
        """
        return {
            'delta': self.calculate_delta(S, K, T, r, sigma, option_type),
            'gamma': self.calculate_gamma(S, K, T, r, sigma),
            'theta': self.calculate_theta(S, K, T, r, sigma, option_type),
            'vega': self.calculate_vega(S, K, T, r, sigma),
            'rho': self.calculate_rho(S, K, T, r, sigma, option_type)
        }
    
    def calculate_implied_volatility(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        market_price: float,
        option_type: str,
        initial_guess: float = 0.2,
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> float:
        """
        Calculate implied volatility using Newton-Raphson method.
        
        Implied volatility is the volatility value that, when input
        into the Black-Scholes formula, gives the market price.
        
        Uses iterative root-finding to solve for σ.
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            market_price: Market price of the option
            option_type: 'CALL' or 'PUT'
            initial_guess: Initial volatility guess (default: 20%)
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            
        Returns:
            Implied volatility
        """
        sigma = initial_guess
        
        for _ in range(max_iterations):
            # Calculate option price and vega at current sigma
            price = self.calculate_black_scholes_price(S, K, T, r, sigma, option_type)
            vega = self.calculate_vega(S, K, T, r, sigma) / 0.01  # Convert back
            
            # Check convergence
            diff = price - market_price
            if abs(diff) < tolerance:
                break
            
            # Newton-Raphson update
            sigma = sigma - diff / vega
            
            # Keep sigma in reasonable range
            sigma = max(0.01, min(sigma, 5.0))
        
        return sigma
    
    def calculate_black_scholes_price(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str
    ) -> float:
        """
        Calculate Black-Scholes option price.
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'CALL' or 'PUT'
            
        Returns:
            Option price
        """
        d1, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        
        if option_type == 'CALL':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:  # PUT
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        return price
    
    def calculate_probability_itm(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str
    ) -> float:
        """
        Calculate probability of option expiring in-the-money.
        
        For calls: Probability that S > K at expiration
        For puts: Probability that S < K at expiration
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'CALL' or 'PUT'
            
        Returns:
            Probability (0-1)
        """
        _, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        
        if option_type == 'CALL':
            return norm.cdf(d2)
        else:
            return norm.cdf(-d2)


# QUICK TEST
if __name__ == '__main__':
    calc = GreeksCalculator(risk_free_rate=0.05)
    
    # Example: TSLA call option
    S = 250  # Spot price
    K = 260  # Strike price
    T = 30 / 365  # 30 days to expiration
    r = 0.05  # 5% risk-free rate
    sigma = 0.40  # 40% volatility
    
    greeks = calc.calculate_all_greeks(S, K, T, r, sigma, 'CALL')
    
    print("TSLA $260 Call (30 days to exp):")
    print(f"Delta: {greeks['delta']:.4f}")
    print(f"Gamma: {greeks['gamma']:.4f}")
    print(f"Theta: {greeks['theta']:.4f} (per day)")
    print(f"Vega: {greeks['vega']:.4f} (per 1% vol)")
    print(f"Rho: {greeks['rho']:.4f} (per 1% rate)")
    print(f"Probability ITM: {calc.calculate_probability_itm(S, K, T, r, sigma, 'CALL'):.2%}")
```

---

### STEP 4: Create Options Data Provider (2 hours)

**File:** `apps/backend/src/options/providers/yahoo_options.py`

```python
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
from ..services.greeks_calculator import GreeksCalculator

class YahooOptionsProvider:
    """
    Fetch options data from Yahoo Finance using yfinance.
    
    Free, reliable, but has rate limits.
    """
    
    def __init__(self):
        self.greeks_calc = GreeksCalculator()
    
    def get_options_chain(
        self,
        symbol: str,
        expiration: str = None
    ) -> Dict:
        """
        Fetch options chain for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'TSLA')
            expiration: Expiration date (YYYY-MM-DD), or None for nearest
            
        Returns:
            Dictionary with calls, puts, and spot price
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get expirations
            expirations = ticker.options
            
            if not expirations:
                return {'error': 'No options available'}
            
            # Use nearest expiration if not specified
            if expiration is None:
                expiration = expirations[0]
            
            # Get options chain
            opt = ticker.option_chain(expiration)
            
            # Get current spot price
            spot_price = ticker.info.get('currentPrice') or ticker.history(period='1d')['Close'].iloc[-1]
            
            # Process calls
            calls = []
            for _, row in opt.calls.iterrows():
                call_data = self._process_option(row, spot_price, 'CALL')
                calls.append(call_data)
            
            # Process puts
            puts = []
            for _, row in opt.puts.iterrows():
                put_data = self._process_option(row, spot_price, 'PUT')
                puts.append(put_data)
            
            return {
                'symbol': symbol,
                'spot_price': float(spot_price),
                'expiration': expiration,
                'expirations': list(expirations),
                'calls': calls,
                'puts': puts
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _process_option(self, row, spot_price: float, option_type: str) -> Dict:
        """Process option row and calculate Greeks."""
        from decimal import Decimal
        
        strike = float(row['strike'])
        last_price = float(row['lastPrice'])
        bid = float(row['bid'])
        ask = float(row['ask'])
        iv = float(row['impliedVolatility']) if 'impliedVolatility' in row and row['impliedVolatility'] else None
        
        # Calculate time to expiration
        expiration_date = datetime.strptime(row['lastTradeDate'], '%Y-%m-%d')
        T = (expiration_date - datetime.now()).days / 365.0
        
        # Calculate Greeks if we have IV
        greeks = {}
        if iv and T > 0:
            try:
                greeks = self.greeks_calc.calculate_all_greeks(
                    S=spot_price,
                    K=strike,
                    T=T,
                    r=0.05,
                    sigma=iv,
                    option_type=option_type
                )
            except:
                pass
        
        # Determine if ITM
        if option_type == 'CALL':
            itm = spot_price > strike
        else:
            itm = spot_price < strike
        
        return {
            'strike': strike,
            'last_price': last_price,
            'bid': bid,
            'ask': ask,
            'volume': int(row['volume']) if 'volume' in row else 0,
            'open_interest': int(row['openInterest']) if 'openInterest' in row else 0,
            'implied_volatility': iv,
            'in_the_money': itm,
            'delta': greeks.get('delta'),
            'gamma': greeks.get('gamma'),
            'theta': greeks.get('theta'),
            'vega': greeks.get('vega'),
            'rho': greeks.get('rho'),
            'last_trade_date': row.get('lastTradeDate')
        }


# USAGE EXAMPLE
if __name__ == '__main__':
    provider = YahooOptionsProvider()
    
    # Get TSLA options
    chain = provider.get_options_chain('TSLA')
    
    print(f"Spot: ${chain['spot_price']:.2f}")
    print(f"Calls: {len(chain['calls'])}")
    print(f"Puts: {len(chain['puts'])}")
```

---

### STEP 5: Create Options Analytics Service (2 hours)

**File:** `apps/backend/src/options/services/options_analytics.py`

```python
import numpy as np
from typing import List, Dict

class OptionsAnalyticsService:
    """
    Calculate options analytics: IV rank, max pain, put/call ratio.
    """
    
    def calculate_iv_rank(
        self,
        current_iv: float,
        iv_low_52w: float,
        iv_high_52w: float
    ) -> float:
        """
        Calculate IV rank.
        
        IV rank shows where current IV sits in the 52-week range.
        Formula: (IV - IV_low) / (IV_high - IV_low)
        
        Args:
            current_iv: Current implied volatility
            iv_low_52w: 52-week low IV
            iv_high_52w: 52-week high IV
            
        Returns:
            IV rank (0-100)
        """
        if iv_high_52w == iv_low_52w:
            return 50
        
        rank = (current_iv - iv_low_52w) / (iv_high_52w - iv_low_52w) * 100
        return max(0, min(100, rank))
    
    def calculate_max_pain(
        self,
        calls: List[Dict],
        puts: List[Dict],
        spot_price: float
    ) -> float:
        """
        Calculate max pain price.
        
        Max pain is the strike price at which the maximum number of
        options expire worthless, causing maximum pain to option holders.
        
        Args:
            calls: List of call contracts with strike and open_interest
            puts: List of put contracts with strike and open_interest
            spot_price: Current spot price
            
        Returns:
            Max pain price
        """
        # Get all unique strikes
        strikes = set()
        for call in calls:
            strikes.add(call['strike'])
        for put in puts:
            strikes.add(put['strike'])
        
        # Calculate total pain at each strike
        min_pain = float('inf')
        max_pain_price = spot_price
        
        for strike in strikes:
            total_pain = 0
            
            # Calculate pain for call holders
            for call in calls:
                if call['strike'] == strike:
                    intrinsic_value = max(0, spot_price - strike)
                    pain = intrinsic_value * call['open_interest']
                    total_pain += pain
            
            # Calculate pain for put holders
            for put in puts:
                if put['strike'] == strike:
                    intrinsic_value = max(0, strike - spot_price)
                    pain = intrinsic_value * put['open_interest']
                    total_pain += pain
            
            # Find strike with minimum pain (maximum pain for holders)
            if total_pain < min_pain:
                min_pain = total_pain
                max_pain_price = strike
        
        return max_pain_price
    
    def calculate_put_call_ratio(
        self,
        call_volume: int,
        put_volume: int
    ) -> float:
        """
        Calculate put/call ratio.
        
        PCR > 1: More bearish (more puts traded)
        PCR < 1: More bullish (more calls traded)
        
        Args:
            call_volume: Total call volume
            put_volume: Total put volume
            
        Returns:
            Put/call ratio
        """
        if call_volume == 0:
            return float('inf') if put_volume > 0 else 1
        
        return put_volume / call_volume
    
    def calculate_expected_move(
        self,
        spot_price: float,
        iv: float,
        days_to_expiration: int
    ) -> float:
        """
        Calculate expected move for an expiration.
        
        Expected move = spot_price * IV * sqrt(days/365)
        
        This gives the expected 1-standard deviation range.
        
        Args:
            spot_price: Current spot price
            iv: Implied volatility
            days_to_expiration: Days to expiration
            
        Returns:
            Expected move (+/-)
        """
        T = days_to_expiration / 365.0
        expected_move = spot_price * iv * np.sqrt(T)
        return expected_move
```

---

### STEP 6: Create API Endpoints (1.5 hours)

**File:** `apps/backend/src/options/api/options.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..providers.yahoo_options import YahooOptionsProvider
from ..services.options_analytics import OptionsAnalyticsService

class OptionsViewSet(viewsets.ViewSet):
    """
    Options API endpoints.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = YahooOptionsProvider()
        self.analytics = OptionsAnalyticsService()
    
    def retrieve(self, request, pk=None):
        """
        GET /api/options/{symbol}/chain
        Get options chain for a symbol.
        """
        expiration = request.query_params.get('expiration')
        
        chain = self.provider.get_options_chain(pk, expiration)
        
        if 'error' in chain:
            return Response({'error': chain['error']}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(chain)
    
    @action(detail=False, methods=['get'])
    def expirations(self, request):
        """
        GET /api/options/{symbol}/expirations
        Get available expiration dates.
        """
        symbol = request.query_params.get('symbol')
        
        chain = self.provider.get_options_chain(symbol)
        
        if 'error' in chain:
            return Response({'error': chain['error']}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'expirations': chain['expirations']})
```

---

## 📚 COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Forgetting to Convert Time to Years
```python
# WRONG - Using days directly
T = 30  # 30 days
d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))

# CORRECT - Convert to years
T = 30 / 365.0  # 30 days in years
```

### ❌ Mistake 2: Not Handling Division by Zero
```python
# WRONG - Will crash if T=0
d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))

# CORRECT - Handle edge case
if T == 0:
    T = 0.0001
d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
```

### ❌ Mistake 3: Wrong Volatility Input
```python
# WRONG - Using percentage (40) instead of decimal (0.40)
sigma = 40  # This will give wrong results

# CORRECT - Use decimal
sigma = 0.40  # 40% volatility
```

### ❌ Mistake 4: Not Annualizing Interest Rate
```python
# WRONG - Using monthly rate directly
r = 0.004  # 0.4% monthly rate

# CORRECT - Use annual rate
r = 0.05  # 5% annual rate
```

### ❌ Mistake 5: Theta Wrong Units
```python
# WRONG - Returning annual theta
return theta  # This is per year

# CORRECT - Convert to per day
return theta / 365  # Per day
```

---

## ❓ FAQ

**Q: Why are my Greeks different from my broker?**  
A: Small differences are normal. Check: (1) Risk-free rate used, (2) Time calculation (trading days vs calendar days), (3) Early exercise features (American vs European options).

**Q: Should I use simple or continuous compounding?**  
A: Use continuous compounding (e^(-rT)) for Black-Scholes. It's the standard.

**Q: How do I handle American options?**  
A: Black-Scholes is for European options only. For American options, use binomial tree or finite difference methods.

**Q: What's a good default for risk-free rate?**  
A: Use current 10-year Treasury yield. Check: https://www.treasury.gov/resource-center/data-chart-center/interest-rates

**Q: Why is my IV calculation failing?**  
A: Newton-Raphson needs a good initial guess. Use 0.20 (20%) as default. If it fails, use bisection method instead.

**Q: How accurate is Black-Scholes?**  
A: Good for at-the-money options with >30 days to expiration. Less accurate for deep ITM/OTM or near expiration.

**Q: Should I cache Greeks calculations?**  
A: YES! Greeks are expensive. Cache for 5-15 minutes. Greeks change slowly except near expiration.

---

## 📦 FRONTEND IMPLEMENTATION GUIDE

### File: `apps/frontend/src/components/options/OptionsChainTable.tsx`

```typescript
'use client';

import { useState } from 'react';

interface OptionContract {
  strike: number;
  last_price: number;
  bid: number;
  ask: number;
  volume: number;
  open_interest: number;
  implied_volatility: number;
  delta?: number;
  gamma?: number;
  theta?: number;
  vega?: number;
  in_the_money: boolean;
}

interface OptionsChainTableProps {
  spotPrice: number;
  calls: OptionContract[];
  puts: OptionContract[];
}

export function OptionsChainTable({ spotPrice, calls, puts }: OptionsChainTableProps) {
  const [sortBy, setSortBy] = useState<'strike' | 'delta' | 'iv'>('strike');
  
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th colSpan={7} className="text-center font-bold text-green-600">Calls</th>
            <th className="bg-gray-200">Strike</th>
            <th colSpan={7} className="text-center font-bold text-red-600">Puts</th>
          </tr>
          <tr>
            {/* Calls headers */}
            <th>Last</th>
            <th>Change</th>
            <th>Bid</th>
            <th>Ask</th>
            <th>Volume</th>
            <th>IV</th>
            <th>Delta</th>
            
            {/* Strike */}
            <th className="bg-gray-200">Strike</th>
            
            {/* Puts headers */}
            <th>Last</th>
            <th>Change</th>
            <th>Bid</th>
            <th>Ask</th>
            <th>Volume</th>
            <th>IV</th>
            <th>Delta</th>
          </tr>
        </thead>
        <tbody>
          {calls.map((call, i) => (
            <tr
              key={call.strike}
              className={
                call.in_the_money
                  ? 'bg-green-50'
                  : put[i]?.in_the_money
                  ? 'bg-red-50'
                  : i % 2 === 0
                  ? 'bg-white'
                  : 'bg-gray-50'
              }
            >
              {/* Calls */}
              <td>${call.last_price.toFixed(2)}</td>
              <td>0.00</td>
              <td>${call.bid.toFixed(2)}</td>
              <td>${call.ask.toFixed(2)}</td>
              <td>{call.volume}</td>
              <td>{call.implied_volatility ? (call.implied_volatility * 100).toFixed(1) + '%' : '-'}</td>
              <td>{call.delta ? call.delta.toFixed(3) : '-'}</td>
              
              {/* Strike */}
              <td className="bg-gray-200 text-center font-bold">
                {call.strike}
              </td>
              
              {/* Puts */}
              {puts[i] && (
                <>
                  <td>${puts[i].last_price.toFixed(2)}</td>
                  <td>0.00</td>
                  <td>${puts[i].bid.toFixed(2)}</td>
                  <td>${puts[i].ask.toFixed(2)}</td>
                  <td>{puts[i].volume}</td>
                  <td>{puts[i].implied_volatility ? (puts[i].implied_volatility * 100).toFixed(1) + '%' : '-'}</td>
                  <td>{puts[i].delta ? puts[i].delta.toFixed(3) : '-'}</td>
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 📋 CHECKLIST BEFORE SUBMITTING

- [ ] All models created with base classes
- [ ] Migration created and applied
- [ ] Greeks calculator working with test data
- [ ] Black-Scholes formula implemented correctly
- [ ] Time to expiration converted to years
- [ ] Implied volatility calculation converges
- [ ] Yahoo Finance provider working
- [ ] IV rank calculation correct
- [ ] Max pain calculation working
- [ ] Put/call ratio calculated
- [ ] API endpoints have authentication
- [ ] Options chain table renders
- [ ] ITM highlighting working
- [ ] Greeks displayed correctly

---

## 🎯 SUCCESS CRITERIA

1. ✅ Options chains load in < 2 seconds
2. ✅ All Greeks calculated accurately
3. ✅ IV skew chart renders correctly
4. ✅ Max pain calculated correctly
5. ✅ IV rank and percentile shown
6. ✅ Put/call ratio displayed
7. ✅ Frontend shows calls/puts side-by-side

---

**Start with Step 1 (install dependencies) and work through each step sequentially.**
