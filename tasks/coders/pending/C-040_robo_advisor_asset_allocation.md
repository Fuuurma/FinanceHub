# #️⃣ TASK: C-040 - Robo-Advisor Asset Allocation

**Task ID:** C-040
**Created:** February 1, 2026
**Assigned To:** Backend Coder (Linus)
**Status:** ⏳ PENDING
**Priority:** P1 HIGH
**Estimated Time:** 18-24 hours
**Deadline:** March 15, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Create an intelligent robo-advisor system that:
- Assesses user risk tolerance
- Recommends optimal asset allocation
- Provides portfolio rebalancing suggestions
- Tax-efficient allocation strategies
- Goal-based planning (retirement, growth, income)

---

## 📋 REQUIREMENTS

### 1. Robo-Advisor Models

```python
# apps/backend/src/investments/models/robo_advisor.py
class RiskProfile(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    risk_tolerance = CharField()  # 'conservative', 'moderate', 'aggressive'
    risk_score = IntegerField()  # 0-100
    time_horizon = IntegerField()  # Years
    investment_goal = CharField()  # 'retirement', 'growth', 'income', 'preservation'
    initial_investment = DecimalField(max_digits=12, decimal_places=2)
    monthly_contribution = DecimalField(max_digits=12, decimal_places=2)
    age = IntegerField()
    income = DecimalField(max_digits=12, decimal_places=2)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class AssetAllocation(models.Model):
    risk_profile = ForeignKey(RiskProfile)
    asset_class = CharField()  # 'stocks', 'bonds', 'crypto', 'cash', 'real_estate', 'commodities'
    target_percentage = DecimalField(max_digits=5, decimal_places=2)
    current_percentage = DecimalField(max_digits=5, decimal_places=2)
    drift_threshold = DecimalField(max_digits=5, decimal_places=2)  # Rebalance if drift exceeds this
    min_percentage = DecimalField(max_digits=5, decimal_places=2)
    max_percentage = DecimalField(max_digits=5, decimal_places=2)

class RebalancingSuggestion(models.Model):
    user = ForeignKey(User)
    portfolio = ForeignKey(Portfolio)
    suggested_allocation = JSONField()  # Target allocation
    current_allocation = JSONField()  # Current allocation
    trades_required = JSONField()  # Trades to rebalance
    estimated_cost = DecimalField(max_digits=10, decimal_places=2)
    tax_impact = CharField()  # 'low', 'medium', 'high'
    priority = CharField()  # 'low', 'medium', 'high'
    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()

class OptimizationResult(models.Model):
    user = ForeignKey(User)
    portfolio = ForeignKey(Porfolio)
    optimization_type = CharField()  # 'max_return', 'min_risk', 'max_sharpe'
    expected_return = DecimalField(max_digits=8, decimal_places=4)
    expected_volatility = DecimalField(max_digits=8, decimal_places=4)
    sharpe_ratio = DecimalField(max_digits=8, decimal_places=4)
    allocation = JSONField()  # Optimal allocation
    constraints = JSONField()  # Constraints applied
    created_at = DateTimeField(auto_now_add=True)
```

### 2. Robo-Advisor Service

```python
# apps/backend/src/investments/services/robo_advisor_service.py
import numpy as np
from scipy.optimize import minimize

class RoboAdvisorService:
    def assess_risk_tolerance(self, user: User, answers: dict) -> RiskProfile:
        """
        Assess user's risk tolerance based on questionnaire
        Questions cover:
        - Age, income, net worth
        - Investment experience
        - Reaction to market volatility
        - Time horizon
        - Investment goals
        """
        score = self._calculate_risk_score(answers)

        if score < 30:
            tolerance = 'conservative'
        elif score < 70:
            tolerance = 'moderate'
        else:
            tolerance = 'aggressive'

        profile = RiskProfile.objects.create(
            user=user,
            risk_tolerance=tolerance,
            risk_score=score,
            time_horizon=answers.get('time_horizon', 5),
            investment_goal=answers.get('goal', 'growth'),
            initial_investment=answers.get('initial_investment', 0),
            monthly_contribution=answers.get('monthly_contribution', 0),
            age=answers.get('age', 30),
            income=answers.get('income', 0)
        )

        return profile

    def recommend_allocation(self, risk_profile: RiskProfile) -> dict:
        """
        Recommend asset allocation based on risk profile
        Uses modern portfolio theory principles
        """
        tolerance = risk_profile.risk_tolerance
        horizon = risk_profile.time_horizon

        if tolerance == 'conservative':
            # 20% stocks, 50% bonds, 20% cash, 10% other
            allocation = {
                'stocks': 20,
                'bonds': 50,
                'cash': 20,
                'real_estate': 5,
                'commodities': 5
            }
        elif tolerance == 'moderate':
            # 60% stocks, 30% bonds, 5% cash, 5% other
            allocation = {
                'stocks': 60,
                'bonds': 30,
                'cash': 5,
                'real_estate': 3,
                'commodities': 2
            }
        else:  # aggressive
            # 90% stocks, 5% bonds, 0% cash, 5% other
            allocation = {
                'stocks': 90,
                'bonds': 5,
                'crypto': 3,
                'real_estate': 2
            }

        return allocation

    def optimize_portfolio(self, portfolio: Portfolio,
                          optimization_type: str = 'max_sharpe'):
        """
        Use mean-variance optimization to find optimal allocation
        Maximizes Sharpe ratio by default
        """
        # Get historical returns for assets in portfolio
        returns = self._get_historical_returns(portfolio)

        # Calculate expected returns and covariance matrix
        mean_returns = returns.mean()
        cov_matrix = returns.cov()

        # Optimization constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Sum to 100%
        ]

        bounds = [(0, 1) for _ in range(len(mean_returns))]  # 0-100% each

        # Objective function
        def objective(weights):
            portfolio_return = np.sum(mean_returns * weights)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = portfolio_return / portfolio_volatility

            if optimization_type == 'max_sharpe':
                return -sharpe_ratio  # Maximize Sharpe (negative for minimization)
            elif optimization_type == 'min_risk':
                return portfolio_volatility
            elif optimization_type == 'max_return':
                return -portfolio_return

        # Optimize
        result = minimize(
            objective,
            x0=np.ones(len(mean_returns)) / len(mean_returns),  # Equal weight start
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        optimal_weights = result.x

        # Calculate metrics
        expected_return = np.sum(mean_returns * optimal_weights)
        expected_volatility = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        sharpe_ratio = expected_return / expected_volatility

        # Save result
        optimization_result = OptimizationResult.objects.create(
            user=portfolio.user,
            portfolio=portfolio,
            optimization_type=optimization_type,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe_ratio,
            allocation=dict(zip(returns.columns, optimal_weights.tolist())),
            constraints={'sum_to_1': True, 'no_short': True}
        )

        return optimization_result

    def suggest_rebalancing(self, portfolio: Portfolio) -> RebalancingSuggestion:
        """
        Suggest trades to rebalance portfolio to target allocation
        """
        # Get user's risk profile
        risk_profile = RiskProfile.objects.filter(user=portfolio.user).first()

        if not risk_profile:
            raise ValueError("User needs to complete risk assessment first")

        # Get target allocation
        target_allocation = self.recommend_allocation(risk_profile)

        # Get current allocation
        current_allocation = self._get_current_allocation(portfolio)

        # Calculate drift for each asset class
        trades_required = []
        total_value = portfolio.total_value

        for asset_class, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_class, 0)
            drift = abs(current_pct - target_pct)

            if drift > 5:  # 5% threshold
                # Calculate trade needed
                target_value = total_value * (target_pct / 100)
                current_value = total_value * (current_pct / 100)
                trade_value = target_value - current_value

                trades_required.append({
                    'asset_class': asset_class,
                    'current_value': float(current_value),
                    'target_value': float(target_value),
                    'trade_value': float(trade_value),
                    'action': 'buy' if trade_value > 0 else 'sell'
                })

        # Estimate cost (assumes 0.1% trading cost)
        estimated_cost = sum(abs(t['trade_value']) for t in trades_required) * 0.001

        # Determine tax impact (simplified)
        tax_impact = 'medium' if any(t['action'] == 'sell' for t in trades_required) else 'low'

        suggestion = RebalancingSuggestion.objects.create(
            user=portfolio.user,
            portfolio=portfolio,
            suggested_allocation=target_allocation,
            current_allocation=current_allocation,
            trades_required=trades_required,
            estimated_cost=estimated_cost,
            tax_impact=tax_impact,
            priority='high' if len(trades_required) > 3 else 'medium',
            expires_at=timezone.now() + timedelta(days=7)
        )

        return suggestion

    def project_portfolio_growth(self, risk_profile: RiskProfile,
                                 years: int = 10) -> dict:
        """
        Project portfolio value over time using Monte Carlo simulation
        Returns percentiles (10th, 50th, 90th) of projected outcomes
        """
        initial = risk_profile.initial_investment
        monthly_contrib = risk_profile.monthly_contribution

        # Get expected return and volatility based on risk tolerance
        if risk_profile.risk_tolerance == 'conservative':
            expected_return = 0.05  # 5%
            volatility = 0.08  # 8%
        elif risk_profile.risk_tolerance == 'moderate':
            expected_return = 0.08  # 8%
            volatility = 0.14  # 14%
        else:  # aggressive
            expected_return = 0.11  # 11%
            volatility = 0.20  # 20%

        # Monte Carlo simulation (1000 scenarios)
        num_simulations = 1000
        projections = []

        for _ in range(num_simulations):
            portfolio_value = initial
            values = [portfolio_value]

            for month in range(years * 12):
                # Random return based on normal distribution
                monthly_return = np.random.normal(
                    expected_return / 12,
                    volatility / np.sqrt(12)
                )

                portfolio_value = portfolio_value * (1 + monthly_return) + monthly_contrib
                values.append(portfolio_value)

            projections.append(values)

        # Calculate percentiles at each time point
        percentiles = {}
        for percentile in [10, 50, 90]:
            values_at_percentile = []
            for month in range(years * 12 + 1):
                month_values = [proj[month] for proj in projections]
                percentile_value = np.percentile(month_values, percentile)
                values_at_percentile.append(percentile_value)
            percentiles[percentile] = values_at_percentile

        return {
            'years': years,
            'projections': percentiles,
            'median_final_value': percentiles[50][-1],
            'best_case_10th': percentiles[10][-1],
            'worst_case_90th': percentiles[90][-1]
        }
```

### 3. API Endpoints

```python
# apps/backend/src/investments/api/robo_advisor.py
from ninja import Router

router = Router()

@router.post("/robo-advisor/assess-risk")
def assess_risk_tolerance(request, answers: dict):
    """Assess user's risk tolerance from questionnaire"""
    pass

@router.get("/robo-advisor/allocation")
def get_recommended_allocation(request):
    """Get recommended asset allocation based on risk profile"""
    pass

@router.post("/robo-advisor/optimize")
def optimize_portfolio(request, portfolio_id: int,
                       optimization_type: str = 'max_sharpe'):
    """Optimize portfolio allocation"""
    pass

@router.get("/robo-advisor/rebalancing")
def get_rebalancing_suggestion(request, portfolio_id: int):
    """Get suggested trades to rebalance portfolio"""
    pass

@router.get("/robo-advisor/projections")
def get_growth_projections(request, years: int = 10):
    """Get Monte Carlo projections for portfolio growth"""
    pass

@router.get("/robo-advisor/risk-profile")
def get_risk_profile(request):
    """Get user's current risk profile"""
    pass
```

### 4. Frontend Components

```typescript
// apps/frontend/src/components/robo-advisor/RiskQuestionnaire.tsx
export function RiskQuestionnaire() {
  // Multi-step questionnaire:
  // 1. Age, income, net worth
  // 2. Investment experience
  // 3. Risk attitude questions
  // 4. Time horizon
  // 5. Investment goals
  // Calculate risk score
  // Create risk profile
}

// apps/frontend/src/components/robo-advisor/AllocationRecommendation.tsx
export function AllocationRecommendation({ riskProfile }: Props) {
  // Show recommended asset allocation
  // Pie chart of target allocation
  // Explanation of allocation
  // Expected return and risk
  // Comparison to current allocation
}

// apps/frontend/src/components/robo-advisor/RebalancingSuggestions.tsx
export function RebalancingSuggestions({ portfolioId }: Props) {
  // List trades needed to rebalance
  // Show current vs target allocation
  // Estimated cost of rebalancing
  - Tax impact assessment
  // Priority ranking
  // Execute rebalancing (future)
}

// apps/frontend/src/components/robo-advisor/GrowthProjectionChart.tsx
export function GrowthProjectionChart({ riskProfile }: Props) {
  // Monte Carlo projection chart
  // Show 10th, 50th, 90th percentiles
  - 5, 10, 20 year projections
  - Range of possible outcomes
  // Hover for details
}
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Risk tolerance questionnaire (10-15 questions)
- [ ] Risk profile creation (conservative/moderate/aggressive)
- [ ] Recommended asset allocation based on risk profile
- [ ] Portfolio optimization (max Sharpe ratio)
- [ ] Rebalancing suggestions with trade list
- [ ] Monte Carlo growth projections
- [ ] Expected return and volatility metrics
- [ ] Tax-efficient rebalancing consideration
- [ ] API endpoints for all operations
- [ ] Frontend questionnaire UI
- [ ] Allocation visualization
- [ ] Projection charts
- [ ] Tests for optimization algorithms
- [ ] Disclaimer about projections (not guarantees)

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/backend/src/investments/models/robo_advisor.py`
- `apps/backend/src/investments/services/robo_advisor_service.py`
- `apps/backend/src/investments/api/robo_advisor.py`
- `apps/backend/src/investments/tests/test_robo_advisor.py`
- `apps/frontend/src/components/robo-advisor/RiskQuestionnaire.tsx`
- `apps/frontend/src/components/robo-advisor/AllocationRecommendation.tsx`
- `apps/frontend/src/components/robo-advisor/RebalancingSuggestions.tsx`
- `apps/frontend/src/components/robo-advisor/GrowthProjectionChart.tsx`

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- Portfolio model exists
- Position model exists
- Historical returns data

**Python Libraries:**
- `numpy` - Numerical calculations
- `scipy` - Optimization algorithms
- `pandas` - Data manipulation

**Related Tasks:**
- None (standalone feature)

---

## 🎯 ALLOCATION MODELS

### Conservative (Risk Score: 0-30)
**Focus:** Capital preservation, income
**Allocation:**
- US Stocks: 15%
- International Stocks: 5%
- Bonds: 50%
- Cash: 20%
- Real Estate: 5%
- Commodities: 5%

**Expected Return:** 4-6%
**Volatility:** 5-8%

### Moderate (Risk Score: 30-70)
**Focus:** Balanced growth
**Allocation:**
- US Stocks: 45%
- International Stocks: 15%
- Bonds: 30%
- Cash: 5%
- Real Estate: 3%
- Commodities: 2%

**Expected Return:** 7-9%
**Volatility:** 10-14%

### Aggressive (Risk Score: 70-100)
**Focus:** Maximum growth
**Allocation:**
- US Stocks: 70%
- International Stocks: 20%
- Bonds: 5%
- Crypto: 3%
- Real Estate: 2%

**Expected Return:** 10-12%
**Volatility:** 18-22%

---

## 📊 DELIVERABLES

1. **Models:** RiskProfile, AssetAllocation, RebalancingSuggestion
2. **Service:** Robo-advisor with optimization, projections
3. **API:** All robo-advisor endpoints
4. **Frontend:** Questionnaire, allocation display, projections
5. **Optimization:** Mean-variance optimization implementation
6. **Monte Carlo:** 1000-scenario projection simulation
7. **Tests:** Unit tests for optimization
8. **Documentation:** Investment disclaimer

---

## 💬 NOTES

**Implementation Approach:**
- Use Modern Portfolio Theory (Markowitz)
- Mean-variance optimization for efficient frontier
- Monte Carlo for projections (1000 scenarios)
- Risk questionnaire based on industry standards

**Optimization Constraints:**
- Sum of weights = 100%
- No short selling (weights >= 0)
- Maximum weight per asset class (diversification)
- Minimum cash buffer (for emergencies)

**Projections Disclaimer:**
- "Past performance does not guarantee future results"
- "Projections are hypothetical"
- "Actual results may vary significantly"
- "Not financial advice, consult a professional"

**User Experience:**
- Simple questionnaire (5-10 minutes)
- Clear explanation of risk level
- Visual allocation recommendations
- What-if scenarios (different risk levels)
- Rebalancing reminders quarterly

**Libraries:**
- Backend: `numpy`, `scipy`, `pandas`
- Frontend: Chart libraries for projections

---

**Status:** ⏳ READY TO START
**Assigned To:** Backend Coder (Linus)
**User Value:** HIGH - retail investors want automated advice

---

#️⃣ *C-040: Robo-Advisor Asset Allocation*
*AI-powered portfolio optimization - risk assessment, allocation, rebalancing*
