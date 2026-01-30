# Task C-040: Robo-Advisor Asset Allocation

**Priority:** P1 HIGH  
**Estimated Time:** 18-24 hours  
**Assigned To:** Backend Coder + Frontend Coder  
**Status:** PENDING

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

## Technical Requirements

### Backend
- **Files to Create:**
  - `apps/backend/src/robo_advisor/models/risk_profile.py`
  - `apps/backend/src/robo_advisor/services/portfolio_optimization.py`
  - `apps/backend/src/robo_advisor/services/mpt_engine.py`
  - `apps/backend/src/robo_advisor/services/goal_planning.py`
  - `apps/backend/src/robo_advisor/api/robo_advisor.py`

- **Database Schema:**
  ```python
  class RiskProfile(UUIDModel, TimestampedModel):
      user = OneToOneField(User, on_delete=CASCADE)
      risk_score = IntegerField()  # 1-10
      risk_tolerance = CharField(choices=[('CONSERVATIVE', 'C'), ('MODERATE', 'M'), ('AGGRESSIVE', 'A')])
      time_horizon = IntegerField()  # years
      investment_objective = CharField(max_length=50)  # growth, income, preservation
      
  class RecommendedAllocation(UUIDModel, TimestampedModel):
      user = ForeignKey(User, on_delete=CASCADE)
      risk_profile = ForeignKey(RiskProfile, on_delete=CASCADE)
      asset = ForeignKey(Asset, on_delete=PROTECT)
      target_allocation = FloatField()  # 0.0 to 1.0
      expected_return = FloatField()
      expected_risk = FloatField()
      
  class InvestmentGoal(UUIDModel, TimestampedModel):
      user = ForeignKey(User, on_delete=CASCADE)
      goal_type = CharField(max_length=50)  # retirement, college, house
      target_amount = DecimalField(max_digits=14, decimal_places=2)
      current_amount = DecimalField(max_digits=14, decimal_places=2)
      target_date = DateField()
      monthly_contribution = DecimalField(max_digits=12, decimal_places=2)
      probability_of_success = FloatField()
  ```

- **Libraries:**
  - `scipy.optimize` - Portfolio optimization
  - `numpy` - Matrix operations
  - `pandas` - Data manipulation
  - `cvxpy` - Convex optimization (optional)
  - `arch` - GARCH models for volatility forecasting

- **Portfolio Optimization (MPT):**
  ```python
  def optimize_portfolio(returns, risk_free_rate=0.02):
      # returns: DataFrame of historical returns
      # Returns: optimal weights, expected return, expected risk
      # Maximize Sharpe Ratio: (Rp - Rf) / σp
  ```

- **Efficient Frontier:**
  ```python
  def calculate_efficient_frontier(returns, num_portfolios=100):
      # Generate 100 portfolios with different risk/return
      # Return: efficient frontier data for chart
  ```

- **Monte Carlo Simulation:**
  ```python
  def monte_carlo_goal_probability(initial, contribution, years, return_mean, return_std, goal):
      # Run 10,000 simulations
      # Return: probability of reaching goal
  ```

### Frontend
- **Files to Create:**
  - `apps/frontend/src/app/(dashboard)/robo-advisor/page.tsx`
  - `apps/frontend/src/app/(dashboard)/robo-advisor/assessment/page.tsx`
  - `apps/frontend/src/components/robo-advisor/RiskQuestionnaire.tsx`
  - `apps/frontend/src/components/robo-advisor/AllocationChart.tsx`
  - `apps/frontend/src/components/robo-advisor/EfficientFrontier.tsx`
  - `apps/frontend/src/components/robo-advisor/RebalancingTool.tsx`
  - `apps/frontend/src/components/robo-advisor/GoalPlanner.tsx`
  - `apps/frontend/src/lib/api/robo-advisor.ts`

- **Risk Questionnaire:**
  - Multi-step form (wizard)
  - Progress indicator
  - Range sliders for numeric answers
  - Radio buttons for multiple choice
  - Real-time risk score calculation
  - Explain risk profile at end

- **Visualizations:**
  - Efficient frontier scatter plot (risk vs return)
  - Allocation pie chart (by asset class)
  - Monte Carlo simulation histogram
  - Goal progress gauge
  - Use Recharts for charts

- **State Management:**
  - `roboAdvisorStore.ts` for risk profile and recommendations
  - React Query for data fetching
  - Form state for questionnaire

## Dependencies
- **Prerequisites:** C-001 (User System), C-002 (Asset Management), C-005 (Portfolio Core), C-011 (Portfolio Analytics)
- **Related Tasks:** C-012 (Portfolio Rebalancing), C-022 (Strategy Backtesting), C-026 (VaR Calculator)

## Testing Requirements
- **Backend:**
  - Test MPT optimization accuracy
  - Test efficient frontier calculation
  - Test portfolio constraints handling
  - Test Monte Carlo simulation convergence
  - Test risk profile scoring

- **Frontend:**
  - Test questionnaire flow
  - Test allocation chart rendering
  - Test rebalancing suggestions
  - Test goal probability calculation
  - Test responsive design

## Performance Considerations
- Cache optimization results (user-specific, 1-hour TTL)
- Use pre-computed efficient frontier for risk profiles
- Monte Carlo simulations are expensive, run asynchronously
- Use Celery/Dramatiq for background tasks
- Store simulation results for retrieval

## Success Metrics
- Risk questionnaire completes in < 5 minutes
- Portfolio optimization runs in < 10 seconds
- Rebalancing suggestions are actionable
- Users report high satisfaction with recommendations
- Goal probability estimates are accurate (backtest)

## Notes
- Robo-advisors are EXCELLENT user engagement features
- Start with simple 3-fund portfolio (Total US, Total Intl, Total Bond)
- Efficient frontier is complex, simplify visualization
- Monte Carlo requires many simulations (10,000+), use caching
- Risk questionnaire should be simple (5-10 questions max)
- Consider "age-based" glide path (target date funds)
- Consider "ethical investing" filters (ESG)
- Consider "tax-efficient" allocations
- Always add disclaimer: "Past performance ≠ future results"
- Robo-advisor should be a starting point, not financial advice

## Future Enhancements
- AI-powered allocation (ML models)
- Dynamic risk adjustment (market volatility)
- Factor investing (value, momentum, quality)
- Direct indexing instead of ETFs
- Tax-loss harvesting automation
- Smart beta strategies
- Alternative assets (real estate, private equity)
- Retirement withdrawal strategies
- Social Security optimization
