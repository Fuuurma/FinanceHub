# Task C-015: Position Size Calculator & Risk Tools

**Priority:** P1 HIGH  
**Estimated Time:** 8-12 hours  
**Assigned To:** Backend Coder  
**Status:** PENDING

## ⚡ Quick Start Guide

**What to do FIRST (in order):**

1. **Backend (Step 1):** Create risk service (3h) - Position size, risk/reward calculations
2. **Backend (Step 2):** Create API endpoints (2h) - 4 REST endpoints
3. **Backend (Step 3):** Create risk metrics (2h) - Portfolio risk score, VaR
4. **Frontend (Step 4):** Create calculator form (1.5h) - Position size calculator UI
5. **Frontend (Step 5):** Create risk analysis page (1.5h) - Display risk metrics
6. **Testing (Step 6):** Write tests (1h) - Test calculations

**Total: 9 hours (estimate)**

---

## Overview
Implement position size calculator and risk management tools for portfolio protection.

---

## 🔧 STEP-BY-STEP IMPLEMENTATION GUIDE

### STEP 1: Create Risk Management Service (3 hours) ⭐ CRITICAL

**File:** `apps/backend/src/investments/services/risk_service.py`

```python
from typing import Dict, List
from decimal import Decimal

class RiskManagementService:
    """
    Risk management and position sizing service.
    
    Helps traders:
    - Calculate optimal position sizes
    - Manage risk per trade
    - Calculate stop-loss levels
    - Analyze risk/reward ratios
    """
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        account_balance: float,
        risk_per_trade: float,
        entry_price: float,
        stop_loss_price: float
    ) -> Dict:
        """
        Calculate optimal position size using fixed fractional method.
        
        Formula:
        Position Size = (Account Balance × Risk Per Trade) / (Entry Price - Stop Loss)
        
        Args:
            portfolio_value: Total portfolio value
            account_balance: Available cash for trading
            risk_per_trade: Risk per trade (e.g., 0.01 for 1%)
            entry_price: Entry price per share
            stop_loss_price: Stop loss price per share
        
        Returns:
            Dictionary with position size details
        """
        # Calculate risk amount (dollar amount to risk)
        risk_amount = account_balance * risk_per_trade
        
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            return {
                'error': 'Entry price and stop loss cannot be the same'
            }
        
        # Calculate position size (number of shares)
        position_shares = risk_amount / risk_per_share
        
        # Calculate position value
        position_value = position_shares * entry_price
        
        # Calculate max loss (if stop loss is hit)
        max_loss = position_shares * risk_per_share
        
        # Calculate position as percentage of portfolio
        position_pct = (position_value / portfolio_value * 100) if portfolio_value > 0 else 0
        
        return {
            'position_shares': round(position_shares, 2),
            'position_value': round(position_value, 2),
            'position_percentage': round(position_pct, 2),
            'risk_amount': round(risk_amount, 2),
            'risk_per_share': round(risk_per_share, 2),
            'max_loss': round(max_loss, 2),
            'max_loss_percentage': round((max_loss / account_balance * 100), 2),
            'stop_loss_distance': round(risk_per_share / entry_price * 100, 2)
        }
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        stop_loss_pct: float,
        position_type: str = 'LONG'
    ) -> float:
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price
            stop_loss_pct: Stop loss percentage (e.g., 0.05 for 5%)
            position_type: 'LONG' or 'SHORT'
        
        Returns:
            Stop loss price
        """
        if position_type == 'LONG':
            # Long: Stop loss below entry
            return entry_price * (1 - stop_loss_pct)
        else:
            # Short: Stop loss above entry
            return entry_price * (1 + stop_loss_pct)
    
    def calculate_risk_reward_ratio(
        self,
        entry_price: float,
        stop_loss: float,
        target_price: float
    ) -> Dict:
        """
        Calculate risk/reward ratio.
        
        R/R Ratio = (Target Price - Entry) / (Entry - Stop Loss)
        
        Guidelines:
        - R/R >= 3.0: EXCELLENT
        - R/R >= 2.0: GOOD
        - R/R >= 1.0: FAIR
        - R/R < 1.0: POOR
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            target_price: Target/profit price
        
        Returns:
            Dictionary with R/R analysis
        """
        # Calculate risk and reward
        risk = abs(entry_price - stop_loss)
        reward = abs(target_price - entry_price)
        
        if risk == 0:
            return {
                'error': 'Risk cannot be zero (entry and stop loss are the same)'
            }
        
        # Calculate ratio
        ratio = reward / risk
        
        # Determine verdict
        if ratio >= 3.0:
            verdict = 'EXCELLENT'
            color = 'green'
        elif ratio >= 2.0:
            verdict = 'GOOD'
            color = 'blue'
        elif ratio >= 1.0:
            verdict = 'FAIR'
            color = 'yellow'
        else:
            verdict = 'POOR'
            color = 'red'
        
        return {
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'risk_per_share': round(risk, 2),
            'reward_per_share': round(reward, 2),
            'risk_reward_ratio': round(ratio, 2),
            'verdict': verdict,
            'color': color
        }
    
    def calculate_portfolio_risk_score(
        self,
        positions: List[Dict]
    ) -> Dict:
        """
        Calculate overall portfolio risk score.
        
        Factors:
        - Concentration risk (single position > 20%)
        - Correlation risk (highly correlated assets)
        - Volatility risk (overall portfolio volatility)
        
        Args:
            positions: List of position dicts with {symbol, value, volatility}
        
        Returns:
            Portfolio risk analysis
        """
        if not positions:
            return {
                'risk_score': 0,
                'risk_level': 'NONE',
                'factors': []
            }
        
        total_value = sum(p['value'] for p in positions)
        risk_factors = []
        risk_score = 0
        
        # Concentration risk
        max_position_pct = max((p['value'] / total_value * 100) for p in positions)
        if max_position_pct > 20:
            risk_score += 20
            risk_factors.append({
                'type': 'CONCENTRATION',
                'severity': 'HIGH',
                'description': f'Max position is {max_position_pct:.1f}% (>20% recommended)'
            })
        elif max_position_pct > 10:
            risk_score += 10
            risk_factors.append({
                'type': 'CONCENTRATION',
                'severity': 'MEDIUM',
                'description': f'Max position is {max_position_pct:.1f}%'
            })
        
        # Volatility risk
        avg_volatility = sum(p.get('volatility', 0.2) for p in positions) / len(positions)
        if avg_volatility > 0.4:
            risk_score += 20
            risk_factors.append({
                'type': 'VOLATILITY',
                'severity': 'HIGH',
                'description': f'High volatility: {avg_volatility:.1%}'
            })
        elif avg_volatility > 0.25:
            risk_score += 10
            risk_factors.append({
                'type': 'VOLATILITY',
                'severity': 'MEDIUM',
                'description': f'Moderate volatility: {avg_volatility:.1%}'
            })
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'VERY HIGH'
        elif risk_score >= 30:
            risk_level = 'HIGH'
        elif risk_score >= 15:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'factors': risk_factors
        }
```

---

### STEP 2: Create API Endpoints (2 hours)

**File:** `apps/backend/src/api/risk_management.py`

```python
from ninja import Router
from pydantic import BaseModel
from investments.services.risk_service import RiskManagementService

router = Router()
risk_service = RiskManagementService()

class PositionSizeRequest(BaseModel):
    portfolio_value: float
    account_balance: float
    risk_per_trade: float
    entry_price: float
    stop_loss_price: float

@router.post("/risk/position-size")
def calculate_position_size(request, data: PositionSizeRequest):
    """Calculate optimal position size."""
    result = risk_service.calculate_position_size(
        data.portfolio_value,
        data.account_balance,
        data.risk_per_trade,
        data.entry_price,
        data.stop_loss_price
    )
    return result

@router.get("/risk/risk-reward")
def calculate_risk_reward(request, entry: float, stop: float, target: float):
    """Calculate risk/reward ratio."""
    return risk_service.calculate_risk_reward_ratio(entry, stop, target)

@router.post("/risk/portfolio-score")
def calculate_portfolio_risk(request, positions: list):
    """Calculate portfolio risk score."""
    return risk_service.calculate_portfolio_risk_score(positions)
```

---

## 📚 COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Not Checking for Zero Risk
```python
# WRONG - Division by zero error
position_size = risk_amount / (entry_price - stop_loss_price)

# CORRECT - Check first
risk_per_share = entry_price - stop_loss_price
if risk_per_share == 0:
    return {'error': 'Invalid stop loss'}
position_size = risk_amount / risk_per_share
```

### ❌ Mistake 2: Risking Too Much Per Trade
```python
# WRONG - 5% risk per trade is too high
risk_per_trade = 0.05  # 5% - WILL BLOW ACCOUNT SOON

# CORRECT - 1% max risk per trade
risk_per_trade = 0.01  # 1% - PROFESSIONAL STANDARD
```

### ❌ Mistake 3: Ignoring Position Size Limits
```python
# WRONG - Could be 100% of portfolio
position_shares = risk_amount / risk_per_share

# CORRECT - Limit to 20% max
position_pct = (position_shares * entry_price) / portfolio_value
if position_pct > 0.20:
    position_shares = (portfolio_value * 0.20) / entry_price
```

### ❌ Mistake 4: Wrong Risk/Reward Interpretation
```python
# WRONG - Takes low R/R trades
if ratio > 0.5:  # This is POOR
    return 'GOOD'

# CORRECT - Only take 2:1 or better
if ratio >= 2.0:
    return 'GOOD'
elif ratio >= 1.0:
    return 'FAIR'
else:
    return 'POOR'
```

### ❌ Mistake 5: Not Accounting for Slippage
```python
# WRONG - Assumes perfect execution
stop_loss = entry_price * 0.95

# CORRECT - Add buffer for slippage
stop_loss = entry_price * 0.94  # Extra 1% buffer
```

---

## ❓ FAQ

**Q: What's the ideal risk per trade?**  
A: 1% of account balance. This is the professional standard. Never exceed 2%.

**Q: What's a good risk/reward ratio?**  
A: Minimum 2:1. Ideally 3:1 or better. This means you risk $1 to make $2 or $3.

**Q: How much should I allocate to one position?**  
A: Maximum 20% of portfolio. Ideally 5-10% per position for diversification.

**Q: Where should I set my stop loss?**  
A: Below a recent swing low (for longs) or above a swing high (for shorts). Use technical levels, not arbitrary percentages.

**Q: What if the position size calculation says 1000 shares but I can only afford 500?**  
A: Use 500 shares. Never over-leverage. Reduce risk or wait for better entry.

**Q: Should I adjust position size based on volatility?**  
A: YES! Reduce position size for high-volatility assets, increase for low-volatility.

**Q: How do I calculate risk for crypto?**  
A: Same formula, but use wider stops (10-20%) due to higher volatility.

---

## 📋 CHECKLIST BEFORE SUBMITTING

- [ ] RiskManagementService created
- [ ] Position size calculation accurate
- [ ] Risk/reward calculation working
- [ ] Portfolio risk score calculation
- [ ] API endpoints created
- [ ] Input validation (no zero risk)
- [ ] Position size limits enforced (max 20%)
- [ ] Stop loss calculator working
- [ ] Tests written
- [ ] Frontend calculator form created
- [ ] Risk analysis page created

---

## 🎯 SUCCESS CRITERIA

1. ✅ Position size calculator accurate
2. ✅ Risk/reward ratio correct
3. ✅ Portfolio risk score calculated
4. ✅ Stop loss recommendations provided
5. ✅ API endpoints working
6. ✅ Frontend calculator functional
7. ✅ Risk limits enforced (max 20% per position)
8. ✅ All edge cases handled

---

**Start with Step 1 (risk service) and work through each step sequentially.**
