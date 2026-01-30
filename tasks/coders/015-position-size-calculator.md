# C-015: Position Size Calculator & Risk Tools

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 8-12 hours  
**Dependencies:** None  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement position size calculator and risk management tools for portfolio protection.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 5.1 - Position Risk):**

- Position size calculator
- Portfolio risk score
- Stop-loss order recommendations
- Risk/reward ratio analysis
- Maximum drawdown tracking

---

## ✅ CURRENT STATE

**What exists:**
- Basic portfolio tracking
- Position data in PortfolioPosition model

**What's missing:**
- Position size calculation
- Risk metrics
- Stop-loss recommendations
- Risk/reward analysis

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Risk Calculation Service** (4-5 hours)

**Create `apps/backend/src/investments/services/risk_service.py`:**

```python
from typing import Dict, List
from decimal import Decimal
from investments.models import Portfolio, PortfolioPosition, Asset

class RiskManagementService:
    
    def calculate_position_size(self, portfolio_value: float, risk_percentage: float, stop_loss_pct: float) -> Dict:
        """
        Calculate optimal position size based on risk
        
        Args:
            portfolio_value: Total portfolio value
            risk_percentage: Max risk per trade (e.g., 1% = 0.01)
            stop_loss_pct: Stop loss percentage (e.g., 5% = 0.05)
        
        Returns:
            {position_size, max_loss, shares, risk_amount}
        """
        risk_amount = portfolio_value * risk_percentage
        position_size = risk_amount / stop_loss_pct
        
        return {
            'portfolio_value': portfolio_value,
            'risk_percentage': risk_percentage * 100,
            'risk_amount': risk_amount,
            'stop_loss_percentage': stop_loss_pct * 100,
            'position_size': position_size,
            'position_percentage': (position_size / portfolio_value * 100) if portfolio_value > 0 else 0
        }
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, target_price: float) -> Dict:
        """
        Calculate risk/reward ratio for a trade
        
        Returns:
            {risk, reward, ratio, verdict}
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(target_price - entry_price)
        ratio = reward / risk if risk > 0 else 0
        
        # Verdict
        if ratio >= 3:
            verdict = "EXCELLENT"
        elif ratio >= 2:
            verdict = "GOOD"
        elif ratio >= 1:
            verdict = "FAIR"
        else:
            verdict = "POOR"
        
        return {
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'risk_per_share': risk,
            'reward_per_share': reward,
            'risk_reward_ratio': round(ratio, 2),
            'verdict': verdict
        }
    
    def calculate_portfolio_risk_score(self, portfolio_id: int) -> Dict:
        """
        Calculate overall portfolio risk score (0-100)
        
        Returns:
            {risk_score, risk_level, factors}
        """
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related('asset')
        
        total_value = sum(p.current_value for p in positions)
        
        # Risk factors
        factors = []
        total_score = 0
        
        # 1. Concentration risk (0-25 points)
        max_position_pct = max((p.current_value / total_value * 100) for p in positions) if positions else 0
        if max_position_pct > 20:
            concentration_score = 25
            factors.append({'factor': 'Concentration', 'score': 25, 'note': f'Max position {max_position_pct:.1f}% is high'})
        elif max_position_pct > 10:
            concentration_score = 15
            factors.append({'factor': 'Concentration', 'score': 15, 'note': f'Max position {max_position_pct:.1f}% is moderate'})
        else:
            concentration_score = 5
            factors.append({'factor': 'Concentration', 'score': 5, 'note': f'Max position {max_position_pct:.1f}% is good'})
        
        total_score += concentration_score
        
        # 2. Volatility risk (0-25 points)
        # Simplified - in production, use historical volatility
        avg_volatility = sum(p.asset.volatility or 0.2 for p in positions) / len(positions) if positions else 0.2
        volatility_score = min(25, avg_volatility * 100)
        factors.append({'factor': 'Volatility', 'score': volatility_score, 'note': f'Avg volatility {avg_volatility*100:.1f}%'})
        total_score += volatility_score
        
        # 3. Asset class diversity (0-25 points)
        asset_classes = set(p.asset.asset_type for p in positions)
        diversity_score = max(0, 25 - len(asset_classes) * 5)
        factors.append({'factor': 'Diversity', 'score': diversity_score, 'note': f'{len(asset_classes)} asset classes'})
        total_score += diversity_score
        
        # 4. Leverage risk (0-25 points)
        # Assuming no leverage for now
        leverage_score = 0
        factors.append({'factor': 'Leverage', 'score': 0, 'note': 'No leverage'})
        total_score += leverage_score
        
        # Risk level
        if total_score < 30:
            risk_level = "LOW"
        elif total_score < 60:
            risk_level = "MODERATE"
        else:
            risk_level = "HIGH"
        
        return {
            'risk_score': round(total_score, 2),
            'risk_level': risk_level,
            'factors': factors
        }
    
    def recommend_stop_loss(self, position: PortfolioPosition, method: str = 'percentage') -> Dict:
        """
        Recommend stop-loss level for a position
        
        Methods:
        - percentage: Fixed % below entry (e.g., 5%)
        - atr: Based on Average True Range
        - support: Below support level
        
        Returns:
            {stop_loss_price, method, reasoning}
        """
        entry_price = position.average_cost
        
        if method == 'percentage':
            # Default 5% stop loss
            stop_loss_pct = Decimal('0.05')
            stop_loss_price = entry_price * (1 - stop_loss_pct)
            reasoning = f"5% trailing stop loss"
        
        elif method == 'atr':
            # Calculate ATR (simplified - use historical data in production)
            # Placeholder: 2x ATR
            atr = entry_price * Decimal('0.02')  # Assume 2% daily range
            stop_loss_price = entry_price - (2 * atr)
            reasoning = f"2x ATR stop loss"
        
        elif method == 'support':
            # Find recent support level (simplified)
            # In production, query recent lows from price history
            support_level = entry_price * Decimal('0.95')  # Assume support at 5% below
            stop_loss_price = support_level
            reasoning = f"Support level at {support_level:.2f}"
        
        else:
            stop_loss_price = entry_price * Decimal('0.95')
            reasoning = "Default 5% stop loss"
        
        return {
            'position_id': position.id,
            'asset_symbol': position.asset.symbol,
            'entry_price': float(entry_price),
            'stop_loss_price': float(stop_loss_price),
            'stop_loss_percentage': float(((entry_price - stop_loss_price) / entry_price * 100)),
            'method': method,
            'reasoning': reasoning
        }
```

---

### **Phase 2: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/risk_management.py`:**

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from investments.services.risk_service import RiskManagementService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_position_size(request):
    """
    POST /api/risk/position-size/
    Body: {portfolio_value, risk_percentage, stop_loss_pct}
    Returns position size recommendation
    """
    data = request.data
    service = RiskManagementService()
    result = service.calculate_position_size(
        portfolio_value=float(data['portfolio_value']),
        risk_percentage=float(data['risk_percentage']),
        stop_loss_pct=float(data['stop_loss_pct'])
    )
    return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_risk_reward(request):
    """
    POST /api/risk/risk-reward/
    Body: {entry_price, stop_loss, target_price}
    Returns risk/reward analysis
    """
    data = request.data
    service = RiskManagementService()
    result = service.calculate_risk_reward_ratio(
        entry_price=float(data['entry_price']),
        stop_loss=float(data['stop_loss']),
        target_price=float(data['target_price'])
    )
    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_risk_score(request, portfolio_id):
    """
    GET /api/portfolios/{id}/risk-score/
    Returns portfolio risk analysis
    """
    service = RiskManagementService()
    result = service.calculate_portfolio_risk_score(portfolio_id)
    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stop_loss_recommendation(request, position_id, method='percentage'):
    """
    GET /api/positions/{id}/stop-loss/?method=percentage
    Returns stop-loss recommendation
    """
    position = PortfolioPosition.objects.get(id=position_id)
    service = RiskManagementService()
    result = service.recommend_stop_loss(position, method)
    return Response(result)
```

---

### **Phase 3: Frontend Components** (2-3 hours)

**Create `apps/frontend/src/components/risk/PositionSizeCalculator.tsx`:**

```typescript
import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';

export const PositionSizeCalculator: React.FC = () => {
  const [portfolioValue, setPortfolioValue] = useState(10000);
  const [riskPct, setRiskPct] = useState(1);
  const [stopLossPct, setStopLossPct] = useState(5);
  
  const { data: result, mutate: calculate } = useMutation({
    mutationFn: () => api.post('/api/risk/position-size/', {
      portfolio_value: portfolioValue,
      risk_percentage: riskPct / 100,
      stop_loss_pct: stopLossPct / 100
    })
  });
  
  return (
    <div className="position-size-calculator">
      <h2>Position Size Calculator</h2>
      
      <div className="input-group">
        <label>Portfolio Value ($)</label>
        <input type="number" value={portfolioValue} onChange={e => setPortfolioValue(Number(e.target.value))} />
      </div>
      
      <div className="input-group">
        <label>Risk per Trade (%)</label>
        <input type="number" value={riskPct} onChange={e => setRiskPct(Number(e.target.value))} />
      </div>
      
      <div className="input-group">
        <label>Stop Loss (%)</label>
        <input type="number" value={stopLossPct} onChange={e => setStopLossPct(Number(e.target.value))} />
      </div>
      
      <button onClick={() => calculate()}>Calculate</button>
      
      {result && (
        <div className="results">
          <h3>Results</h3>
          <p>Position Size: ${result.data.position_size.toFixed(2)}</p>
          <p>Max Loss: ${result.data.risk_amount.toFixed(2)}</p>
          <p>Position % of Portfolio: {result.data.position_percentage.toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
};
```

---

## 📋 DELIVERABLES

- [ ] RiskManagementService with 4 methods
- [ ] 4 API endpoints
- [ ] Frontend PositionSizeCalculator component
- [ ] Frontend RiskRewardAnalyzer component
- [ ] Unit tests
- [ ] API documentation

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Position size calculator returns correct allocation
- [ ] Risk/reward ratio calculates properly (reward/risk)
- [ ] Portfolio risk score returns 0-100 scale
- [ ] Stop loss recommendations use 3 methods
- [ ] All tests passing

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/015-position-size-calculator.md
