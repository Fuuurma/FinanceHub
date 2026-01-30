# C-011: Portfolio Analytics Enhancement

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 10-14 hours  
**Dependencies:** None  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement advanced portfolio analytics including sector allocation, geographic breakdown, and performance attribution.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 4.2 - Portfolio Analytics):**

Current portfolio analytics need enhancement with:
- Sector allocation breakdown
- Geographic allocation
- Asset class allocation (stocks, bonds, crypto, cash)
- Concentration risk analysis
- Portfolio beta calculation
- Performance attribution by security, sector, factor

---

## ✅ CURRENT STATE

**What exists:**
- Basic portfolio tracking models in `apps/backend/src/investments/models/`
- Transaction history
- Basic portfolio value calculation

**What's missing:**
- Sector allocation API
- Geographic allocation API
- Concentration risk metrics
- Performance attribution calculations
- Portfolio beta calculation

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Schema** (2-3 hours)

**Add new models to `apps/backend/src/investments/models/portfolio_analytics.py`:**

```python
from django.db import models
from .portfolio import Portfolio
from .asset import Asset

class PortfolioSectorAllocation(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    sector = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

class PortfolioGeographicAllocation(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

class PortfolioConcentrationRisk(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    concentration_score = models.DecimalField(max_digits=5, decimal_places=2)
    concentration_level = models.CharField(max_length=20)  # LOW, MEDIUM, HIGH
    updated_at = models.DateTimeField(auto_now=True)

class PortfolioBeta(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    benchmark = models.ForeignKey(Asset, on_delete=models.CASCADE)
    beta = models.DecimalField(max_digits=10, decimal_places=4)
    calculated_at = models.DateTimeField(auto_now=True)
```

**Create migration:**
```bash
python manage.py makemigrations investments
python manage.py migrate
```

---

### **Phase 2: Analytics Services** (4-5 hours)

**Create `apps/backend/src/investments/services/analytics_service.py`:**

```python
from typing import Dict, List
from decimal import Decimal
from django.db.models import Sum, Q
from investments.models import Portfolio, PortfolioPosition, Asset
from investments.models.portfolio_analytics import (
    PortfolioSectorAllocation,
    PortfolioGeographicAllocation,
    PortfolioConcentrationRisk,
    PortfolioBeta
)

class PortfolioAnalyticsService:
    
    def calculate_sector_allocation(self, portfolio_id: int) -> List[Dict]:
        """
        Calculate sector breakdown of portfolio
        Returns: List of {sector, percentage, value}
        """
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related('asset')
        
        total_value = sum(p.current_value for p in positions)
        
        sectors = {}
        for position in positions:
            sector = position.asset.sector or "Unknown"
            if sector not in sectors:
                sectors[sector] = Decimal('0')
            sectors[sector] += position.current_value
        
        result = []
        for sector, value in sectors.items():
            result.append({
                'sector': sector,
                'value': float(value),
                'percentage': float((value / total_value) * 100) if total_value > 0 else 0
            })
        
        return sorted(result, key=lambda x: x['percentage'], reverse=True)
    
    def calculate_geographic_allocation(self, portfolio_id: int) -> List[Dict]:
        """
        Calculate geographic breakdown
        Returns: List of {country, percentage, value}
        """
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related('asset')
        
        total_value = sum(p.current_value for p in positions)
        
        countries = {}
        for position in positions:
            country = position.asset.country or "Unknown"
            if country not in countries:
                countries[country] = Decimal('0')
            countries[country] += position.current_value
        
        result = []
        for country, value in countries.items():
            result.append({
                'country': country,
                'value': float(value),
                'percentage': float((value / total_value) * 100) if total_value > 0 else 0
            })
        
        return sorted(result, key=lambda x: x['percentage'], reverse=True)
    
    def calculate_concentration_risk(self, portfolio_id: int) -> List[Dict]:
        """
        Calculate concentration risk by position
        Returns: List of {asset, concentration_score, concentration_level}
        """
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related('asset')
        
        total_value = sum(p.current_value for p in positions)
        
        result = []
        for position in positions:
            percentage = (position.current_value / total_value * 100) if total_value > 0 else 0
            
            # Risk scoring based on concentration
            if percentage > 20:
                level = "HIGH"
                score = Decimal('90')
            elif percentage > 10:
                level = "MEDIUM"
                score = Decimal('60')
            else:
                level = "LOW"
                score = Decimal('30')
            
            result.append({
                'asset_id': position.asset.id,
                'asset_symbol': position.asset.symbol,
                'concentration_score': float(score),
                'concentration_level': level,
                'percentage': float(percentage)
            })
        
        return sorted(result, key=lambda x: x['percentage'], reverse=True)
    
    def calculate_portfolio_beta(self, portfolio_id: int, benchmark_symbol: str = "SPY") -> Dict:
        """
        Calculate portfolio beta vs benchmark
        Returns: {beta, benchmark, calculated_at}
        """
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related('asset')
        
        total_value = sum(p.current_value for p in positions)
        
        # Weighted average beta
        weighted_beta = Decimal('0')
        
        for position in positions:
            weight = position.current_value / total_value if total_value > 0 else 0
            asset_beta = self._get_asset_beta(position.asset)
            weighted_beta += weight * asset_beta
        
        return {
            'beta': float(weighted_beta),
            'benchmark': benchmark_symbol,
            'calculated_at': timezone.now().isoformat()
        }
    
    def calculate_performance_attribution(self, portfolio_id: int) -> Dict:
        """
        Calculate performance attribution by sector
        Returns: {by_sector, total_return}
        """
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related('asset')
        
        # Group by sector
        sector_returns = {}
        
        for position in positions:
            sector = position.asset.sector or "Unknown"
            
            if sector not in sector_returns:
                sector_returns[sector] = {
                    'invested': Decimal('0'),
                    'current_value': Decimal('0'),
                    'return': Decimal('0')
                }
            
            sector_returns[sector]['invested'] += position.invested_amount
            sector_returns[sector]['current_value'] += position.current_value
        
        # Calculate returns
        result = {
            'by_sector': [],
            'total_return': 0
        }
        
        total_invested = sum(s['invested'] for s in sector_returns.values())
        total_current = sum(s['current_value'] for s in sector_returns.values())
        
        for sector, data in sector_returns.items():
            sector_return = ((data['current_value'] - data['invested']) / data['invested'] * 100) if data['invested'] > 0 else 0
            
            result['by_sector'].append({
                'sector': sector,
                'invested': float(data['invested']),
                'current_value': float(data['current_value']),
                'return_percentage': float(sector_return),
                'contribution': float((data['invested'] / total_invested * 100) if total_invested > 0 else 0)
            })
        
        result['total_return'] = float(((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0)
        
        return result
    
    def _get_asset_beta(self, asset: Asset) -> Decimal:
        """
        Get asset beta from historical data or calculate
        """
        # Try to get cached beta first
        from investments.models.portfolio_analytics import AssetBeta
        cached = AssetBeta.objects.filter(asset=asset).order_by('-calculated_at').first()
        
        if cached and cached.calculated_at > timezone.now() - timedelta(days=7):
            return cached.beta
        
        # Calculate beta (simplified - in production, use proper regression)
        # This is a placeholder - implement proper beta calculation
        return Decimal('1.0')
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/portfolio_analytics.py`:**

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from investments.services.analytics_service import PortfolioAnalyticsService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_sector_allocation(request, portfolio_id):
    """
    GET /api/portfolios/{id}/sector-allocation/
    Returns sector breakdown
    """
    service = PortfolioAnalyticsService()
    data = service.calculate_sector_allocation(portfolio_id)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_geographic_allocation(request, portfolio_id):
    """
    GET /api/portfolios/{id}/geographic-allocation/
    Returns geographic breakdown
    """
    service = PortfolioAnalyticsService()
    data = service.calculate_geographic_allocation(portfolio_id)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_concentration_risk(request, portfolio_id):
    """
    GET /api/portfolios/{id}/concentration-risk/
    Returns concentration risk analysis
    """
    service = PortfolioAnalyticsService()
    data = service.calculate_concentration_risk(portfolio_id)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_beta(request, portfolio_id):
    """
    GET /api/portfolios/{id}/beta/?benchmark=SPY
    Returns portfolio beta
    """
    benchmark = request.GET.get('benchmark', 'SPY')
    service = PortfolioAnalyticsService()
    data = service.calculate_portfolio_beta(portfolio_id, benchmark)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_performance_attribution(request, portfolio_id):
    """
    GET /api/portfolios/{id}/performance-attribution/
    Returns performance attribution by sector
    """
    service = PortfolioAnalyticsService()
    data = service.calculate_performance_attribution(portfolio_id)
    return Response(data)
```

**Update `apps/backend/src/api/urls.py`:**
```python
from .portfolio_analytics import (
    portfolio_sector_allocation,
    portfolio_geographic_allocation,
    portfolio_concentration_risk,
    portfolio_beta,
    portfolio_performance_attribution
)

urlpatterns = [
    # ... existing urls ...
    path('portfolios/<int:portfolio_id>/sector-allocation/', portfolio_sector_allocation),
    path('portfolios/<int:portfolio_id>/geographic-allocation/', portfolio_geographic_allocation),
    path('portfolios/<int:portfolio_id>/concentration-risk/', portfolio_concentration_risk),
    path('portfolios/<int:portfolio_id>/beta/', portfolio_beta),
    path('portfolios/<int:portfolio_id>/performance-attribution/', portfolio_performance_attribution),
]
```

---

### **Phase 4: Tests** (2-3 hours)

**Create `apps/backend/src/investments/tests/test_analytics_service.py`:**

```python
from django.test import TestCase
from investments.services.analytics_service import PortfolioAnalyticsService
from investments.models import Portfolio, PortfolioPosition, Asset

class PortfolioAnalyticsServiceTest(TestCase):
    
    def setUp(self):
        self.portfolio = Portfolio.objects.create(name="Test Portfolio", user=self.user)
        self.service = PortfolioAnalyticsService()
    
    def test_sector_allocation(self):
        # Test sector calculation
        data = self.service.calculate_sector_allocation(self.portfolio.id)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
    
    def test_concentration_risk(self):
        # Test concentration risk detection
        data = self.service.calculate_concentration_risk(self.portfolio.id)
        self.assertIsInstance(data, list)
        # Should detect high concentration
        high_concentration = [x for x in data if x['concentration_level'] == 'HIGH']
        self.assertTrue(len(high_concentration) > 0)
```

---

## 📋 DELIVERABLES

- [ ] Database models for analytics (Sector, Geographic, Concentration, Beta)
- [ ] AnalyticsService with 5 calculation methods
- [ ] 5 API endpoints for analytics data
- [ ] Unit tests for analytics calculations
- [ ] API documentation in OpenAPI/Swagger

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Sector allocation API returns percentage breakdown by sector
- [ ] Geographic allocation API returns country breakdown
- [ ] Concentration risk API identifies positions >20% as HIGH risk
- [ ] Portfolio beta API calculates weighted average beta
- [ ] Performance attribution API shows return contribution by sector
- [ ] All tests passing
- [ ] API documented in Swagger

---

## 📊 SUCCESS METRICS

- 5 new analytics endpoints
- Portfolio analytics calculation time <2 seconds
- Test coverage >80%
- API response time <500ms

---

## 🚀 NEXT STEPS AFTER COMPLETION

- Frontend: C-012 (Portfolio Analytics Dashboard)
- Frontend: Visual charts for allocation (pie charts, heatmaps)
- Backend: Cache analytics calculations (Redis)

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/011-portfolio-analytics-enhancement.md
