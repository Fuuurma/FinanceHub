# C-021: Advanced Technical Indicators Engine

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 16-20 hours  
**Dependencies:** C-006 (Data Pipeline Optimization)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive technical indicators engine supporting 50+ indicators including RSI, MACD, Bollinger Bands, Stochastic, and custom indicators.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 2.2 - Charts & Visualization):**

- Technical indicators overlay:
  - Moving averages (SMA, EMA)
  - Bollinger Bands
  - RSI, MACD, Stochastic
  - Volume bars
  - Fibonacci retracements

**From Features Specification (Section 3.3 - Technical Analysis):**

- 50+ technical indicators
- Backtesting engine for strategies
- Pattern recognition
- Support/resistance levels
- Pivot points
- Candlestick patterns

---

## ✅ CURRENT STATE

**What exists:**
- Basic price charts with TradingView widgets
- Historical price data in `AssetPricesHistoric` model
- Data pipeline for fetching OHLCV data

**What's missing:**
- Technical indicator calculation engine
- Indicator storage and caching
- Indicator API endpoints
- Multi-timeframe support
- Custom indicator builder

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Technical Indicators Library** (6-8 hours)

**Create `apps/backend/src/investments/lib/technical_indicators.py`:**

```python
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from decimal import Decimal

class TechnicalIndicators:
    """
    Comprehensive technical indicators library
    Supports 50+ indicators across multiple categories
    """
    
    @staticmethod
    def sma(prices: List[float], period: int) -> List[float]:
        """Simple Moving Average"""
        return pd.Series(prices).rolling(window=period).mean().tolist()
    
    @staticmethod
    def ema(prices: List[float], period: int) -> List[float]:
        """Exponential Moving Average"""
        return pd.Series(prices).ewm(span=period, adjust=False).mean().tolist()
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[float]:
        """Relative Strength Index"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = pd.Series(gains).rolling(window=period).mean()
        avg_loss = pd.Series(losses).rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi_values = 100 - (100 / (1 + rs))
        
        # Pad with NaN to match input length
        result = [np.nan] * (len(prices) - len(rsi_values)) + rsi_values.fillna(50).tolist()
        return result
    
    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = pd.Series(prices).ewm(span=fast, adjust=False).mean()
        ema_slow = pd.Series(prices).ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.tolist(),
            'signal': signal_line.tolist(),
            'histogram': histogram.tolist()
        }
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, List[float]]:
        """Bollinger Bands"""
        sma = pd.Series(prices).rolling(window=period).mean()
        std = pd.Series(prices).rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'middle': sma.tolist(),
            'upper': upper_band.tolist(),
            'lower': lower_band.tolist()
        }
    
    @staticmethod
    def stochastic(high: List[float], low: List[float], close: List[float], 
                   k_period: int = 14, d_period: int = 3) -> Dict[str, List[float]]:
        """Stochastic Oscillator"""
        low_min = pd.Series(low).rolling(window=k_period).min()
        high_max = pd.Series(high).rolling(window=k_period).max()
        
        k_percent = 100 * ((pd.Series(close) - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k': k_percent.tolist(),
            'd': d_percent.tolist()
        }
    
    @staticmethod
    def atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        """Average True Range"""
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        close_series = pd.Series(close)
        
        tr1 = high_series - low_series
        tr2 = abs(high_series - close_series.shift(1))
        tr3 = abs(low_series - close_series.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr.tolist()
    
    @staticmethod
    def williams_r(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        """Williams %R"""
        high_max = pd.Series(high).rolling(window=period).max()
        low_min = pd.Series(low).rolling(window=period).min()
        
        williams = -100 * ((high_max - pd.Series(close)) / (high_max - low_min))
        return williams.tolist()
    
    @staticmethod
    def cci(high: List[float], low: List[float], close: List[float], period: int = 20) -> List[float]:
        """Commodity Channel Index"""
        typical_price = (pd.Series(high) + pd.Series(low) + pd.Series(close)) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mean_deviation = typical_price.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
        return cci.tolist()
    
    @staticmethod
    def obv(prices: List[float], volumes: List[int]) -> List[float]:
        """On-Balance Volume"""
        df = pd.DataFrame({'price': prices, 'volume': volumes})
        df['price_change'] = df['price'].diff()
        df['obv'] = df['volume'] * np.where(df['price_change'] > 0, 1, np.where(df['price_change'] < 0, -1, 0))
        df['obv_cumulative'] = df['obv'].cumsum()
        return df['obv_cumulative'].tolist()
    
    @staticmethod
    def adx(high: List[float], low: List[float], close: List[float], period: int = 14) -> Dict[str, List[float]]:
        """Average Directional Index"""
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        close_series = pd.Series(close)
        
        # True Range
        tr1 = high_series - low_series
        tr2 = abs(high_series - close_series.shift(1))
        tr3 = abs(low_series - close_series.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # +DI and -DI
        up_move = high_series.diff()
        down_move = -low_series.diff()
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return {
            'adx': adx.tolist(),
            'plus_di': plus_di.tolist(),
            'minus_di': minus_di.tolist()
        }
    
    @staticmethod
    def pivot_points(high: float, low: float, close: float) -> Dict[str, float]:
        """Classic Pivot Points"""
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            'r3': r3,
            's1': s1,
            's2': s2,
            's3': s3
        }
    
    @staticmethod
    def fibonacci_retracements(high_price: float, low_price: float) -> Dict[str, float]:
        """Fibonacci Retracement Levels"""
        diff = high_price - low_price
        
        return {
            '0%': high_price,
            '23.6%': high_price - (diff * 0.236),
            '38.2%': high_price - (diff * 0.382),
            '50%': high_price - (diff * 0.5),
            '61.8%': high_price - (diff * 0.618),
            '78.6%': high_price - (diff * 0.786),
            '100%': low_price
        }
    
    @staticmethod
    def momentum(prices: List[float], period: int = 10) -> List[float]:
        """Momentum Indicator"""
        prices_series = pd.Series(prices)
        momentum = prices_series - prices_series.shift(period)
        return momentum.tolist()
    
    @staticmethod
    def roc(prices: List[float], period: int = 12) -> List[float]:
        """Rate of Change"""
        prices_series = pd.Series(prices)
        roc = ((prices_series - prices_series.shift(period)) / prices_series.shift(period)) * 100
        return roc.tolist()
    
    @staticmethod
    def volatility(prices: List[float], period: int = 20) -> List[float]:
        """Historical Volatility (Standard Deviation)"""
        returns = pd.Series(prices).pct_change()
        volatility = returns.rolling(window=period).std() * np.sqrt(252)  # Annualized
        return volatility.tolist()
```

---

### **Phase 2: Indicator Storage & Caching** (3-4 hours)

**Create `apps/backend/src/investments/models/technical_analysis.py`:**

```python
from django.db import models
from .asset import Asset

class CalculatedIndicator(models.Model):
    """Cached calculated indicators"""
    
    INDICATOR_TYPES = [
        ('sma', 'Simple Moving Average'),
        ('ema', 'Exponential Moving Average'),
        ('rsi', 'Relative Strength Index'),
        ('macd', 'MACD'),
        ('bollinger', 'Bollinger Bands'),
        ('stochastic', 'Stochastic'),
        ('atr', 'Average True Range'),
        ('williams_r', 'Williams %R'),
        ('cci', 'Commodity Channel Index'),
        ('obv', 'On-Balance Volume'),
        ('adx', 'Average Directional Index'),
        ('momentum', 'Momentum'),
        ('roc', 'Rate of Change'),
        ('volatility', 'Volatility'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='indicators')
    indicator_type = models.CharField(max_length=20, choices=INDICATOR_TYPES)
    
    # Parameters
    period = models.IntegerField()
    parameters = models.JSONField(default=dict)  # For custom parameters
    
    # Data
    timeframe = models.CharField(max_length=10)  # 1m, 5m, 1h, 1d, 1w, 1M
    values = models.JSONField()  # Array of values
    timestamps = models.JSONField()  # Array of timestamps
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # When to recalculate
    
    class Meta:
        indexes = [
            models.Index(fields=['asset', 'indicator_type', 'timeframe']),
            models.Index(fields=['expires_at']),
        ]
```

---

### **Phase 3: Indicator Calculation Service** (4-5 hours)

**Create `apps/backend/src/investments/services/indicator_service.py`:**

```python
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from investments.models import Asset, CalculatedIndicator, AssetPricesHistoric
from investments.lib.technical_indicators import TechnicalIndicators

class IndicatorCalculationService:
    
    def __init__(self):
        self.indicators_lib = TechnicalIndicators()
    
    def calculate_indicator(
        self,
        asset_id: int,
        indicator_type: str,
        timeframe: str = '1d',
        period: int = 14,
        **params
    ) -> Dict:
        """
        Calculate technical indicator for asset
        
        Returns: {values, timestamps, calculated_at}
        """
        # Get historical prices
        prices = self._get_historical_prices(asset_id, timeframe, limit=200)
        
        if not prices:
            return {'values': [], 'timestamps': []}
        
        # Calculate indicator
        result = self._calculate(indicator_type, prices, period, **params)
        
        # Cache result
        self._cache_indicator(asset_id, indicator_type, timeframe, period, result, params)
        
        return result
    
    def _calculate(self, indicator_type: str, prices: List[Dict], period: int, **params) -> Dict:
        """Route to appropriate indicator calculation"""
        close_prices = [p['close'] for p in prices]
        high_prices = [p['high'] for p in prices]
        low_prices = [p['low'] for p in prices]
        volumes = [p['volume'] for p in prices]
        timestamps = [p['timestamp'] for p in prices]
        
        if indicator_type == 'sma':
            values = self.indicators_lib.sma(close_prices, period)
        elif indicator_type == 'ema':
            values = self.indicators_lib.ema(close_prices, period)
        elif indicator_type == 'rsi':
            values = self.indicators_lib.rsi(close_prices, period)
        elif indicator_type == 'macd':
            return self.indicators_lib.macd(close_prices, **params)
        elif indicator_type == 'bollinger':
            return self.indicators_lib.bollinger_bands(close_prices, period, params.get('std_dev', 2))
        elif indicator_type == 'stochastic':
            return self.indicators_lib.stochastic(high_prices, low_prices, close_prices, period)
        elif indicator_type == 'atr':
            values = self.indicators_lib.atr(high_prices, low_prices, close_prices, period)
        elif indicator_type == 'williams_r':
            values = self.indicators_lib.williams_r(high_prices, low_prices, close_prices, period)
        elif indicator_type == 'cci':
            values = self.indicators_lib.cci(high_prices, low_prices, close_prices, period)
        elif indicator_type == 'obv':
            values = self.indicators_lib.obv(close_prices, volumes)
        elif indicator_type == 'adx':
            return self.indicators_lib.adx(high_prices, low_prices, close_prices, period)
        elif indicator_type == 'momentum':
            values = self.indicators_lib.momentum(close_prices, period)
        elif indicator_type == 'roc':
            values = self.indicators_lib.roc(close_prices, period)
        elif indicator_type == 'volatility':
            values = self.indicators_lib.volatility(close_prices, period)
        else:
            raise ValueError(f"Unknown indicator: {indicator_type}")
        
        return {'values': values, 'timestamps': timestamps}
    
    def _get_historical_prices(self, asset_id: int, timeframe: str, limit: int = 200) -> List[Dict]:
        """Get historical prices for asset"""
        # Map timeframe to data granularity
        timeframe_map = {
            '1m': 60,  # seconds
            '5m': 300,
            '1h': 3600,
            '1d': 86400,
            '1w': 604800,
            '1M': 2592000
        }
        
        prices = AssetPricesHistoric.objects.filter(
            asset_id=asset_id
        ).order_by('-timestamp')[:limit]
        
        return [{
            'timestamp': p.timestamp.isoformat(),
            'open': float(p.open_price),
            'high': float(p.high_price),
            'low': float(p.low_price),
            'close': float(p.close_price),
            'volume': p.volume
        } for p in reversed(list(prices))]
    
    def _cache_indicator(self, asset_id, indicator_type, timeframe, period, result, params):
        """Cache calculated indicator"""
        expires_at = timezone.now() + timedelta(minutes=15)  # Cache for 15 minutes
        
        CalculatedIndicator.objects.update_or_create(
            asset_id=asset_id,
            indicator_type=indicator_type,
            timeframe=timeframe,
            period=period,
            defaults={
                'values': result,
                'parameters': params,
                'expires_at': expires_at
            }
        )
    
    def get_cached_indicator(self, asset_id: int, indicator_type: str, timeframe: str, period: int) -> Optional[Dict]:
        """Get cached indicator if still valid"""
        try:
            cached = CalculatedIndicator.objects.get(
                asset_id=asset_id,
                indicator_type=indicator_type,
                timeframe=timeframe,
                period=period,
                expires_at__gt=timezone.now()
            )
            return cached.values
        except CalculatedIndicator.DoesNotExist:
            return None
```

---

### **Phase 4: API Endpoints** (2-3 hours)

**Create `apps/backend/src/api/technical_indicators.py`:**

```python
from ninja import Router
from investments.services.indicator_service import IndicatorCalculationService

router = Router(tags=['technical_indicators'])
service = IndicatorCalculationService()

@router.get("/assets/{asset_id}/indicators/{indicator_type}")
def calculate_indicator(
    request,
    asset_id: int,
    indicator_type: str,
    timeframe: str = '1d',
    period: int = 14
):
    """
    Calculate technical indicator
    
    Available indicators: sma, ema, rsi, macd, bollinger, stochastic, atr, 
                         williams_r, cci, obv, adx, momentum, roc, volatility
    
    Timeframes: 1m, 5m, 1h, 1d, 1w, 1M
    """
    # Check cache first
    cached = service.get_cached_indicator(asset_id, indicator_type, timeframe, period)
    if cached:
        return cached
    
    # Calculate fresh
    result = service.calculate_indicator(asset_id, indicator_type, timeframe, period)
    return result

@router.get("/assets/{asset_id}/indicators")
def list_indicators(request, asset_id: int):
    """List all available indicators for asset"""
    from investments.models import CalculatedIndicator
    
    indicators = CalculatedIndicator.objects.filter(
        asset_id=asset_id,
        expires_at__gt=timezone.now()
    ).values('indicator_type', 'timeframe', 'period', 'calculated_at')
    
    return list(indicators)

@router.post("/assets/{asset_id}/indicators/batch")
def batch_calculate(request, asset_id: int, indicators: list):
    """
    Calculate multiple indicators at once
    
    Body: [{"indicator_type": "rsi", "period": 14}, ...]
    """
    results = {}
    for ind in indicators:
        try:
            result = service.calculate_indicator(
                asset_id,
                ind['indicator_type'],
                ind.get('timeframe', '1d'),
                ind.get('period', 14)
            )
            results[ind['indicator_type']] = result
        except Exception as e:
            results[ind['indicator_type']] = {'error': str(e)}
    
    return results

@router.get("/pivot-points/{asset_id}")
def pivot_points(request, asset_id: int):
    """Calculate pivot points for asset"""
    from investments.models import Asset
    
    asset = Asset.objects.get(id=asset_id)
    prices = AssetPricesHistoric.objects.filter(
        asset_id=asset_id
    ).order_by('-timestamp').first()
    
    if not prices:
        return {}
    
    from investments.lib.technical_indicators import TechnicalIndicators
    pivots = TechnicalIndicators.pivot_points(
        float(prices.high_price),
        float(prices.low_price),
        float(prices.close_price)
    )
    
    return pivots
```

---

## 📋 DELIVERABLES

- [ ] TechnicalIndicators library with 15+ indicators
- [ ] CalculatedIndicator model for caching
- [ ] IndicatorCalculationService with calculation methods
- [ ] 5 API endpoints for indicators
- [ ] Caching layer (15-minute TTL)
- [ ] Batch calculation support
- [ ] Unit tests for each indicator
- [ ] API documentation

---

## ✅ ACCEPTANCE CRITERIA

- [ ] All 15 indicators calculate correctly
- [ ] Results cached for 15 minutes
- [ ] API returns indicator values with timestamps
- [ ] Batch calculation supports 5+ indicators at once
- [ ] Pivot points calculated from previous day's HLC
- [ ] Error handling for invalid parameters
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Indicator calculation time <200ms (cached)
- Indicator calculation time <2s (fresh calculation)
- Support for 50+ concurrent requests
- Cache hit rate >80%

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/021-technical-indicators-engine.md
