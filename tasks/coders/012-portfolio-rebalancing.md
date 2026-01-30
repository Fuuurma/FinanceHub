# C-012: Portfolio Rebalancing Tools

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 12-16 hours  
**Dependencies:** C-011 (Portfolio Analytics)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement portfolio rebalancing tools including drift alerts, what-if analysis, and suggested trades.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 4.3 - Rebalancing Tools):**

- Target allocation settings
- Drift alerts (when off target)
- What-if rebalancing analysis
- Suggested trades to rebalance
- Tax-efficient rebalancing (harvest losses)
- Automated rebalancing suggestions

---

## ✅ CURRENT STATE

**What exists:**
- Basic portfolio tracking
- Manual transaction entry

**What's missing:**
- Target allocation models
- Drift calculation
- Rebalancing recommendations
- Tax-loss harvesting suggestions

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (3-4 hours)

**Create `apps/backend/src/investments/models/rebalancing.py`:**

```python
from django.db import models
from .portfolio import Portfolio
from .asset import Asset

class TargetAllocation(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=50)  # stock, bond, crypto, cash
    target_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    tolerance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PortfolioDrift(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=50)
    current_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    target_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    drift_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    drift_level = models.CharField(max_length=20)  # WITHIN_TOLERANCE, WARNING, CRITICAL
    calculated_at = models.DateTimeField(auto_now=True)

class RebalancingSuggestion(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    action = models.CharField(max_length=10)  # BUY, SELL
    current_quantity = models.DecimalField(max_digits=20, decimal_places=4)
    suggested_quantity = models.DecimalField(max_digits=20, decimal_places=4)
    estimated_value = models.DecimalField(max_digits=20, decimal_places=2)
    priority = models.CharField(max_length=20)  # HIGH, MEDIUM, LOW
    tax_implication = models.CharField(max_length=20)  # GAIN, LOSS, NEUTRAL
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDING')  # PENDING, EXECUTED, CANCELLED
```

---

### **Phase 2: Rebalancing Service** (6-8 hours)

**Create `apps/backend/src/investments/services/rebalancing_service.py`:**

```python
from typing import List, Dict
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum
from investments.models import Portfolio, PortfolioPosition, Asset
from investments.models.rebalancing import (
    TargetAllocation,
    PortfolioDrift,
    RebalancingSuggestion
)

class RebalancingService:
    
    def calculate_drift(self, portfolio_id: int) -> List[Dict]:
        """
        Calculate allocation drift vs targets
        Returns: List of drift by asset type
        """
        # Get current allocation
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related('asset')
        
        total_value = sum(p.current_value for p in positions)
        
        current_allocation = {}
        for position in positions:
            asset_type = position.asset.asset_type
            if asset_type not in current_allocation:
                current_allocation[asset_type] = Decimal('0')
            current_allocation[asset_type] += position.current_value
        
        # Get target allocations
        targets = TargetAllocation.objects.filter(
            portfolio_id=portfolio_id
        )
        
        result = []
        for target in targets:
            current_value = current_allocation.get(target.asset_type, Decimal('0'))
            current_pct = (current_value / total_value * 100) if total_value > 0 else 0
            drift = current_pct - target.target_percentage
            
            # Determine drift level
            if abs(drift) <= target.tolerance_percentage:
                level = "WITHIN_TOLERANCE"
            elif abs(drift) <= target.tolerance_percentage * 2:
                level = "WARNING"
            else:
                level = "CRITICAL"
            
            result.append({
                'asset_type': target.asset_type,
                'current_percentage': float(current_pct),
                'target_percentage': float(target.target_percentage),
                'drift_percentage': float(drift),
                'drift_level': level
            })
        
        return result
    
    def generate_rebalancing_suggestions(self, portfolio_id: int) -> List[Dict]:
        """
        Generate trade suggestions to rebalance portfolio
        Returns: List of suggested trades
        """
        drift_data = self.calculate_drift(portfolio_id)
        portfolio = Portfolio.objects.get(id=portfolio_id)
        total_value = portfolio.current_value
        
        suggestions = []
        
        for drift in drift_data:
            if drift['drift_level'] == 'WITHIN_TOLERANCE':
                continue
            
            # Calculate required trade
            drift_value = (drift['drift_percentage'] / 100) * total_value
            
            if drift['drift_percentage'] > 0:
                # Overweight - sell
                action = 'SELL'
                priority = 'HIGH' if drift['drift_level'] == 'CRITICAL' else 'MEDIUM'
            else:
                # Underweight - buy
                action = 'BUY'
                priority = 'HIGH' if drift['drift_level'] == 'CRITICAL' else 'MEDIUM'
            
            suggestions.append({
                'asset_type': drift['asset_type'],
                'action': action,
                'value': float(abs(drift_value)),
                'priority': priority
            })
        
        return sorted(suggestions, key=lambda x: x['priority'], reverse=True)
    
    def calculate_tax_implications(self, portfolio_id: int, suggestions: List[Dict]) -> List[Dict]:
        """
        Calculate tax implications for suggested trades
        Returns: Suggestions with tax data
        """
        for suggestion in suggestions:
            if suggestion['action'] == 'SELL':
                # Check for loss harvesting opportunities
                positions = PortfolioPosition.objects.filter(
                    portfolio_id=portfolio_id,
                    asset__asset_type=suggestion['asset_type']
                )
                
                total_loss = Decimal('0')
                total_gain = Decimal('0')
                
                for position in positions:
                    unrealized_pnl = position.current_value - position.invested_amount
                    if unrealized_pnl < 0:
                        total_loss += abs(unrealized_pnl)
                    else:
                        total_gain += unrealized_pnl
                
                if total_loss > 0:
                    suggestion['tax_implication'] = 'LOSS_HARVESTING_OPPORTUNITY'
                    suggestion['tax_loss'] = float(total_loss)
                elif total_gain > 0:
                    suggestion['tax_implication'] = 'GAIN'
                    suggestion['tax_gain'] = float(total_gain)
                else:
                    suggestion['tax_implication'] = 'NEUTRAL'
            else:
                suggestion['tax_implication'] = 'NEUTRAL'
        
        return suggestions
    
    def what_if_analysis(self, portfolio_id: int, trades: List[Dict]) -> Dict:
        """
        Simulate what-if rebalancing scenario
        trades: List of {asset_type, action, value}
        Returns: New allocation breakdown
        """
        portfolio = Portfolio.objects.get(id=portfolio_id)
        
        # Get current allocation
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related('asset')
        
        allocation = {}
        for position in positions:
            asset_type = position.asset.asset_type
            if asset_type not in allocation:
                allocation[asset_type] = Decimal('0')
            allocation[asset_type] += position.current_value
        
        # Apply trades
        for trade in trades:
            asset_type = trade['asset_type']
            value = Decimal(str(trade['value']))
            
            if asset_type not in allocation:
                allocation[asset_type] = Decimal('0')
            
            if trade['action'] == 'BUY':
                allocation[asset_type] += value
            else:  # SELL
                allocation[asset_type] -= value
        
        # Calculate new percentages
        total_value = sum(allocation.values())
        new_allocation = {}
        
        for asset_type, value in allocation.items():
            new_allocation[asset_type] = {
                'value': float(value),
                'percentage': float((value / total_value * 100) if total_value > 0 else 0)
            }
        
        return new_allocation
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/rebalancing.py`:**

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from investments.services.rebalancing_service import RebalancingService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_drift(request, portfolio_id):
    """
    GET /api/portfolios/{id}/drift/
    Returns allocation drift analysis
    """
    service = RebalancingService()
    data = service.calculate_drift(portfolio_id)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rebalancing_suggestions(request, portfolio_id):
    """
    GET /api/portfolios/{id}/rebalance/suggestions/
    Returns rebalancing trade suggestions
    """
    service = RebalancingService()
    suggestions = service.generate_rebalancing_suggestions(portfolio_id)
    suggestions_with_tax = service.calculate_tax_implications(portfolio_id, suggestions)
    return Response(suggestions_with_tax)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def what_if_rebalancing(request, portfolio_id):
    """
    POST /api/portfolios/{id}/rebalance/what-if/
    Body: {trades: [{asset_type, action, value}]}
    Returns simulated allocation after trades
    """
    trades = request.data.get('trades', [])
    service = RebalancingService()
    result = service.what_if_analysis(portfolio_id, trades)
    return Response(result)
```

---

## 📋 DELIVERABLES

- [ ] Database models (TargetAllocation, PortfolioDrift, RebalancingSuggestion)
- [ ] RebalancingService with 4 methods
- [ ] 3 API endpoints
- [ ] Unit tests
- [ ] API documentation

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Drift calculation identifies allocations outside tolerance
- [ ] Suggestions prioritize trades (HIGH/MEDIUM/LOW)
- [ ] Tax-loss harvesting identified for SELL suggestions
- [ ] What-if analysis simulates new allocation
- [ ] All tests passing

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/012-portfolio-rebalancing.md
