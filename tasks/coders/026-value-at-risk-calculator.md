# C-026: Value-at-Risk (VaR) Calculator & Portfolio Risk

**Priority:** P0 - CRITICAL  
**Assigned to:** Backend Coder  
**Estimated Time:** 14-18 hours  
**Dependencies:** C-011 (Portfolio Analytics Enhancement)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive Value-at-Risk (VaR) calculation engine with multiple methodologies (parametric, historical simulation, Monte Carlo), stress testing scenarios, and risk contribution analysis.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 4.2 - Portfolio Analytics):**

- Value-at-risk (VaR) calculation
- Beta-adjusted VaR
- Stress testing scenarios
- Performance attribution (by security, sector, factor)

**From Features Specification (Section 5.2 - Portfolio Risk):**

- Value-at-Risk (VaR) - parametric, historical, Monte Carlo
- Expected Shortfall (CVaR)
- Beta-adjusted VaR
- Stress testing (historical scenarios, custom)
- Sensitivity analysis (interest rate, FX, commodity)
- Correlation breakdown
- Risk contribution by asset
- Risk limits & alerts

---

## ✅ CURRENT STATE

**What exists:**
- Portfolio tracking (C-025)
- Basic portfolio analytics (C-011)
- Asset pricing data
- Historical price data

**What's missing:**
- VaR calculation engine
- Multiple VaR methodologies
- Stress testing scenarios
- Expected Shortfall (CVaR)
- Risk contribution breakdown
- Risk limits and alerts

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (2-3 hours)

**Create `apps/backend/src/investments/models/risk.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from .portfolio import Portfolio

User = get_user_model()

class ValueAtRisk(models.Model):
    """VaR calculations for portfolios"""
    
    METHOD_CHOICES = [
        ('parametric', 'Parametric (Variance-Covariance)'),
        ('historical', 'Historical Simulation'),
        ('monte_carlo', 'Monte Carlo Simulation'),
    ]
    
    CONFIDENCE_CHOICES = [
        (90, '90%'),
        (95, '95%'),
        (99, '99%'),
        (99.9, '99.9%'),
    ]
    
    # Portfolio reference
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='var_calculations')
    
    # Calculation parameters
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    confidence_level = models.IntegerField(choices=CONFIDENCE_CHOICES)
    time_horizon = models.IntegerField()  # Days
    
    # Results
    var_amount = models.DecimalField(max_digits=20, decimal_places=2)  # Dollar amount at risk
    var_percentage = models.DecimalField(max_digits=10, decimal_places=4)  # % of portfolio value
    expected_shortfall = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # CVaR
    
    # Portfolio value at calculation time
    portfolio_value = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    calculation_time_ms = models.IntegerField()  # Performance tracking
    
    class Meta:
        indexes = [
            models.Index(fields=['portfolio', '-calculated_at']),
            models.Index(fields=['method', 'confidence_level']),
        ]
        ordering = ['-calculated_at']

class StressTest(models.Model):
    """Stress test scenarios and results"""
    
    SCENARIO_TYPE_CHOICES = [
        ('historical', 'Historical Event'),
        ('custom', 'Custom Scenario'),
        ('sensitivity', 'Sensitivity Analysis'),
    ]
    
    # Portfolio reference
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='stress_tests')
    
    # Scenario definition
    scenario_type = models.CharField(max_length=20, choices=SCENARIO_TYPE_CHOICES)
    scenario_name = models.CharField(max_length=100)
    scenario_description = models.TextField(blank=True)
    
    # Historical event reference
    historical_event = models.CharField(max_length=100, blank=True)  # e.g., "2008 Financial Crisis"
    historical_date_start = models.DateField(null=True, blank=True)
    historical_date_end = models.DateField(null=True, blank=True)
    
    # Custom shock parameters
    market_shock_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)  # Overall market drop
    sector_shocks = models.JSONField(default=dict)  # {"Technology": -0.15, "Healthcare": -0.05}
    fx_shocks = models.JSONField(default=dict)  # {"EUR": -0.10, "GBP": -0.08}
    
    # Results
    portfolio_value_before = models.DecimalField(max_digits=20, decimal_places=2)
    portfolio_value_after = models.DecimalField(max_digits=20, decimal_places=2)
    portfolio_loss = models.DecimalField(max_digits=20, decimal_places=2)
    portfolio_loss_pct = models.DecimalField(max_digits=10, decimal_places=4)
    
    # Worst performers
    worst_performing_assets = models.JSONField(default=list)  # [{"symbol": "AAPL", "loss": -0.20}]
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class RiskContribution(models.Model):
    """Risk contribution by asset"""
    
    # References
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='risk_contributions')
    var_calculation = models.ForeignKey(ValueAtRisk, on_delete=models.CASCADE, related_name='contributions')
    
    # Asset
    asset_id = models.IntegerField()
    asset_symbol = models.CharField(max_length=20)
    asset_name = models.CharField(max_length=200)
    
    # Position data
    position_value = models.DecimalField(max_digits=20, decimal_places=2)
    position_weight = models.DecimalField(max_digits=10, decimal_places=6)  # Weight in portfolio
    
    # Risk metrics
    marginal_var = models.DecimalField(max_digits=20, decimal_places=2)  # Risk added by this position
    component_var = models.DecimalField(max_digits=20, decimal_places=2)  # This position's contribution to portfolio VaR
    pct_contribution = models.DecimalField(max_digits=10, decimal_places=4)  # % of total VaR
    
    # Risk statistics
    beta = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    volatility = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    correlation_to_portfolio = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['var_calculation', '-pct_contribution']),
        ]

class RiskLimit(models.Model):
    """Risk limits and alerts"""
    
    LIMIT_TYPE_CHOICES = [
        ('var', 'VaR Limit'),
        ('concentration', 'Concentration Limit'),
        ('beta', 'Beta Limit'),
        ('drawdown', 'Max Drawdown Limit'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='risk_limits')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='risk_limits', null=True)
    
    limit_type = models.CharField(max_length=20, choices=LIMIT_TYPE_CHOICES)
    limit_name = models.CharField(max_length=100)
    
    # Limit parameters
    threshold_value = models.DecimalField(max_digits=20, decimal_places=2)  # e.g., max VaR of $10,000
    threshold_percentage = models.DecimalField(max_digits=10, decimal_places=4, null=True)  # e.g., max 20% concentration
    alert_threshold_pct = models.DecimalField(max_digits=10, decimal_places=2, default=80)  # Alert at 80% of limit
    
    # Current status
    current_value = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    current_percentage = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    breached = models.BooleanField(default=False)
    last_alert_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'limit_type', 'breached']),
        ]
```

---

### **Phase 2: VaR Calculation Service** (5-6 hours)

**Create `apps/backend/src/investments/services/var_service.py`:**

```python
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from investments.models.risk import ValueAtRisk, StressTest, RiskContribution, RiskLimit
from investments.models.portfolio import Portfolio, PortfolioPosition
from investments.models.asset import Asset
from investments.services.price_service import PriceService

class ValueAtRiskService:
    
    def __init__(self):
        self.price_service = PriceService()
    
    @transaction.atomic
    def calculate_var(
        self,
        portfolio_id: int,
        method: str = 'parametric',
        confidence_level: int = 95,
        time_horizon: int = 1,
        lookback_days: int = 252
    ) -> Dict:
        """
        Calculate Value-at-Risk using specified method
        
        Returns: {var_amount, var_percentage, expected_shortfall, ...}
        """
        import time
        start_time = time.time()
        
        portfolio = Portfolio.objects.get(id=portfolio_id)
        positions = PortfolioPosition.objects.filter(
            portfolio=portfolio,
            is_open=True
        ).select_related('asset')
        
        portfolio_value = Decimal(str(sum([
            p.quantity * p.asset.current_price 
            for p in positions
        ])))
        
        if method == 'parametric':
            result = self._calculate_parametric_var(
                positions, portfolio_value, confidence_level, time_horizon
            )
        elif method == 'historical':
            result = self._calculate_historical_var(
                positions, portfolio_value, confidence_level, time_horizon, lookback_days
            )
        elif method == 'monte_carlo':
            result = self._calculate_monte_carlo_var(
                positions, portfolio_value, confidence_level, time_horizon
            )
        else:
            raise ValueError(f"Unknown VaR method: {method}")
        
        # Save to database
        var_record = ValueAtRisk.objects.create(
            portfolio=portfolio,
            method=method,
            confidence_level=confidence_level,
            time_horizon=time_horizon,
            var_amount=Decimal(str(result['var_amount'])),
            var_percentage=Decimal(str(result['var_percentage'])),
            expected_shortfall=Decimal(str(result.get('expected_shortfall', 0))),
            portfolio_value=portfolio_value,
            calculation_time_ms=int((time.time() - start_time) * 1000)
        )
        
        # Calculate risk contributions
        self._calculate_risk_contributions(var_record, positions, result)
        
        # Check risk limits
        self._check_risk_limits(portfolio, result)
        
        result['var_id'] = var_record.id
        return result
    
    def _calculate_parametric_var(
        self,
        positions: List[PortfolioPosition],
        portfolio_value: Decimal,
        confidence_level: int,
        time_horizon: int
    ) -> Dict:
        """
        Parametric VaR using variance-covariance method
        VaR = portfolio_value * z_score * portfolio_volatility * sqrt(time_horizon)
        """
        # Get portfolio weights
        weights = np.array([
            float(p.quantity * p.asset.current_price / portfolio_value)
            for p in positions
        ])
        
        # Get covariance matrix
        returns_matrix = self._get_returns_matrix(positions, lookback_days=252)
        cov_matrix = np.cov(returns_matrix)
        
        # Calculate portfolio volatility
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Get z-score for confidence level
        z_score = self._get_z_score(confidence_level)
        
        # Calculate VaR
        var_percentage = z_score * portfolio_volatility * np.sqrt(time_horizon)
        var_amount = float(portfolio_value) * var_percentage
        
        # Calculate Expected Shortfall (CVaR)
        # For normal distribution, CVaR = VaR / (1 - confidence_level) * pdf(z_score)
        from scipy.stats import norm
        cvar_multiplier = norm.pdf(z_score) / (1 - confidence_level / 100)
        expected_shortfall = var_amount * cvar_multiplier
        
        return {
            'var_amount': var_amount,
            'var_percentage': var_percentage,
            'portfolio_volatility': portfolio_volatility,
            'expected_shortfall': expected_shortfall,
            'z_score': z_score
        }
    
    def _calculate_historical_var(
        self,
        positions: List[PortfolioPosition],
        portfolio_value: Decimal,
        confidence_level: int,
        time_horizon: int,
        lookback_days: int
    ) -> Dict:
        """
        Historical simulation VaR
        Uses actual historical returns to simulate portfolio performance
        """
        # Get historical returns for all positions
        returns_matrix = self._get_returns_matrix(positions, lookback_days)
        weights = np.array([
            float(p.quantity * p.asset.current_price / portfolio_value)
            for p in positions
        ])
        
        # Calculate portfolio returns for each day
        portfolio_returns = np.dot(returns_matrix.T, weights)
        
        # Calculate returns for time horizon
        if time_horizon > 1:
            # Aggregate returns for multi-day horizon
            portfolio_returns = pd.Series(portfolio_returns).rolling(
                window=time_horizon
            ).sum().dropna().values
        
        # Calculate VaR percentile
        var_percentile = (100 - confidence_level) / 100
        var_percentage = np.percentile(portfolio_returns, var_percentile * 100)
        var_amount = float(portfolio_value) * abs(var_percentage)
        
        # Calculate Expected Shortfall (average of losses beyond VaR)
        tail_losses = portfolio_returns[portfolio_returns <= var_percentage]
        expected_shortfall = float(portfolio_value) * abs(np.mean(tail_losses))
        
        return {
            'var_amount': var_amount,
            'var_percentage': abs(var_percentage),
            'expected_shortfall': expected_shortfall,
            'historical_scenarios': len(portfolio_returns)
        }
    
    def _calculate_monte_carlo_var(
        self,
        positions: List[PortfolioPosition],
        portfolio_value: Decimal,
        confidence_level: int,
        time_horizon: int,
        num_simulations: int = 10000
    ) -> Dict:
        """
        Monte Carlo simulation VaR
        Simulates thousands of potential future scenarios
        """
        # Get parameters
        returns_matrix = self._get_returns_matrix(positions, lookback_days=252)
        weights = np.array([
            float(p.quantity * p.asset.current_price / portfolio_value)
            for p in positions
        ])
        
        # Calculate mean returns and covariance matrix
        mean_returns = np.mean(returns_matrix, axis=1)
        cov_matrix = np.cov(returns_matrix)
        
        # Generate correlated random scenarios
        np.random.seed(42)  # For reproducibility
        simulated_returns = np.random.multivariate_normal(
            mean_returns,
            cov_matrix,
            size=(num_simulations, time_horizon)
        )
        
        # Calculate portfolio returns for each simulation
        portfolio_simulations = []
        for sim in simulated_returns:
            sim_portfolio_return = np.dot(sim.sum(axis=0), weights)
            portfolio_simulations.append(sim_portfolio_return)
        
        portfolio_simulations = np.array(portfolio_simulations)
        
        # Calculate VaR percentile
        var_percentile = (100 - confidence_level) / 100
        var_percentage = np.percentile(portfolio_simulations, var_percentile * 100)
        var_amount = float(portfolio_value) * abs(var_percentage)
        
        # Calculate Expected Shortfall
        tail_losses = portfolio_simulations[portfolio_simulations <= var_percentage]
        expected_shortfall = float(portfolio_value) * abs(np.mean(tail_losses))
        
        return {
            'var_amount': var_amount,
            'var_percentage': abs(var_percentage),
            'expected_shortfall': expected_shortfall,
            'num_simulations': num_simulations
        }
    
    def _get_returns_matrix(
        self,
        positions: List[PortfolioPosition],
        lookback_days: int = 252
    ) -> np.ndarray:
        """
        Get returns matrix for all positions
        
        Returns: numpy array of shape (num_positions, num_days)
        """
        returns_list = []
        
        for position in positions:
            # Get historical prices
            prices = self.price_service.get_historical_prices(
                asset_id=position.asset.id,
                days=lookback_days
            )
            
            if len(prices) < 2:
                # If insufficient data, use 0 returns
                returns_list.append(np.zeros(lookback_days))
                continue
            
            # Calculate daily returns
            price_array = np.array([float(p['close']) for p in prices])
            returns = np.diff(price_array) / price_array[:-1]
            
            returns_list.append(returns)
        
        # Pad to ensure all arrays have same length
        max_length = max(len(r) for r in returns_list)
        padded_returns = []
        for returns in returns_list:
            if len(returns) < max_length:
                padded = np.pad(returns, (max_length - len(returns), 0), constant_values=0)
            else:
                padded = returns
            padded_returns.append(padded)
        
        return np.array(padded_returns)
    
    def _get_z_score(self, confidence_level: int) -> float:
        """Get z-score for confidence level"""
        from scipy.stats import norm
        return norm.ppf(1 - (100 - confidence_level) / 100)
    
    def _calculate_risk_contributions(
        self,
        var_record: ValueAtRisk,
        positions: List[PortfolioPosition],
        var_result: Dict
    ):
        """Calculate risk contribution by asset"""
        portfolio_value = var_record.portfolio_value
        total_var = float(var_record.var_amount)
        
        returns_matrix = self._get_returns_matrix(positions, lookback_days=252)
        
        for i, position in enumerate(positions):
            position_value = position.quantity * position.asset.current_price
            weight = float(position_value / portfolio_value)
            
            # Calculate beta to portfolio
            position_returns = returns_matrix[i]
            portfolio_returns = np.average(returns_matrix, axis=0, weights=[
                float(p.quantity * p.asset.current_price / portfolio_value) 
                for p in positions
            ])
            
            # Calculate beta
            covariance = np.cov(position_returns, portfolio_returns)[0, 1]
            portfolio_variance = np.var(portfolio_returns)
            beta = covariance / portfolio_variance if portfolio_variance > 0 else 1.0
            
            # Calculate volatility
            volatility = np.std(position_returns)
            
            # Calculate correlation
            correlation = np.corrcoef(position_returns, portfolio_returns)[0, 1]
            
            # Marginal VaR (approximate)
            marginal_var = total_var * weight * beta
            
            # Component VaR
            component_var = marginal_var
            
            # Percentage contribution
            pct_contribution = (component_var / total_var * 100) if total_var > 0 else 0
            
            RiskContribution.objects.create(
                var_calculation=var_record,
                portfolio=var_record.portfolio,
                asset_id=position.asset.id,
                asset_symbol=position.asset.symbol,
                asset_name=position.asset.name,
                position_value=position_value,
                position_weight=weight,
                marginal_var=Decimal(str(marginal_var)),
                component_var=Decimal(str(component_var)),
                pct_contribution=Decimal(str(pct_contribution)),
                beta=Decimal(str(beta)),
                volatility=Decimal(str(volatility)),
                correlation_to_portfolio=Decimal(str(correlation))
            )
    
    def _check_risk_limits(self, portfolio: Portfolio, var_result: Dict):
        """Check if any risk limits are breached"""
        limits = RiskLimit.objects.filter(
            portfolio=portfolio,
            limit_type='var'
        )
        
        for limit in limits:
            current_var = var_result['var_amount']
            limit.current_value = Decimal(str(current_var))
            limit.current_percentage = Decimal(str(current_var / float(limit.threshold_value) * 100))
            
            # Check if limit is breached
            if current_var > float(limit.threshold_value):
                limit.breached = True
                # TODO: Send alert
            
            # Check if approaching limit (alert threshold)
            alert_threshold = float(limit.threshold_value) * float(limit.alert_threshold_pct) / 100
            if current_var > alert_threshold and not limit.breached:
                if limit.last_alert_sent_at is None or \
                   (timezone.now() - limit.last_alert_sent_at).days >= 1:
                    # TODO: Send approaching alert
                    limit.last_alert_sent_at = timezone.now()
            
            limit.save()
```

---

### **Phase 3: Stress Testing Service** (3-4 hours)

**Create `apps/backend/src/investments/services/stress_test_service.py`:**

```python
from typing import Dict, List
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from investments.models.risk import StressTest
from investments.models.portfolio import Portfolio, PortfolioPosition
from investments.models.asset import Asset
from investments.services.price_service import PriceService

class StressTestingService:
    
    def __init__(self):
        self.price_service = PriceService()
        
        # Predefined historical scenarios
        self.historical_scenarios = {
            '2008_financial_crisis': {
                'name': '2008 Financial Crisis',
                'start_date': '2008-09-01',
                'end_date': '2009-03-31',
                'market_drop': -0.50,
                'sector_shocks': {
                    'Financials': -0.60,
                    'Technology': -0.45,
                    'Healthcare': -0.30,
                    'Consumer Discretionary': -0.55
                }
            },
            'covid_crash': {
                'name': 'COVID-19 Crash (2020)',
                'start_date': '2020-02-19',
                'end_date': '2020-03-23',
                'market_drop': -0.34,
                'sector_shocks': {
                    'Energy': -0.50,
                    'Industrials': -0.40,
                    'Financials': -0.35,
                    'Technology': -0.25
                }
            },
            'dot_com_bubble': {
                'name': 'Dot-Com Bubble (2000-2002)',
                'start_date': '2000-03-10',
                'end_date': '2002-10-09',
                'market_drop': -0.49,
                'sector_shocks': {
                    'Technology': -0.78,
                    'Telecommunications': -0.65,
                    'Utilities': -0.20,
                    'Consumer Staples': -0.15
                }
            }
        }
    
    @transaction.atomic
    def run_historical_scenario(
        self,
        portfolio_id: int,
        scenario_key: str
    ) -> Dict:
        """
        Run historical stress test scenario
        
        Returns: {portfolio_loss, loss_pct, worst_performers, ...}
        """
        if scenario_key not in self.historical_scenarios:
            raise ValueError(f"Unknown scenario: {scenario_key}")
        
        scenario = self.historical_scenarios[scenario_key]
        portfolio = Portfolio.objects.get(id=portfolio_id)
        positions = PortfolioPosition.objects.filter(
            portfolio=portfolio,
            is_open=True
        ).select_related('asset')
        
        portfolio_value_before = Decimal(str(sum([
            p.quantity * p.asset.current_price 
            for p in positions
        ])))
        
        # Calculate new portfolio value after scenario
        portfolio_value_after = Decimal('0')
        worst_performers = []
        
        for position in positions:
            # Get shock for this asset's sector
            sector_shock = scenario['sector_shocks'].get(
                position.asset.sector or 'Unknown',
                scenario['market_drop']
            )
            
            # Calculate new value
            current_value = position.quantity * position.asset.current_price
            shocked_value = current_value * (1 + Decimal(str(sector_shock)))
            portfolio_value_after += shocked_value
            
            # Track worst performers
            loss_pct = float(shock := sector_shock)
            worst_performers.append({
                'symbol': position.asset.symbol,
                'name': position.asset.name,
                'loss': loss_pct,
                'loss_amount': float(current_value - shocked_value)
            })
        
        # Sort worst performers
        worst_performers.sort(key=lambda x: x['loss'])
        worst_performers = worst_performers[:10]
        
        portfolio_loss = portfolio_value_before - portfolio_value_after
        portfolio_loss_pct = float(portfolio_loss / portfolio_value_before * 100)
        
        # Save stress test
        stress_test = StressTest.objects.create(
            portfolio=portfolio,
            scenario_type='historical',
            scenario_name=scenario['name'],
            historical_event=scenario['name'],
            historical_date_start=datetime.strptime(scenario['start_date'], '%Y-%m-%d').date(),
            historical_date_end=datetime.strptime(scenario['end_date'], '%Y-%m-%d').date(),
            market_shock_pct=Decimal(str(scenario['market_drop'])),
            sector_shocks=scenario['sector_shocks'],
            portfolio_value_before=portfolio_value_before,
            portfolio_value_after=portfolio_value_after,
            portfolio_loss=portfolio_loss,
            portfolio_loss_pct=Decimal(str(portfolio_loss_pct)),
            worst_performing_assets=worst_performers[:5]
        )
        
        return {
            'stress_test_id': stress_test.id,
            'scenario_name': scenario['name'],
            'portfolio_value_before': float(portfolio_value_before),
            'portfolio_value_after': float(portfolio_value_after),
            'portfolio_loss': float(portfolio_loss),
            'portfolio_loss_pct': portfolio_loss_pct,
            'worst_performers': worst_performers
        }
    
    @transaction.atomic
    def run_custom_scenario(
        self,
        portfolio_id: int,
        market_shock_pct: float,
        sector_shocks: Dict[str, float] = None,
        fx_shocks: Dict[str, float] = None
    ) -> Dict:
        """
        Run custom stress test scenario
        
        Returns: {portfolio_loss, loss_pct, worst_performers, ...}
        """
        portfolio = Portfolio.objects.get(id=portfolio_id)
        positions = PortfolioPosition.objects.filter(
            portfolio=portfolio,
            is_open=True
        ).select_related('asset')
        
        portfolio_value_before = Decimal(str(sum([
            p.quantity * p.asset.current_price 
            for p in positions
        ])))
        
        sector_shocks = sector_shocks or {}
        fx_shocks = fx_shocks or {}
        
        # Calculate new portfolio value after scenario
        portfolio_value_after = Decimal('0')
        worst_performers = []
        
        for position in positions:
            # Determine shock for this position
            shock = Decimal(str(market_shock_pct))
            
            # Apply sector-specific shock if available
            if position.asset.sector and position.asset.sector in sector_shocks:
                shock = Decimal(str(sector_shocks[position.asset.sector]))
            
            # Apply FX shock if applicable
            if position.asset.currency and position.asset.currency in fx_shocks:
                fx_shock = Decimal(str(fx_shocks[position.asset.currency]))
                shock += fx_shock
            
            # Calculate new value
            current_value = position.quantity * position.asset.current_price
            shocked_value = current_value * (1 + shock)
            portfolio_value_after += shocked_value
            
            # Track worst performers
            worst_performers.append({
                'symbol': position.asset.symbol,
                'name': position.asset.name,
                'loss': float(shock),
                'loss_amount': float(current_value - shocked_value)
            })
        
        # Sort worst performers
        worst_performers.sort(key=lambda x: x['loss'])
        worst_performers = worst_performers[:10]
        
        portfolio_loss = portfolio_value_before - portfolio_value_after
        portfolio_loss_pct = float(portfolio_loss / portfolio_value_before * 100)
        
        # Save stress test
        stress_test = StressTest.objects.create(
            portfolio=portfolio,
            scenario_type='custom',
            scenario_name='Custom Scenario',
            market_shock_pct=Decimal(str(market_shock_pct)),
            sector_shocks=sector_shocks,
            fx_shocks=fx_shocks,
            portfolio_value_before=portfolio_value_before,
            portfolio_value_after=portfolio_value_after,
            portfolio_loss=portfolio_loss,
            portfolio_loss_pct=Decimal(str(portfolio_loss_pct)),
            worst_performing_assets=worst_performers[:5]
        )
        
        return {
            'stress_test_id': stress_test.id,
            'scenario_name': 'Custom Scenario',
            'portfolio_loss': float(portfolio_loss),
            'portfolio_loss_pct': portfolio_loss_pct,
            'worst_performers': worst_performers
        }
    
    def get_available_scenarios(self) -> List[Dict]:
        """Get list of available historical scenarios"""
        return [
            {
                'key': key,
                'name': scenario['name'],
                'market_drop': scenario['market_drop'],
                'sectors_affected': list(scenario['sector_shocks'].keys())
            }
            for key, scenario in self.historical_scenarios.items()
        ]
```

---

### **Phase 4: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/risk.py`:**

```python
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from investments.services.var_service import ValueAtRiskService
from investments.services.stress_test_service import StressTestingService
from investments.models import Portfolio

router = Router(tags=['risk'])

var_service = ValueAtRiskService()
stress_service = StressTestingService()

class VaRCalculateSchema(Schema):
    method: str  # parametric, historical, monte_carlo
    confidence_level: int  # 90, 95, 99, 99.9
    time_horizon: int  # Days

@router.post("/risk/var/{portfolio_id}")
def calculate_var(request, portfolio_id: int, data: VaRCalculateSchema):
    """Calculate Value-at-Risk for portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    result = var_service.calculate_var(
        portfolio_id=portfolio_id,
        method=data.method,
        confidence_level=data.confidence_level,
        time_horizon=data.time_horizon
    )
    
    return result

@router.get("/risk/var/{portfolio_id}/history")
def var_history(request, portfolio_id: int):
    """Get historical VaR calculations"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    from investments.models.risk import ValueAtRisk, RiskContribution
    
    var_records = ValueAtRisk.objects.filter(
        portfolio=portfolio
    ).prefetch_related('contributions')[:20]
    
    results = []
    for var in var_records:
        contributions = RiskContribution.objects.filter(
            var_calculation=var
        ).order_by('-pct_contribution')[:5]
        
        results.append({
            'id': var.id,
            'method': var.method,
            'confidence_level': var.confidence_level,
            'var_amount': float(var.var_amount),
            'var_percentage': float(var.var_percentage),
            'expected_shortfall': float(var.expected_shortfall) if var.expected_shortfall else None,
            'calculated_at': var.calculated_at,
            'top_contributors': [
                {
                    'symbol': c.asset_symbol,
                    'contribution_pct': float(c.pct_contribution)
                }
                for c in contributions
            ]
        })
    
    return results

@router.get("/risk/contributions/{var_id}")
def risk_contributions(request, var_id: int):
    """Get risk contributions for VaR calculation"""
    from investments.models.risk import ValueAtRisk, RiskContribution
    
    var = get_object_or_404(ValueAtRisk, id=var_id)
    if var.portfolio.user != request.auth:
        return {"error": "Unauthorized"}, 403
    
    contributions = RiskContribution.objects.filter(
        var_calculation=var
    ).order_by('-pct_contribution')
    
    return [
        {
            'asset_symbol': c.asset_symbol,
            'asset_name': c.asset_name,
            'position_value': float(c.position_value),
            'position_weight': float(c.position_weight),
            'component_var': float(c.component_var),
            'pct_contribution': float(c.pct_contribution),
            'beta': float(c.beta) if c.beta else None,
            'volatility': float(c.volatility) if c.volatility else None
        }
        for c in contributions
    ]

@router.post("/risk/stress-test/{portfolio_id}/historical")
def historical_stress_test(request, portfolio_id: int, scenario: str):
    """Run historical stress test scenario"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    result = stress_service.run_historical_scenario(
        portfolio_id=portfolio_id,
        scenario_key=scenario
    )
    
    return result

@router.post("/risk/stress-test/{portfolio_id}/custom")
def custom_stress_test(request, portfolio_id: int, data: dict):
    """Run custom stress test scenario"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    result = stress_service.run_custom_scenario(
        portfolio_id=portfolio_id,
        market_shock_pct=data.get('market_shock_pct', -0.20),
        sector_shocks=data.get('sector_shocks'),
        fx_shocks=data.get('fx_shocks')
    )
    
    return result

@router.get("/risk/stress-test/scenarios")
def list_stress_scenarios(request):
    """List available stress test scenarios"""
    return stress_service.get_available_scenarios()

@router.get("/risk/stress-tests/{portfolio_id}")
def portfolio_stress_tests(request, portfolio_id: int):
    """Get stress test history for portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    from investments.models.risk import StressTest
    
    stress_tests = StressTest.objects.filter(
        portfolio=portfolio
    ).order_by('-created_at')[:20]
    
    return [
        {
            'id': st.id,
            'scenario_name': st.scenario_name,
            'scenario_type': st.scenario_type,
            'portfolio_loss': float(st.portfolio_loss),
            'portfolio_loss_pct': float(st.portfolio_loss_pct),
            'worst_performers': st.worst_performing_assets,
            'created_at': st.created_at
        }
        for st in stress_tests
    ]

@router.get("/risk/limits/{portfolio_id}")
def risk_limits(request, portfolio_id: int):
    """Get risk limits for portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    from investments.models.risk import RiskLimit
    
    limits = RiskLimit.objects.filter(portfolio=portfolio)
    
    return [
        {
            'id': limit.id,
            'limit_type': limit.limit_type,
            'limit_name': limit.limit_name,
            'threshold_value': float(limit.threshold_value),
            'current_value': float(limit.current_value) if limit.current_value else None,
            'current_percentage': float(limit.current_percentage) if limit.current_percentage else None,
            'breached': limit.breached
        }
        for limit in limits
    ]
```

---

## 📋 DELIVERABLES

- [ ] ValueAtRisk, StressTest, RiskContribution, RiskLimit models
- [ ] ValueAtRiskService with 3 calculation methods (parametric, historical, Monte Carlo)
- [ ] StressTestingService with historical and custom scenarios
- [ ] 8 API endpoints for risk analysis
- [ ] Database migrations
- [ ] Unit tests (coverage >80%)
- [ ] API documentation

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Parametric VaR calculates correctly using variance-covariance method
- [ ] Historical VaR uses actual historical returns for simulation
- [ ] Monte Carlo VaR runs 10,000+ simulations
- [ ] All 3 methods return consistent results
- [ ] Risk contributions calculated by asset
- [ ] Stress tests apply correct shocks to sectors
- [ ] 3 predefined historical scenarios available (2008, COVID, Dot-com)
- [ ] Custom stress tests with sector/FX shocks working
- [ ] Risk limits trigger alerts when breached
- [ ] Expected Shortfall (CVaR) calculated for all methods
- [ ] All tests passing
- [ ] API documentation complete

---

## 📊 SUCCESS METRICS

- VaR calculation time <2 seconds (parametric), <5 seconds (Monte Carlo)
- Support for portfolios with 100+ positions
- Stress test completion <1 second
- Risk contribution calculations accurate to 2 decimal places
- Risk limit alerts sent within 10 seconds of breach

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/026-value-at-risk-calculator.md
