# C-027: Universal Asset Search & Discovery Engine

**Priority:** P0 - CRITICAL  
**Assigned to:** Backend Coder  
**Estimated Time:** 12-16 hours  
**Dependencies:** C-005 (Backend Improvements)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive universal search engine that supports searching across all asset classes (stocks, crypto, ETF, forex, commodities, bonds) with advanced filtering, auto-suggestions, and intelligent ranking.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 1.1 - Asset Search & Screening):**

- Universal search bar (stocks, crypto, ETF, forex, commodities, bonds)
- Advanced screening filters:
  - Market cap ranges
  - Sector/industry classification
  - P/E ratio, P/B ratio
  - Dividend yield
  - Volume criteria
  - Technical indicators (RSI, MACD levels)
  - Geographic regions
- Custom screen builders with save/load
- Pre-built screen templates (value stocks, growth stocks, dividend aristocrats)
- Sector/industry browser with hierarchy

**From Features Specification (Section 1.2 - Asset Details):**

- Comprehensive profile pages per asset
- Company fundamentals (P&L, balance sheet, cash flow)
- Financial statements (quarterly, annual)
- Peer comparison analysis

---

## ✅ CURRENT STATE

**What exists:**
- Basic asset models
- Price data for stocks and crypto
- Simple API for listing assets

**What's missing:**
- Universal search across asset types
- Advanced filtering and screening
- Auto-suggestion and search ranking
- Custom screen builders
- Pre-built screen templates
- Asset comparison tools

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models & Search Index** (2-3 hours)

**Create `apps/backend/src/investments/models/search.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from .asset import Asset

User = get_user_model()

class SavedSearch(models.Model):
    """User's saved searches and screeners"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    
    # Search definition
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Search parameters (JSON)
    search_query = models.CharField(max_length=200, blank=True)  # Text search
    filters = models.JSONField(default=dict)  # {asset_type: [], sector: [], market_cap_min: ..., ...}
    sort_by = models.CharField(max_length=50, default='market_cap')  # market_cap, volume, dividend_yield, etc.
    sort_order = models.CharField(max_length=10, default='desc')  # asc, desc
    
    # Results settings
    is_default = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    use_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-is_default', '-use_count', '-last_used_at']
        indexes = [
            models.Index(fields=['user', '-use_count']),
            models.Index(fields=['user', '-last_used_at']),
        ]

class SearchHistory(models.Model):
    """User's search history for suggestions and analytics"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    
    # Search query
    query = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, null=True)  # stock, crypto, etc.
    
    # Results
    results_count = models.IntegerField()
    clicked_asset_id = models.IntegerField(null=True, blank=True)  # Which result they clicked
    
    # Timestamp
    searched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-searched_at']),
            models.Index(fields=['user', 'query']),
        ]

class ScreenTemplate(models.Model):
    """Pre-built screen templates for common use cases"""
    
    CATEGORY_CHOICES = [
        ('value', 'Value Investing'),
        ('growth', 'Growth Investing'),
        ('dividend', 'Dividend Stocks'),
        ('momentum', 'Momentum Trading'),
        ('quality', 'Quality Companies'),
        ('small_cap', 'Small Cap Opportunities'),
        ('etf', 'ETF Screener'),
        ('crypto', 'Crypto Screener'),
    ]
    
    # Template definition
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    
    # Filters (JSON) - pre-configured filter criteria
    filters = models.JSONField(default=dict)
    
    # Default sorting
    default_sort_by = models.CharField(max_length=50)
    default_sort_order = models.CharField(max_length=10)
    
    # Metadata
    is_featured = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-use_count', 'name']

class AssetComparison(models.Model):
    """Asset comparison lists"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asset_comparisons')
    
    # Comparison list
    name = models.CharField(max_length=200)
    assets = models.JSONField(default=list)  # [asset_id1, asset_id2, ...]
    
    # Comparison metrics to display
    metrics = models.JSONField(default=list)  # ['market_cap', 'pe_ratio', 'dividend_yield', ...]
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']

class SearchSuggestionLog(models.Model):
    """Track which suggestions are clicked to improve ranking"""
    
    query = models.CharField(max_length=200)
    suggestion = models.CharField(max_length=200)
    asset_id = models.IntegerField()
    clicked = models.BooleanField(default=True)
    position = models.IntegerField()  # Position in suggestions list (0, 1, 2, ...)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['query', '-created_at']),
        ]
```

---

### **Phase 2: Search Service** (5-6 hours)

**Create `apps/backend/src/investments/services/search_service.py`:**

```python
from typing import List, Dict, Optional, Tuple
from django.db.models import Q, Count, Case, When, IntegerField, F, FloatField
from django.db.models.functions import Cast
from django.utils import timezone
from investments.models.asset import Asset
from investments.models.search import SavedSearch, SearchHistory, ScreenTemplate, AssetComparison, SearchSuggestionLog
from investments.models.price import AssetPricesCurrent
import re

class UniversalSearchService:
    
    def __init__(self):
        # Relevance weights for search ranking
        self.weights = {
            'symbol_exact_match': 100,
            'symbol_starts_with': 80,
            'name_starts_with': 60,
            'name_contains': 40,
            'sector_match': 20,
            'popular_asset': 10,
        }
    
    def universal_search(
        self,
        query: str,
        asset_types: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        """
        Universal search across all asset types
        
        Returns: {results, total_count, suggestions}
        """
        if not query or len(query.strip()) < 1:
            return {'results': [], 'total_count': 0, 'suggestions': []}
        
        query = query.strip()
        
        # Build search query
        assets_qs = Asset.objects.all()
        
        if asset_types:
            assets_qs = assets_qs.filter(asset_type__in=asset_types)
        
        # Calculate relevance score for each asset
        assets_qs = self._annotate_relevance(assets_qs, query)
        
        # Get total count before pagination
        total_count = assets_qs.count()
        
        # Apply pagination and ordering
        results = assets_qs.order_by('-relevance')[offset:offset + limit]
        
        # Format results
        formatted_results = [self._format_search_result(asset) for asset in results]
        
        # Generate suggestions if no results
        suggestions = []
        if len(formatted_results) < 5:
            suggestions = self._generate_suggestions(query, asset_types)
        
        # Log search
        self._log_search(query, len(formatted_results))
        
        return {
            'results': formatted_results,
            'total_count': total_count,
            'suggestions': suggestions
        }
    
    def _annotate_relevance(self, queryset, query: str):
        """Annotate queryset with relevance score"""
        query_lower = query.lower()
        
        # Exact symbol match
        exact_symbol = When(
            Q(symbol__iexact=query_lower),
            then=self.weights['symbol_exact_match']
        )
        
        # Symbol starts with
        symbol_starts = When(
            Q(symbol__istartswith=query_lower),
            then=self.weights['symbol_starts_with']
        )
        
        # Name starts with
        name_starts = When(
            Q(name__istartswith=query_lower),
            then=self.weights['name_starts_with']
        )
        
        # Name contains
        name_contains = When(
            Q(name__icontains=query_lower),
            then=self.weights['name_contains']
        )
        
        # Default relevance
        default = self.weights.get('popular_asset', 0)
        
        return queryset.annotate(
            relevance=Case(
                exact_symbol,
                symbol_starts,
                name_starts,
                name_contains,
                default=default,
                output_field=IntegerField()
            )
        )
    
    def _format_search_result(self, asset: Asset) -> Dict:
        """Format asset for search results"""
        # Get current price if available
        current_price = None
        change_pct = None
        try:
            price_data = AssetPricesCurrent.objects.filter(asset=asset).first()
            if price_data:
                current_price = float(price_data.price)
                change_pct = float(price_data.change_percent_24h) if price_data.change_percent_24h else None
        except:
            pass
        
        return {
            'id': asset.id,
            'symbol': asset.symbol,
            'name': asset.name,
            'asset_type': asset.asset_type,
            'exchange': asset.exchange,
            'sector': asset.sector,
            'industry': asset.industry,
            'market_cap': float(asset.market_cap) if asset.market_cap else None,
            'current_price': current_price,
            'change_percent_24h': change_pct,
            'logo_url': asset.logo_url,
            'is_tradable': asset.is_tradable
        }
    
    def _generate_suggestions(self, query: str, asset_types: Optional[List[str]] = None) -> List[str]:
        """Generate search suggestions based on query"""
        suggestions = []
        query_lower = query.lower()
        
        # Try to find symbols that start with query
        symbol_matches = Asset.objects.filter(
            symbol__istartswith=query_lower
        )
        if asset_types:
            symbol_matches = symbol_matches.filter(asset_type__in=asset_types)
        
        symbol_matches = symbol_matches.values_list('symbol', flat=True)[:10]
        suggestions.extend([f"{symbol} - Symbol" for symbol in symbol_matches])
        
        # Try to find names that contain query
        name_matches = Asset.objects.filter(
            name__icontains=query_lower
        )
        if asset_types:
            name_matches = name_matches.filter(asset_type__in=asset_types)
        
        name_matches = name_matches.values_list('name', flat=True)[:5]
        suggestions.extend([f"{name} - Company" for name in name_matches])
        
        return suggestions[:10]
    
    def _log_search(self, query: str, results_count: int):
        """Log search for analytics and suggestions improvement"""
        # This would be called asynchronously in production
        # For now, just pass
        pass
    
    def advanced_screen(
        self,
        filters: Dict,
        sort_by: str = 'market_cap',
        sort_order: str = 'desc',
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """
        Advanced screening with multiple filters
        
        filters: {
            asset_type: ['stock', 'etf'],
            sector: ['Technology', 'Healthcare'],
            market_cap_min: 1000000000,  # $1B
            market_cap_max: 10000000000,  # $10B
            pe_ratio_min: 10,
            pe_ratio_max: 30,
            dividend_yield_min: 2.0,
            volume_min: 1000000,
            price_min: 10,
            price_max: 1000,
            country: ['US', 'CA'],
        }
        """
        queryset = Asset.objects.all()
        
        # Apply filters
        if 'asset_type' in filters and filters['asset_type']:
            queryset = queryset.filter(asset_type__in=filters['asset_type'])
        
        if 'sector' in filters and filters['sector']:
            queryset = queryset.filter(sector__in=filters['sector'])
        
        if 'industry' in filters and filters['industry']:
            queryset = queryset.filter(industry__in=filters['industry'])
        
        if 'country' in filters and filters['country']:
            queryset = queryset.filter(country__in=filters['country'])
        
        if 'exchange' in filters and filters['exchange']:
            queryset = queryset.filter(exchange__in=filters['exchange'])
        
        # Market cap filters
        if 'market_cap_min' in filters and filters['market_cap_min']:
            queryset = queryset.filter(market_cap__gte=filters['market_cap_min'])
        
        if 'market_cap_max' in filters and filters['market_cap_max']:
            queryset = queryset.filter(market_cap__lte=filters['market_cap_max'])
        
        # P/E ratio filters
        if 'pe_ratio_min' in filters and filters['pe_ratio_min']:
            queryset = queryset.filter(pe_ratio__gte=filters['pe_ratio_min'])
        
        if 'pe_ratio_max' in filters and filters['pe_ratio_max']:
            queryset = queryset.filter(pe_ratio__lte=filters['pe_ratio_max'])
        
        # P/B ratio filters
        if 'pb_ratio_min' in filters and filters['pb_ratio_min']:
            queryset = queryset.filter(pb_ratio__gte=filters['pb_ratio_min'])
        
        if 'pb_ratio_max' in filters and filters['pb_ratio_max']:
            queryset = queryset.filter(pb_ratio__lte=filters['pb_ratio_max'])
        
        # Dividend yield filters
        if 'dividend_yield_min' in filters and filters['dividend_yield_min']:
            queryset = queryset.filter(dividend_yield__gte=filters['dividend_yield_min'])
        
        if 'dividend_yield_max' in filters and filters['dividend_yield_max']:
            queryset = queryset.filter(dividend_yield__lte=filters['dividend_yield_max'])
        
        # Price filters (need to join with current prices)
        if 'price_min' in filters and filters['price_min'] or \
           'price_max' in filters and filters['price_max']:
            queryset = queryset.filter(
                prices_current__price__isnull=False
            )
            
            if 'price_min' in filters and filters['price_min']:
                queryset = queryset.filter(prices_current__price__gte=filters['price_min'])
            
            if 'price_max' in filters and filters['price_max']:
                queryset = queryset.filter(prices_current__price__lte=filters['price_max'])
        
        # Volume filters
        if 'volume_min' in filters and filters['volume_min']:
            queryset = queryset.filter(
                prices_current__volume_24h__gte=filters['volume_min']
            )
        
        # Only active, tradable assets
        queryset = queryset.filter(
            is_active=True,
            is_tradable=True
        )
        
        # Count total
        total_count = queryset.count()
        
        # Sort
        sort_field = self._get_sort_field(sort_by)
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'
        
        # Apply pagination
        results = queryset.order_by(sort_field)[offset:offset + limit]
        
        # Format results
        formatted_results = []
        for asset in results:
            result = self._format_search_result(asset)
            
            # Add additional screening metrics
            result.update({
                'pe_ratio': float(asset.pe_ratio) if asset.pe_ratio else None,
                'pb_ratio': float(asset.pb_ratio) if asset.pb_ratio else None,
                'dividend_yield': float(asset.dividend_yield) if asset.dividend_yield else None,
                'eps': float(asset.eps) if asset.eps else None,
                'beta': float(asset.beta) if asset.beta else None,
            })
            
            formatted_results.append(result)
        
        return {
            'results': formatted_results,
            'total_count': total_count,
            'filters_applied': filters,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
    
    def _get_sort_field(self, sort_by: str) -> str:
        """Map sort parameter to model field"""
        mapping = {
            'market_cap': 'market_cap',
            'volume': 'prices_current__volume_24h',
            'dividend_yield': 'dividend_yield',
            'pe_ratio': 'pe_ratio',
            'price': 'prices_current__price',
            'change_percent': 'prices_current__change_percent_24h',
            'name': 'name',
            'symbol': 'symbol',
        }
        return mapping.get(sort_by, 'market_cap')
    
    def save_search(
        self,
        user_id: int,
        name: str,
        search_query: str,
        filters: Dict,
        sort_by: str = 'market_cap',
        sort_order: str = 'desc'
    ) -> Dict:
        """Save user's search/screen"""
        saved_search = SavedSearch.objects.create(
            user_id=user_id,
            name=name,
            search_query=search_query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            'id': saved_search.id,
            'name': saved_search.name,
            'created_at': saved_search.created_at
        }
    
    def get_saved_searches(self, user_id: int) -> List[Dict]:
        """Get user's saved searches"""
        searches = SavedSearch.objects.filter(user_id=user_id)
        
        return [
            {
                'id': s.id,
                'name': s.name,
                'description': s.description,
                'filters': s.filters,
                'is_default': s.is_default,
                'use_count': s.use_count,
                'last_used_at': s.last_used_at
            }
            for s in searches
        ]
    
    def get_screen_templates(self, category: Optional[str] = None) -> List[Dict]:
        """Get available screen templates"""
        queryset = ScreenTemplate.objects.all()
        
        if category:
            queryset = queryset.filter(category=category)
        
        templates = queryset.order_by('-is_featured', '-use_count')
        
        return [
            {
                'id': t.id,
                'name': t.name,
                'category': t.category,
                'description': t.description,
                'filters': t.filters,
                'default_sort_by': t.default_sort_by,
                'default_sort_order': t.default_sort_order,
                'is_featured': t.is_featured
            }
            for t in templates
        ]
    
    def create_comparison(
        self,
        user_id: int,
        name: str,
        asset_ids: List[int],
        metrics: Optional[List[str]] = None
    ) -> Dict:
        """Create asset comparison list"""
        if metrics is None:
            metrics = [
                'market_cap', 'pe_ratio', 'pb_ratio', 'dividend_yield',
                'eps', 'beta', 'current_price', 'change_percent_24h'
            ]
        
        comparison = AssetComparison.objects.create(
            user_id=user_id,
            name=name,
            assets=asset_ids,
            metrics=metrics
        )
        
        return {
            'id': comparison.id,
            'name': comparison.name
        }
    
    def get_comparison_details(self, comparison_id: int, user_id: int) -> Dict:
        """Get detailed comparison data"""
        comparison = AssetComparison.objects.get(id=comparison_id, user_id=user_id)
        
        assets = Asset.objects.filter(id__in=comparison['assets'])
        
        comparison_data = {
            'name': comparison.name,
            'assets': [],
            'metrics': comparison.metrics
        }
        
        for asset in assets:
            asset_data = {
                'id': asset.id,
                'symbol': asset.symbol,
                'name': asset.name,
                'logo_url': asset.logo_url,
                'data': {}
            }
            
            # Get requested metrics
            for metric in comparison.metrics:
                if metric == 'market_cap':
                    asset_data['data']['market_cap'] = float(asset.market_cap) if asset.market_cap else None
                elif metric == 'pe_ratio':
                    asset_data['data']['pe_ratio'] = float(asset.pe_ratio) if asset.pe_ratio else None
                elif metric == 'pb_ratio':
                    asset_data['data']['pb_ratio'] = float(asset.pb_ratio) if asset.pb_ratio else None
                elif metric == 'dividend_yield':
                    asset_data['data']['dividend_yield'] = float(asset.dividend_yield) if asset.dividend_yield else None
                elif metric == 'eps':
                    asset_data['data']['eps'] = float(asset.eps) if asset.eps else None
                elif metric == 'beta':
                    asset_data['data']['beta'] = float(asset.beta) if asset.beta else None
                elif metric == 'current_price':
                    try:
                        price = AssetPricesCurrent.objects.filter(asset=asset).first()
                        asset_data['data']['current_price'] = float(price.price) if price else None
                    except:
                        asset_data['data']['current_price'] = None
                elif metric == 'change_percent_24h':
                    try:
                        price = AssetPricesCurrent.objects.filter(asset=asset).first()
                        asset_data['data']['change_percent_24h'] = float(price.change_percent_24h) if price and price.change_percent_24h else None
                    except:
                        asset_data['data']['change_percent_24h'] = None
            
            comparison_data['assets'].append(asset_data)
        
        return comparison_data
    
    def get_available_filters(self) -> Dict:
        """Get available filters and their options"""
        from django.db.models import Count
        
        sectors = Asset.objects.values_list('sector', flat=True).distinct().exclude(
            sector__isnull=True
        ).order_by('sector')
        
        industries = Asset.objects.values_list('industry', flat=True).distinct().exclude(
            industry__isnull=True
        ).order_by('industry')
        
        countries = Asset.objects.values_list('country', flat=True).distinct().exclude(
            country__isnull=True
        ).order_by('country')
        
        exchanges = Asset.objects.values_list('exchange', flat=True).distinct().exclude(
            exchange__isnull=True
        ).order_by('exchange')
        
        return {
            'asset_types': ['stock', 'crypto', 'etf', 'forex', 'commodity', 'bond', 'index'],
            'sectors': list(sectors),
            'industries': list(industries),
            'countries': list(countries),
            'exchanges': list(exchanges),
            'market_cap_ranges': [
                {'label': 'Mega Cap', 'min': 200000000000, 'max': None},
                {'label': 'Large Cap', 'min': 10000000000, 'max': 200000000000},
                {'label': 'Mid Cap', 'min': 2000000000, 'max': 10000000000},
                {'label': 'Small Cap', 'min': 300000000, 'max': 2000000000},
                {'label': 'Micro Cap', 'min': 50000000, 'max': 300000000},
                {'label': 'Nano Cap', 'min': None, 'max': 50000000},
            ],
            'sort_options': [
                {'value': 'market_cap', 'label': 'Market Cap'},
                {'value': 'volume', 'label': 'Volume'},
                {'value': 'dividend_yield', 'label': 'Dividend Yield'},
                {'value': 'pe_ratio', 'label': 'P/E Ratio'},
                {'value': 'price', 'label': 'Price'},
                {'value': 'change_percent', 'label': '% Change'},
            ]
        }
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/search.py`:**

```python
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from investments.services.search_service import UniversalSearchService
from investments.models.search import SavedSearch, AssetComparison, ScreenTemplate

router = Router(tags=['search'])
search_service = UniversalSearchService()

@router.get("/search/universal")
def universal_search(
    request,
    query: str,
    asset_types: str = None,  # Comma-separated: "stock,crypto"
    limit: int = 20,
    offset: int = 0
):
    """Universal search across all asset types"""
    asset_type_list = asset_types.split(',') if asset_types else None
    
    result = search_service.universal_search(
        query=query,
        asset_types=asset_type_list,
        limit=limit,
        offset=offset
    )
    
    return result

@router.post("/search/screen")
def advanced_screen(request, data: dict):
    """Advanced screening with multiple filters"""
    sort_by = data.get('sort_by', 'market_cap')
    sort_order = data.get('sort_order', 'desc')
    limit = data.get('limit', 50)
    offset = data.get('offset', 0)
    filters = data.get('filters', {})
    
    result = search_service.advanced_screen(
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    
    return result

@router.get("/search/filters")
def get_available_filters(request):
    """Get available filters and options"""
    return search_service.get_available_filters()

@router.get("/search/templates")
def get_screen_templates(request, category: str = None):
    """Get available screen templates"""
    return search_service.get_screen_templates(category=category)

@router.post("/search/save")
def save_search(request, data: dict):
    """Save user's search/screen"""
    saved = search_service.save_search(
        user_id=request.auth.id,
        name=data['name'],
        search_query=data.get('search_query', ''),
        filters=data.get('filters', {}),
        sort_by=data.get('sort_by', 'market_cap'),
        sort_order=data.get('sort_order', 'desc')
    )
    
    return saved

@router.get("/search/saved")
def get_saved_searches(request):
    """Get user's saved searches"""
    return search_service.get_saved_searches(user_id=request.auth.id)

@router.delete("/search/saved/{search_id}")
def delete_saved_search(request, search_id: int):
    """Delete saved search"""
    search = get_object_or_404(SavedSearch, id=search_id, user=request.auth)
    search.delete()
    return {"status": "deleted"}

@router.post("/search/comparison")
def create_comparison(request, data: dict):
    """Create asset comparison"""
    comparison = search_service.create_comparison(
        user_id=request.auth.id,
        name=data['name'],
        asset_ids=data['asset_ids'],
        metrics=data.get('metrics')
    )
    
    return comparison

@router.get("/search/comparison/{comparison_id}")
def get_comparison(request, comparison_id: int):
    """Get comparison details"""
    return search_service.get_comparison_details(
        comparison_id=comparison_id,
        user_id=request.auth.id
    )

@router.get("/search/comparisons")
def list_comparisons(request):
    """List user's comparisons"""
    comparisons = AssetComparison.objects.filter(user=request.auth)
    
    return [
        {
            'id': c.id,
            'name': c.name,
            'asset_count': len(c.assets),
            'updated_at': c.updated_at
        }
        for c in comparisons
    ]
```

---

### **Phase 4: Seed Screen Templates** (1-2 hours)

**Create `apps/backend/src/investments/data/screen_templates.py`:**

```python
from investments.models.search import ScreenTemplate

def seed_screen_templates():
    """Seed pre-built screen templates"""
    
    templates = [
        {
            'name': 'Dividend Aristocrats',
            'category': 'dividend',
            'description': 'Companies with 25+ years of consecutive dividend increases',
            'filters': {
                'asset_type': ['stock'],
                'dividend_yield_min': 2.0,
                'market_cap_min': 1000000000,  # $1B+
            },
            'default_sort_by': 'dividend_yield',
            'default_sort_order': 'desc',
            'is_featured': True
        },
        {
            'name': 'Value Stocks',
            'category': 'value',
            'description': 'Undervalued stocks with low P/E and P/B ratios',
            'filters': {
                'asset_type': ['stock'],
                'pe_ratio_max': 15,
                'pb_ratio_max': 3.0,
                'market_cap_min': 1000000000,
            },
            'default_sort_by': 'pe_ratio',
            'default_sort_order': 'asc',
            'is_featured': True
        },
        {
            'name': 'Growth Stocks',
            'category': 'growth',
            'description': 'High-growth companies with strong momentum',
            'filters': {
                'asset_type': ['stock'],
                'market_cap_min': 500000000,  # $500M+
            },
            'default_sort_by': 'change_percent',
            'default_sort_order': 'desc',
            'is_featured': True
        },
        {
            'name': 'Large Cap Tech',
            'category': 'growth',
            'description': 'Large cap technology companies',
            'filters': {
                'asset_type': ['stock'],
                'sector': ['Technology'],
                'market_cap_min': 10000000000,  # $10B+
            },
            'default_sort_by': 'market_cap',
            'default_sort_order': 'desc',
            'is_featured': False
        },
        {
            'name': 'Small Cap Opportunities',
            'category': 'small_cap',
            'description': 'Small cap stocks with growth potential',
            'filters': {
                'asset_type': ['stock'],
                'market_cap_min': 50000000,  # $50M
                'market_cap_max': 2000000000,  # $2B
            },
            'default_sort_by': 'volume',
            'default_sort_order': 'desc',
            'is_featured': False
        },
        {
            'name': 'Momentum Traders',
            'category': 'momentum',
            'description': 'Stocks with strong upward momentum',
            'filters': {
                'asset_type': ['stock'],
                'volume_min': 1000000,
                'market_cap_min': 500000000,
            },
            'default_sort_by': 'change_percent',
            'default_sort_order': 'desc',
            'is_featured': False
        },
        {
            'name': 'ETF Screener',
            'category': 'etf',
            'description': 'Browse ETFs by category',
            'filters': {
                'asset_type': ['etf'],
                'market_cap_min': 100000000,  # $100M AUM
            },
            'default_sort_by': 'volume',
            'default_sort_order': 'desc',
            'is_featured': True
        },
        {
            'name': 'Top Cryptocurrencies',
            'category': 'crypto',
            'description': 'Largest cryptocurrencies by market cap',
            'filters': {
                'asset_type': ['crypto'],
                'market_cap_min': 100000000,  # $100M+
            },
            'default_sort_by': 'market_cap',
            'default_sort_order': 'desc',
            'is_featured': True
        },
    ]
    
    for template_data in templates:
        ScreenTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )

# Run this via management command or migration
```

---

## 📋 DELIVERABLES

- [ ] SavedSearch, SearchHistory, ScreenTemplate, AssetComparison models
- [ ] UniversalSearchService with 4 methods
- [ ] Relevance-based search ranking
- [ ] Advanced screening with 15+ filters
- [ ] 8 API endpoints
- [ ] 8 pre-built screen templates
- [ ] Asset comparison functionality
- [ ] Database migrations
- [ ] Unit tests

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Universal search returns relevant results for symbols and names
- [ ] Search relevance ranking works correctly
- [ ] Advanced screening supports all major filters
- [ ] Screen templates load and apply filters correctly
- [ ] Saved searches can be created and retrieved
- [ ] Asset comparison shows side-by-side metrics
- [ ] API response time <500ms for search
- [ ] Suggestions generated when no results found
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Search latency <300ms for top 20 results
- Screening queries <1 second
- Search relevance precision >85%
- Support for 10,000+ assets
- Template usage tracking working

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/027-universal-asset-search.md
