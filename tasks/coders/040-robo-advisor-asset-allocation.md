# Task C-040: Robo-Advisor Asset Allocation

**Priority:** P1 HIGH  
**Estimated Time:** 18-24 hours  
**Assigned To:** Backend Coder + Frontend Coder  
**Status:** PENDING

## ⚡ Quick Start Guide

**What to do FIRST (in order):**

1. **Backend (Step 1):** Create models (2h) - RiskProfile, RecommendedAllocation, InvestmentGoal
2. **Backend (Step 2):** Create MPT engine (4h) - Use scipy.optimize.minimize with Sharpe ratio
3. **Backend (Step 3):** Create portfolio service (3h) - Efficient frontier, optimization methods
4. **Backend (Step 4):** Create goal planning service (3h) - Monte Carlo simulation
5. **Backend (Step 5):** Create API endpoints (2h) - 6 REST endpoints
6. **Frontend (Step 6):** Create questionnaire (2h) - Multi-step form with 10 questions
7. **Frontend (Step 7):** Create allocation dashboard (2h) - Pie chart + efficient frontier
8. **Frontend (Step 8):** Create rebalancing tool (1h) - Show current vs target

**Total: 19 hours (estimate)**

---

## Overview
Implement a robo-advisor system that uses modern portfolio theory (MPT) and machine learning to suggest optimal asset allocations based on user's risk tolerance, investment goals, and time horizon.

## User Story
As an investor, I want AI-powered asset allocation recommendations so I can optimize my portfolio for my risk profile and financial goals.

## Acceptance Criteria

### Backend (14-18 hours)
- [ ] **Risk Profile Assessment**
  - RiskQuestionnaire model - User's risk tolerance questions
  - RiskProfile model - Calculated risk score (1-10)
  - InvestmentGoals model - User's financial goals
  - TimeHorizon model - Investment time frame

- [ ] **Modern Portfolio Theory (MPT) Engine**
  - Calculate efficient frontier using historical returns
  - Optimize Sharpe ratio (maximize return, minimize risk)
  - Calculate optimal asset allocation
  - Use covariance matrix for risk calculation
  - Support constraints (min/max allocation per asset)

- [ ] **Asset Allocation Models**
  - Conservative model (20% stocks, 80% bonds)
  - Moderate model (60% stocks, 40% bonds)
  - Aggressive model (90% stocks, 10% bonds)
  - Target Date funds (glide path)
  - Custom allocation based on risk profile

- [ ] **Portfolio Optimization Service**
  - Mean-Variance Optimization (Markowitz)
  - Risk Parity Optimization
  - Minimum Variance Portfolio
  - Maximum Diversification Portfolio
  - Black-Litterman model (incorporate views)

- [ ] **Rebalancing Recommendations**
  - Suggest trades to reach target allocation
  - Calculate drift from target
  - Suggest rebalancing frequency
  - Tax-loss harvesting suggestions
  - Minimize transaction costs

- [ ] **Goal-Based Planning**
  - Retirement goal calculator
  - College savings goal
  - House down payment goal
  - Emergency fund planning
  - Monte Carlo simulations for goal probability

- [ ] **API Endpoints**
  - `GET /api/robo-advisor/assessment` - Get risk questionnaire
  - `POST /api/robo-advisor/assessment` - Submit risk answers
  - `GET /api/robo-advisor/allocation` - Get recommended allocation
  - `GET /api/robo-advisor/efficient-frontier` - Get efficient frontier data
  - `GET /api/robo-advisor/rebalancing` - Get rebalancing suggestions
  - `GET /api/robo-advisor/goals/{goal_id}` - Get goal progress

### Frontend (4-6 hours)
- [ ] **Risk Assessment Questionnaire**
  - 10-15 questions about risk tolerance
  - Questions cover: age, income, net worth, investment experience
  - Time horizon questions
  - Risk attitude questions
  - Calculate risk score in real-time
  - Show risk profile result (Conservative, Moderate, Aggressive)

- [ ] **Asset Allocation Dashboard**
  - Display recommended allocation (pie chart)
  - Show efficient frontier chart
  - Show expected return vs risk
  - Show historical performance of model portfolio
  - Compare with current portfolio
  - Show "what if" scenarios

- [ ] **Rebalancing Tool**
  - Show current vs target allocation
  - Display suggested trades (buy/sell)
  - Show estimated transaction costs
  - One-click rebalancing (if paper trading)
  - Tax impact estimation

- [ ] **Goal Planning Dashboard**
  - Create financial goals (retirement, house, college)
  - Input goal amount, time horizon, monthly contribution
  - Show probability of success (Monte Carlo)
  - Show recommended portfolio for goal
  - Track goal progress over time

- [ ] **Robo-Advisor Landing Page**
  - `/robo-advisor` route
  - Call-to-action: "Get Your Allocation"
  - Explain how it works
  - Show example allocations
  - Link to risk assessment

---

## 🔧 STEP-BY-STEP IMPLEMENTATION GUIDE

### STEP 1: Create Database Models (2 hours)

**File:** `apps/backend/src/robo_advisor/models/__init__.py`

```python
from .risk_profile import RiskProfile, RiskQuestionnaire, InvestmentGoal
from .allocation import RecommendedAllocation

__all__ = ['RiskProfile', 'RiskQuestionnaire', 'InvestmentGoal', 'RecommendedAllocation']
```

**File:** `apps/backend/src/robo_advisor/models/risk_profile.py`

```python
from django.db import models
from django.conf import settings
from apps.common.models import UUIDModel, TimestampedModel, SoftDeleteModel

class RiskProfile(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    User's risk profile based on questionnaire responses.
    Risk score: 1-10 (1=Conservative, 10=Aggressive)
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='risk_profile'
    )
    
    risk_score = models.IntegerField(
        help_text="1-10, calculated from questionnaire"
    )
    
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[
            ('CONSERVATIVE', 'Conservative'),
            ('MODERATE', 'Moderate'),
            ('AGGRESSIVE', 'Aggressive')
        ]
    )
    
    time_horizon = models.IntegerField(
        help_text="Investment time horizon in years"
    )
    
    investment_objective = models.CharField(
        max_length=50,
        choices=[
            ('PRESERVATION', 'Capital Preservation'),
            ('INCOME', 'Income Generation'),
            ('GROWTH', 'Growth'),
            ('AGGRESSIVE_GROWTH', 'Aggressive Growth')
        ]
    )
    
    # Questionnaire responses (JSON)
    responses = models.JSONField(
        default=dict,
        help_text="Store questionnaire answers"
    )
    
    class Meta:
        db_table = 'risk_profiles'
        indexes = [
            models.Index(fields=['user', 'risk_score']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.risk_tolerance} (Score: {self.risk_score})"


class RiskQuestionnaire(UUIDModel, TimestampedModel):
    """
    Risk assessment questionnaire template.
    """
    question = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('MULTIPLE_CHOICE', 'Multiple Choice'),
            ('SCALE', 'Scale 1-10'),
            ('YES_NO', 'Yes/No')
        ]
    )
    choices = models.JSONField(
        default=list,
        help_text="For MULTIPLE_CHOICE: list of options with scores"
    )
    weight = models.FloatField(
        default=1.0,
        help_text="Weight in risk score calculation"
    )
    order = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'risk_questionnaires'
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question[:50]}"


class InvestmentGoal(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    User's financial goals for goal-based investing.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='investment_goals'
    )
    
    goal_type = models.CharField(
        max_length=50,
        choices=[
            ('RETIREMENT', 'Retirement'),
            ('COLLEGE', 'College Education'),
            ('HOUSE', 'House Down Payment'),
            ('EMERGENCY_FUND', 'Emergency Fund'),
            ('WEALTH_BUILDING', 'Wealth Building'),
            ('OTHER', 'Other')
        ]
    )
    
    goal_name = models.CharField(max_length=200)
    target_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Target amount in USD"
    )
    
    current_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    
    target_date = models.DateField()
    
    monthly_contribution = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Monthly contribution amount"
    )
    
    probability_of_success = models.FloatField(
        null=True,
        blank=True,
        help_text="Monte Carlo simulation result (0-1)"
    )
    
    recommended_allocation = models.JSONField(
        null=True,
        blank=True,
        help_text="Recommended allocation for this goal"
    )
    
    achieved = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'investment_goals'
        indexes = [
            models.Index(fields=['user', 'target_date']),
            models.Index(fields=['goal_type']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.goal_name} (${self.target_amount})"
    
    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return float(self.current_amount) / float(self.target_amount) * 100
```

**File:** `apps/backend/src/robo_advisor/models/allocation.py`

```python
from django.db import models
from django.conf import settings
from apps.common.models import UUIDModel, TimestampedModel, SoftDeleteModel
from apps.investments.models import Asset

class RecommendedAllocation(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Recommended asset allocation for a user's risk profile.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommended_allocations'
    )
    
    risk_profile = models.ForeignKey(
        'RiskProfile',
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name='allocations'
    )
    
    target_allocation = models.FloatField(
        help_text="Target allocation (0.0 to 1.0)"
    )
    
    expected_return = models.FloatField(
        help_text="Expected annual return (decimal, e.g., 0.08 for 8%)"
    )
    
    expected_risk = models.FloatField(
        help_text="Expected annual volatility (decimal, e.g., 0.15 for 15%)"
    )
    
    optimization_method = models.CharField(
        max_length=50,
        choices=[
            ('MEAN_VARIANCE', 'Mean-Variance'),
            ('RISK_PARITY', 'Risk Parity'),
            ('MIN_VARIANCE', 'Minimum Variance'),
            ('MAX_DIVERSIFICATION', 'Maximum Diversification'),
            ('BLACK_LITTERMAN', 'Black-Litterman')
        ]
    )
    
    class Meta:
        db_table = 'recommended_allocations'
        unique_together = [['risk_profile', 'asset']]
        indexes = [
            models.Index(fields=['user', 'risk_profile']),
        ]
    
    def __str__(self):
        return f"{self.asset.symbol}: {self.target_allocation:.1%}"
```

**CREATE MIGRATION:**
```bash
python manage.py makemigrations robo_advisor
python manage.py migrate robo_advisor
```

---

### STEP 2: Create MPT Engine (4 hours) ⭐ MOST CRITICAL

**File:** `apps/backend/src/robo_advisor/services/mpt_engine.py`

```python
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class MPTEngine:
    """
    Modern Portfolio Theory Engine for portfolio optimization.
    
    Uses scipy.optimize.minimize to find optimal weights that maximize
    the Sharpe ratio: (Rp - Rf) / σp
    
    Where:
    - Rp = Expected portfolio return
    - Rf = Risk-free rate
    - σp = Portfolio volatility (standard deviation)
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize MPT Engine.
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
        """
        self.risk_free_rate = risk_free_rate
    
    def prepare_returns_data(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert price data to returns data.
        
        Args:
            price_data: DataFrame with datetime index and asset prices
            
        Returns:
            DataFrame with daily returns
        """
        returns = price_data.pct_change().dropna()
        return returns
    
    def calculate_expected_returns(self, returns: pd.DataFrame, method: str = 'mean') -> np.ndarray:
        """
        Calculate expected returns for each asset.
        
        Args:
            returns: DataFrame of historical returns
            method: 'mean' for historical mean, 'ewm' for exponentially weighted
            
        Returns:
            Array of expected returns
        """
        if method == 'mean':
            return returns.mean()
        elif method == 'ewm':
            return returns.ewm(span=252).mean().iloc[-1]
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def calculate_covariance_matrix(self, returns: pd.DataFrame, method: str = 'sample') -> np.ndarray:
        """
        Calculate covariance matrix of returns.
        
        Args:
            returns: DataFrame of historical returns
            method: 'sample' for sample covariance, 'ledoit-wolf' for shrinkage
            
        Returns:
            Covariance matrix (n_assets x n_assets)
        """
        if method == 'sample':
            # Annualize covariance (252 trading days)
            return returns.cov() * 252
        elif method == 'ledoit-wolf':
            from sklearn.covariance import LedoitWolf
            cov = LedoitWolf().fit(returns).covariance_
            return pd.DataFrame(cov, index=returns.columns, columns=returns.columns) * 252
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def portfolio_return(self, weights: np.ndarray, expected_returns: np.ndarray) -> float:
        """
        Calculate expected portfolio return.
        
        Args:
            weights: Portfolio weights (sum to 1)
            expected_returns: Expected returns for each asset
            
        Returns:
            Portfolio return
        """
        return np.sum(expected_returns * weights)
    
    def portfolio_volatility(self, weights: np.ndarray, cov_matrix: np.ndarray) -> float:
        """
        Calculate portfolio volatility (standard deviation).
        
        Args:
            weights: Portfolio weights
            cov_matrix: Covariance matrix
            
        Returns:
            Portfolio volatility
        """
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    def negative_sharpe_ratio(self, weights: np.ndarray, expected_returns: np.ndarray, cov_matrix: np.ndarray) -> float:
        """
        Calculate negative Sharpe ratio (for minimization).
        
        Args:
            weights: Portfolio weights
            expected_returns: Expected returns
            cov_matrix: Covariance matrix
            
        Returns:
            Negative Sharpe ratio
        """
        p_return = self.portfolio_return(weights, expected_returns)
        p_volatility = self.portfolio_volatility(weights, cov_matrix)
        return -(p_return - self.risk_free_rate) / p_volatility
    
    def optimize_portfolio(
        self,
        returns: pd.DataFrame,
        constraints: Dict = None,
        method: str = 'SLSQP'
    ) -> Dict:
        """
        Optimize portfolio to maximize Sharpe ratio.
        
        Args:
            returns: DataFrame of historical returns
            constraints: Optimization constraints
                - min_weight: Minimum weight per asset (default: 0.0)
                - max_weight: Maximum weight per asset (default: 1.0)
                - target_return: Target portfolio return (optional)
            method: Optimization method (SLSQP, L-BFGS-B)
            
        Returns:
            Dictionary with optimal weights, return, volatility, Sharpe ratio
        """
        # Prepare data
        expected_returns = self.calculate_expected_returns(returns)
        cov_matrix = self.calculate_covariance_matrix(returns)
        n_assets = len(expected_returns)
        
        # Set default constraints
        if constraints is None:
            constraints = {}
        
        min_weight = constraints.get('min_weight', 0.0)
        max_weight = constraints.get('max_weight', 1.0)
        
        # Initial guess (equal weights)
        init_guess = np.repeat(1 / n_assets, n_assets)
        
        # Bounds for each asset weight
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Constraints: weights sum to 1
        constraints_dict = {
            'type': 'eq',
            'fun': lambda weights: np.sum(weights) - 1
        }
        
        # Optimize
        result = minimize(
            fun=self.negative_sharpe_ratio,
            x0=init_guess,
            args=(expected_returns.values, cov_matrix.values),
            method=method,
            bounds=bounds,
            constraints=constraints_dict,
            options={'ftol': 1e-9}
        )
        
        if not result.success:
            raise ValueError(f"Optimization failed: {result.message}")
        
        # Calculate portfolio metrics
        optimal_weights = result.x
        opt_return = self.portfolio_return(optimal_weights, expected_returns.values)
        opt_volatility = self.portfolio_volatility(optimal_weights, cov_matrix.values)
        opt_sharpe = (opt_return - self.risk_free_rate) / opt_volatility
        
        return {
            'weights': dict(zip(returns.columns, optimal_weights)),
            'expected_return': opt_return,
            'expected_volatility': opt_volatility,
            'sharpe_ratio': opt_sharpe,
            'success': result.success
        }
    
    def calculate_efficient_frontier(
        self,
        returns: pd.DataFrame,
        num_portfolios: int = 100,
        min_weight: float = 0.0,
        max_weight: float = 1.0
    ) -> pd.DataFrame:
        """
        Calculate efficient frontier.
        
        Generate multiple portfolios with different target returns
        to plot the efficient frontier.
        
        Args:
            returns: DataFrame of historical returns
            num_portfolios: Number of portfolios to generate
            min_weight: Minimum weight per asset
            max_weight: Maximum weight per asset
            
        Returns:
            DataFrame with portfolio metrics (volatility, return, sharpe, weights)
        """
        expected_returns = self.calculate_expected_returns(returns)
        cov_matrix = self.calculate_covariance_matrix(returns)
        n_assets = len(expected_returns)
        
        # Calculate min and max returns
        min_ret = expected_returns.min()
        max_ret = expected_returns.max()
        
        # Generate target returns
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        efficient_portfolios = []
        
        for target_return in target_returns:
            # Optimize for this target return
            result = self._optimize_for_target_return(
                expected_returns.values,
                cov_matrix.values,
                target_return,
                min_weight,
                max_weight
            )
            
            if result['success']:
                efficient_portfolios.append({
                    'volatility': result['expected_volatility'],
                    'return': result['expected_return'],
                    'sharpe_ratio': (result['expected_return'] - self.risk_free_rate) / result['expected_volatility'],
                    'weights': result['weights']
                })
        
        return pd.DataFrame(efficient_portfolios)
    
    def _optimize_for_target_return(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        target_return: float,
        min_weight: float,
        max_weight: float
    ) -> Dict:
        """
        Optimize portfolio for a specific target return.
        
        Minimize volatility for a given target return.
        """
        n_assets = len(expected_returns)
        init_guess = np.repeat(1 / n_assets, n_assets)
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Constraints: weights sum to 1, target return
        constraints = [
            {
                'type': 'eq',
                'fun': lambda weights: np.sum(weights) - 1
            },
            {
                'type': 'eq',
                'fun': lambda weights: self.portfolio_return(weights, expected_returns) - target_return
            }
        ]
        
        # Minimize volatility
        result = minimize(
            fun=lambda weights: self.portfolio_volatility(weights, cov_matrix),
            x0=init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9}
        )
        
        if not result.success:
            return {'success': False}
        
        weights = result.x
        return {
            'weights': dict(enumerate(weights)),
            'expected_return': self.portfolio_return(weights, expected_returns),
            'expected_volatility': self.portfolio_volatility(weights, cov_matrix),
            'success': True
        }
```

---

### STEP 3: Create Portfolio Optimization Service (3 hours)

**File:** `apps/backend/src/robo_advisor/services/portfolio_optimization.py`

```python
from typing import Dict, List
from .mpt_engine import MPTEngine

class PortfolioOptimizationService:
    """
    Portfolio optimization service using multiple methods.
    """
    
    def __init__(self):
        self.mpt_engine = MPTEngine()
    
    def get_risk_based_allocation(self, risk_score: int) -> Dict:
        """
        Get simple risk-based allocation (quick method).
        
        Args:
            risk_score: 1-10 risk score
            
        Returns:
            Allocation dictionary
        """
        if risk_score <= 3:
            # Conservative
            return {
                'stocks': 0.20,
                'bonds': 0.70,
                'cash': 0.10
            }
        elif risk_score <= 6:
            # Moderate
            return {
                'stocks': 0.60,
                'bonds': 0.35,
                'cash': 0.05
            }
        else:
            # Aggressive
            return {
                'stocks': 0.90,
                'bonds': 0.08,
                'cash': 0.02
            }
    
    def optimize_mean_variance(
        self,
        returns_data: Dict[str, List[float]],
        constraints: Dict = None
    ) -> Dict:
        """
        Optimize portfolio using mean-variance optimization (Markowitz).
        """
        import pandas as pd
        
        df = pd.DataFrame(returns_data)
        result = self.mpt_engine.optimize_portfolio(df, constraints)
        return result
    
    def optimize_risk_parity(self, returns_data: Dict[str, List[float]]) -> Dict:
        """
        Optimize portfolio using risk parity (equal risk contribution).
        
        Each asset contributes equal amount of risk to portfolio.
        """
        import pandas as pd
        
        df = pd.DataFrame(returns_data)
        cov_matrix = self.mpt_engine.calculate_covariance_matrix(df)
        
        # Risk parity: each asset contributes equal risk
        # Weight = 1 / (σ_i * sqrt(sum(1/σ_j^2)))
        volatilities = np.sqrt(np.diag(cov_matrix))
        inv_vol = 1 / volatilities
        weights = inv_vol / inv_vol.sum()
        
        return {
            'weights': dict(zip(df.columns, weights)),
            'method': 'risk_parity'
        }
    
    def get_efficient_frontier(
        self,
        returns_data: Dict[str, List[float]],
        num_portfolios: int = 100
    ) -> List[Dict]:
        """
        Calculate efficient frontier for visualization.
        """
        import pandas as pd
        
        df = pd.DataFrame(returns_data)
        frontier_df = self.mpt_engine.calculate_efficient_frontier(df, num_portfolios)
        
        return frontier_df.to_dict('records')
```

---

### STEP 4: Create Goal Planning Service with Monte Carlo (3 hours) ⭐ IMPORTANT

**File:** `apps/backend/src/robo_advisor/services/goal_planning.py`

```python
import numpy as np
from typing import Dict

class GoalPlanningService:
    """
    Goal-based planning with Monte Carlo simulation.
    """
    
    def monte_carlo_goal_probability(
        self,
        initial_amount: float,
        monthly_contribution: float,
        years: int,
        expected_return: float,
        volatility: float,
        goal_amount: float,
        num_simulations: int = 10000
    ) -> Dict:
        """
        Run Monte Carlo simulation to estimate goal probability.
        
        Simulates thousands of possible scenarios using random returns
        from a normal distribution with the given mean and volatility.
        
        Args:
            initial_amount: Starting amount
            monthly_contribution: Monthly contribution
            years: Investment horizon in years
            expected_return: Expected annual return (e.g., 0.07 for 7%)
            volatility: Annual volatility (e.g., 0.15 for 15%)
            goal_amount: Target goal amount
            num_simulations: Number of Monte Carlo simulations
            
        Returns:
            Dictionary with probability and statistics
        """
        np.random.seed(42)  # For reproducibility
        
        # Convert to monthly
        monthly_return = expected_return / 12
        monthly_vol = volatility / np.sqrt(12)
        total_months = years * 12
        
        # Run simulations
        final_amounts = []
        
        for _ in range(num_simulations):
            amount = initial_amount
            
            for month in range(total_months):
                # Generate random return from normal distribution
                random_return = np.random.normal(monthly_return, monthly_vol)
                amount = amount * (1 + random_return) + monthly_contribution
            
            final_amounts.append(amount)
        
        final_amounts = np.array(final_amounts)
        
        # Calculate statistics
        success_count = np.sum(final_amounts >= goal_amount)
        probability_of_success = success_count / num_simulations
        
        return {
            'probability_of_success': probability_of_success,
            'median_final_amount': np.median(final_amounts),
            'mean_final_amount': np.mean(final_amounts),
            'percentile_10': np.percentile(final_amounts, 10),
            'percentile_90': np.percentile(final_amounts, 90),
            'num_simulations': num_simulations
        }
```

---

### STEP 5: Create API Endpoints (2 hours)

**File:** `apps/backend/src/robo_advisor/api/robo_advisor.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import RiskProfile, InvestmentGoal
from ..services.portfolio_optimization import PortfolioOptimizationService
from ..services.goal_planning import GoalPlanningService

class RoboAdvisorViewSet(viewsets.ViewSet):
    """
    Robo-advisor API endpoints.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optimization_service = PortfolioOptimizationService()
        self.goal_service = GoalPlanningService()
    
    @action(detail=False, methods=['get'])
    def assessment(self, request):
        """
        GET /api/robo-advisor/assessment
        Get risk assessment questionnaire.
        """
        from ..models import RiskQuestionnaire
        from ..serializers import RiskQuestionnaireSerializer
        
        questions = RiskQuestionnaire.objects.filter(is_active=True).order_by('order')
        serializer = RiskQuestionnaireSerializer(questions, many=True)
        
        return Response({
            'questions': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def assessment_submit(self, request):
        """
        POST /api/robo-advisor/assessment
        Submit risk questionnaire and calculate risk score.
        """
        responses = request.data.get('responses', {})
        
        # Calculate risk score (simple sum for example)
        risk_score = sum(responses.values()) // len(responses)
        
        # Determine risk tolerance
        if risk_score <= 3:
            risk_tolerance = 'CONSERVATIVE'
        elif risk_score <= 6:
            risk_tolerance = 'MODERATE'
        else:
            risk_tolerance = 'AGGRESSIVE'
        
        # Create or update risk profile
        profile, created = RiskProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'risk_score': risk_score,
                'risk_tolerance': risk_tolerance,
                'responses': responses
            }
        )
        
        if not created:
            profile.risk_score = risk_score
            profile.risk_tolerance = risk_tolerance
            profile.responses = responses
            profile.save()
        
        return Response({
            'risk_score': risk_score,
            'risk_tolerance': risk_tolerance
        })
    
    @action(detail=False, methods=['get'])
    def allocation(self, request):
        """
        GET /api/robo-advisor/allocation
        Get recommended asset allocation.
        """
        try:
            profile = request.user.risk_profile
        except RiskProfile.DoesNotExist:
            return Response(
                {'error': 'Complete risk assessment first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get risk-based allocation
        allocation = self.optimization_service.get_risk_based_allocation(
            profile.risk_score
        )
        
        return Response({
            'risk_tolerance': profile.risk_tolerance,
            'allocation': allocation
        })
    
    @action(detail=False, methods=['get'])
    def efficient_frontier(self, request):
        """
        GET /api/robo-advisor/efficient-frontier
        Get efficient frontier data for visualization.
        """
        # Get historical returns (you'll fetch this from your Asset model)
        returns_data = {
            'SPY': [0.01, 0.02, -0.01, ...],  # Replace with real data
            'AGG': [0.005, 0.003, 0.004, ...],
            'EFA': [0.008, 0.015, -0.005, ...]
        }
        
        frontier = self.optimization_service.get_efficient_frontier(returns_data)
        
        return Response({
            'frontier': frontier
        })
```

---

## 📚 COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Not Annualizing Returns
```python
# WRONG
returns = price_data.pct_change()
cov_matrix = returns.cov()  # This is DAILY covariance!

# CORRECT
returns = price_data.pct_change()
cov_matrix = returns.cov() * 252  # Annualize (252 trading days)
```

### ❌ Mistake 2: Not Handling Missing Data
```python
# WRONG - Will fail if there are NaN values
returns = price_data.pct_change()
cov_matrix = returns.cov()

# CORRECT - Drop NaN values
returns = price_data.pct_change().dropna()
cov_matrix = returns.cov() * 252
```

### ❌ Mistake 3: Wrong Constraint Format
```python
# WRONG
constraints = {'min_weight': 0.0, 'max_weight': 1.0}

# CORRECT - scipy.optimize expects tuple bounds
bounds = tuple((0.0, 1.0) for _ in range(n_assets))
```

### ❌ Mistake 4: Not Scaling Weights
```python
# WRONG - Weights might not sum to 1
weights = result.x

# CORRECT - Verify and normalize
weights = result.x
if not np.isclose(weights.sum(), 1.0):
    weights = weights / weights.sum()
```

### ❌ Mistake 5: Monte Carlo Seed Not Set
```python
# WRONG - Different results every time
final_amounts = [simulate() for _ in range(10000)]

# CORRECT - Reproducible results
np.random.seed(42)
final_amounts = [simulate() for _ in range(10000)]
```

---

## ❓ FAQ

**Q: How much historical data do I need for MPT?**  
A: Minimum 3 years (756 trading days), but 5-10 years is better. More data = more stable estimates.

**Q: What if scipy.optimize fails to converge?**  
A: Try different optimization methods ('SLSQP', 'L-BFGS-B', 'trust-constr') or simplify constraints.

**Q: How do I handle assets with different histories?**  
A: Use common date range (intersection of all assets) or pad missing data with mean returns.

**Q: Should I use log returns or simple returns?**  
A: Simple returns (pct_change) are standard for portfolio optimization. Log returns are for time series analysis.

**Q: How many Monte Carlo simulations should I run?**  
A: 10,000 is standard. More = more accurate but slower. Test with 1,000 first, then increase.

**Q: What risk-free rate should I use?**  
A: Use current 10-year Treasury yield (check: https://www.treasury.gov/resource-center/data-chart-center/interest-rates)

---

## 📦 FRONTEND IMPLEMENTATION GUIDE

### File: `apps/frontend/src/components/robo-advisor/RiskQuestionnaire.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface Question {
  id: string;
  question: string;
  type: 'MULTIPLE_CHOICE' | 'SCALE' | 'YES_NO';
  choices?: Array<{ label: string; value: number }>;
}

interface RiskQuestionnaireProps {
  questions: Question[];
  onComplete: (responses: Record<string, number>) => void;
}

export function RiskQuestionnaire({ questions, onComplete }: RiskQuestionnaireProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [responses, setResponses] = useState<Record<string, number>>({});
  
  const currentQuestion = questions[currentStep];
  const progress = ((currentStep + 1) / questions.length) * 100;
  
  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(responses);
    }
  };
  
  const handleResponse = (value: number) => {
    setResponses({ ...responses, [currentQuestion.id]: value });
  };
  
  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Question {currentStep + 1} of {questions.length}</span>
          <span>{Math.round(progress)}% Complete</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
      
      {/* Question */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold mb-6">{currentQuestion.question}</h2>
        
        {currentQuestion.type === 'SCALE' && (
          <ScaleQuestion onSelect={handleResponse} />
        )}
        
        {currentQuestion.type === 'MULTIPLE_CHOICE' && (
          <MultipleChoiceQuestion
            choices={currentQuestion.choices!}
            onSelect={handleResponse}
          />
        )}
        
        <div className="flex justify-between mt-8">
          <Button
            variant="outline"
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
          >
            Previous
          </Button>
          <Button onClick={handleNext}>
            {currentStep === questions.length - 1 ? 'Get Results' : 'Next'}
          </Button>
        </div>
      </div>
    </div>
  );
}

function ScaleQuestion({ onSelect }: { onSelect: (value: number) => void }) {
  const [value, setValue] = useState(5);
  
  return (
    <div className="space-y-4">
      <input
        type="range"
        min="1"
        max="10"
        value={value}
        onChange={(e) => setValue(Number(e.target.value))}
        className="w-full"
      />
      <div className="flex justify-between text-sm text-gray-600">
        <span>Conservative (1)</span>
        <span className="font-bold text-xl">{value}</span>
        <span>Aggressive (10)</span>
      </div>
      <Button
        className="w-full"
        onClick={() => onSelect(value)}
      >
        Confirm
      </Button>
    </div>
  );
}

function MultipleChoiceQuestion({
  choices,
  onSelect
}: {
  choices: Array<{ label: string; value: number }>;
  onSelect: (value: number) => void;
}) {
  return (
    <div className="space-y-3">
      {choices.map((choice) => (
        <Button
          key={choice.label}
          variant="outline"
          className="w-full text-left"
          onClick={() => onSelect(choice.value)}
        >
          {choice.label}
        </Button>
      ))}
    </div>
  );
}
```

---

## 📊 VISUALIZATION: Efficient Frontier Chart

**File:** `apps/frontend/src/components/robo-advisor/EfficientFrontier.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface FrontierPoint {
  volatility: number;
  return: number;
  sharpe_ratio: number;
}

interface EfficientFrontierProps {
  frontier: FrontierPoint[];
  optimalPoint?: FrontierPoint;
}

export function EfficientFrontier({ frontier, optimalPoint }: EfficientFrontierProps) {
  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="volatility"
            type="number"
            label={{ value: 'Risk (Volatility)', position: 'insideBottom', offset: -5 }}
            tickFormatter={(value) => `${(value * 100).toFixed(1)}%`}
          />
          <YAxis
            dataKey="return"
            type="number"
            label={{ value: 'Expected Return', angle: -90, position: 'insideLeft' }}
            tickFormatter={(value) => `${(value * 100).toFixed(1)}%`}
          />
          <Tooltip
            formatter={(value: number) => `${(value * 100).toFixed(2)}%`}
            contentStyle={{ backgroundColor: '#f4f4f5', border: '1px solid #d4d4d8' }}
          />
          <Scatter
            name="Efficient Frontier"
            data={frontier}
            fill="#3b82f6"
          />
          {optimalPoint && (
            <Scatter
              name="Optimal Portfolio"
              data={[optimalPoint]}
              fill="#ef4444"
              shape="star"
            />
          )}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## 📋 CHECKLIST BEFORE SUBMITTING

- [ ] All models created with base classes (UUIDModel, TimestampedModel, SoftDeleteModel)
- [ ] Migration created and applied
- [ ] MPT engine handles NaN values correctly
- [ ] Covariance matrix is annualized (multiplied by 252)
- [ ] Optimization constraints are properly formatted (bounds as tuples)
- [ ] Monte Carlo simulation uses random seed for reproducibility
- [ ] All API endpoints have authentication
- [ ] Frontend uses React Query for data fetching
- [ ] Charts use Recharts library
- [ ] All forms have loading states
- [ ] Error handling implemented
- [ ] Tests written for MPT engine
- [ ] Performance tested (optimization < 10 seconds)

---

## 🎯 SUCCESS CRITERIA

1. ✅ User can complete risk questionnaire in < 5 minutes
2. ✅ Portfolio optimization runs in < 10 seconds
3. ✅ Efficient frontier chart renders correctly
4. ✅ Monte Carlo simulation returns probability
5. ✅ Rebalancing suggestions are actionable
6. ✅ All API endpoints return correct data
7. ✅ Frontend is responsive on mobile

---

**Good luck! Start with Step 1 (models) and work through each step sequentially.**
