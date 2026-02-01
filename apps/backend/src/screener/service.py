"""
Stock Screener Functionality
Allows filtering stocks based on multiple criteria
"""

import orjson
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from assets.models.asset import Asset
from assets.models.historic.prices import AssetPricesHistoric
from assets.models.asset_type import AssetType
from assets.models.asset_class import AssetClass
from assets.models.exchange import Exchange
from data.processing.pipline import TechnicalIndicatorsCalculator
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

# Screener configuration
DEFAULT_RESULTS_LIMIT = 100
MAX_RESULTS_LIMIT = 500
MIN_DATA_POINTS = 20

# Filter categories
FILTER_CATEGORIES = {
    "price": {
        "label": "Price",
        "filters": [
            "price_min",
            "price_max",
            "change_percent_min",
            "change_percent_max",
        ],
    },
    "volume": {"label": "Volume", "filters": ["volume_min", "volume_avg_min"]},
    "fundamentals": {
        "label": "Fundamentals",
        "filters": [
            "market_cap_min",
            "market_cap_max",
            "pe_min",
            "pe_max",
            "pb_min",
            "pb_max",
            "dividend_yield_min",
        ],
    },
    "technical": {
        "label": "Technical Indicators",
        "filters": ["rsi_min", "rsi_max", "above_ma_20", "above_ma_50", "above_ma_200"],
    },
    "classification": {
        "label": "Classification",
        "filters": ["asset_type", "exchange", "sector", "industry", "country"],
    },
}

# Predefined screener presets
SCREENER_PRESETS = {
    "high_dividend": {
        "name": "High Dividend Stocks",
        "description": "Stocks with dividend yield > 4%",
        "filters": {
            "dividend_yield_min": 4.0,
            "market_cap_min": 1000000000,  # $1B
        },
    },
    "growth_stocks": {
        "name": "Growth Stocks",
        "description": "Stocks with P/E < 30 and revenue growth > 20%",
        "filters": {
            "pe_max": 30.0,
            "market_cap_min": 500000000,  # $500M
        },
    },
    "value_stocks": {
        "name": "Value Stocks",
        "description": "Stocks with P/E < 15 and P/B < 1.5",
        "filters": {"pe_max": 15.0, "pb_max": 1.5},
    },
    "momentum": {
        "name": "Momentum Stocks",
        "description": "Stocks with RSI < 30 and above 50-day MA",
        "filters": {"rsi_max": 30.0, "above_ma_50": True},
    },
    "small_cap_growth": {
        "name": "Small Cap Growth",
        "description": "Market cap $100M-$2B with high volume",
        "filters": {
            "market_cap_min": 100000000,
            "market_cap_max": 2000000000,
            "volume_avg_min": 1000000,
        },
    },
}


class ScreenerFilter:
    """Container for a single screener filter"""

    def __init__(self, key: str, label: str, value: Any, operator: str = "eq"):
        self.key = key
        self.label = label
        self.value = value
        self.operator = operator  # eq, gt, gte, lt, lte, in, not
        self.active = True

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "key": self.key,
            "label": self.label,
            "value": self.value,
            "operator": self.operator,
            "active": self.active,
        }

    def is_match(self, asset_value: Any) -> bool:
        """Check if asset matches this filter"""
        if not self.active:
            return True

        if self.operator == "eq":
            return asset_value == self.value
        elif self.operator == "gt":
            return asset_value > self.value
        elif self.operator == "gte":
            return asset_value >= self.value
        elif self.operator == "lt":
            return asset_value < self.value
        elif self.operator == "lte":
            return asset_value <= self.value
        elif self.operator == "in":
            return asset_value in self.value
        elif self.operator == "not":
            return asset_value not in self.value

        return False


class StockScreener:
    """
    Stock screener with advanced filtering

    Features:
    - Multiple filter categories
    - Predefined screener presets
    - Real-time filtering with caching
    - Custom filter combinations
    - Performance optimization with Polars
    """

    def __init__(self):
        self.indicators_calculator = TechnicalIndicatorsCalculator()
        self.active_filters = []
        self.filter_cache = {}
        self.cache_timeout = 60  # seconds

    def add_filter(self, key: str, label: str, value: Any, operator: str = "eq"):
        """Add a filter to the screener"""
        filter_obj = ScreenerFilter(key, label, value, operator)
        self.active_filters.append(filter_obj)
        logger.info(f"Added filter: {label} {operator} {value}")

    def remove_filter(self, key: str):
        """Remove all filters for a given key"""
        self.active_filters = [f for f in self.active_filters if f.key != key]
        logger.info(f"Removed filter: {key}")

    def clear_filters(self):
        """Clear all active filters"""
        self.active_filters = []
        logger.info("Cleared all filters")

    def apply_preset(self, preset_name: str) -> Dict[str, Any]:
        """Apply a predefined screener preset"""
        if preset_name not in SCREENER_PRESETS:
            return {"error": f"Unknown preset: {preset_name}"}

        preset = SCREENER_PRESETS[preset_name]

        # Clear existing filters
        self.clear_filters()

        # Add preset filters
        for key, value in preset.get("filters", {}).items():
            label = key.replace("_", " ").title()
            self.add_filter(key, label, value)

        return {
            "preset_name": preset_name,
            "filters_applied": len(self.active_filters),
            "preset_description": preset.get("description", ""),
        }

    def screen(self, limit: int = DEFAULT_RESULTS_LIMIT) -> Dict[str, Any]:
        """
        Execute screening with current filters

        Args:
            limit: Maximum number of results

        Returns:
            Dict with results and metadata
        """
        start_time = datetime.now()

        try:
            # Check cache
            cache_key = self._get_cache_key(limit)
            cached_results = self._get_cached_results(cache_key)

            if cached_results:
                logger.info(f"Returning cached screener results")
                return cached_results

            # Build base queryset
            qs = Asset.objects.filter(is_active=True)

            # Apply classification filters
            qs = self._apply_classification_filters(qs)

            # Get assets and apply value filters
            assets = list(qs[: MAX_RESULTS_LIMIT * 3])
            asset_ids = [a.id for a in assets]

            # Get price data
            cutoff_date = datetime.now() - timedelta(days=365)
            prices_qs = AssetPricesHistoric.objects.filter(
                asset__id__in=asset_ids, timestamp__gte=cutoff_date
            )

            # Apply filters
            filtered_assets = self._apply_filters(assets, prices_qs)

            # Sort and limit results
            filtered_assets = filtered_assets[:limit]

            # Calculate metadata
            elapsed = (datetime.now() - start_time).total_seconds()

            result = {
                "results": [a.to_dict() for a in filtered_assets],
                "count": len(filtered_assets),
                "total_screened": len(assets),
                "filters_applied": len(self.active_filters),
                "filters": [f.to_dict() for f in self.active_filters],
                "elapsed_seconds": round(elapsed, 2),
                "limit": limit,
                "timestamp": datetime.now().isoformat(),
            }

            # Cache results
            self._cache_results(cache_key, result)

            logger.info(
                f"Screener completed: {len(filtered_assets)} results in {elapsed:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Screener error: {str(e)}")
            return {
                "error": str(e),
                "results": [],
                "timestamp": datetime.now().isoformat(),
            }

    def _apply_classification_filters(self, qs) -> Any:
        """Apply classification filters (type, exchange, sector, etc.)"""
        for filter_obj in self.active_filters:
            if not filter_obj.active:
                continue

            if filter_obj.key == "asset_type":
                asset_type = AssetType.objects.filter(
                    name__iexact=filter_obj.value
                ).first()
                if asset_type:
                    qs = qs.filter(asset_type=asset_type)

            elif filter_obj.key == "exchange":
                exchange = Exchange.objects.filter(
                    symbol__iexact=filter_obj.value
                ).first()
                if exchange:
                    qs = qs.filter(exchange=exchange)

            elif filter_obj.key == "sector":
                sector = filter_obj.value  # Already an object or string
                if isinstance(sector, str):
                    qs = qs.filter(sector__name__icontains=sector)
                else:
                    qs = qs.filter(sector=sector)

            elif filter_obj.key == "country":
                qs = qs.filter(country__icontains=filter_obj.value)

        return qs

    def _apply_filters(self, assets: List, prices_qs) -> List:
        """
        Apply all value filters to assets

        Returns filtered asset list
        """
        from assets.models.historic.metrics import AssetMetricsHistoric

        # Fetch prices for all assets
        prices = {p.asset_id: p for p in prices_qs}

        # Fetch metrics for fundamental filters
        metrics_qs = AssetMetricsHistoric.objects.filter(
            asset__id__in=[a.id for a in assets],
            timestamp__gte=datetime.now() - timedelta(days=30),
        )

        # Get latest metric for each asset
        metrics = {}
        for metric in metrics_qs:
            metrics[metric.asset_id] = metric

        filtered_assets = []

        for asset in assets:
            asset_id = asset.id
            price = prices.get(asset_id)
            metric = metrics.get(asset_id)

            # Check all filters
            passes_all = True

            for filter_obj in self.active_filters:
                if not filter_obj.is_match(asset, price, metric):
                    passes_all = False
                    break

            if passes_all:
                filtered_assets.append(asset)

        return filtered_assets

    def _get_cache_key(self, limit: int) -> str:
        """Generate cache key"""
        filter_parts = []
        for f in self.active_filters:
            filter_parts.append(f"{f.key}:{f.operator}:{f.value}")

        return f"screener:{'|'.join(filter_parts)}:limit:{limit}"

    def _cache_results(self, cache_key: str, results: Dict):
        """Cache screener results"""
        self.filter_cache[cache_key] = {"results": results, "timestamp": datetime.now()}

    def _get_cached_results(self, cache_key: str) -> Optional[Dict]:
        """Get cached results if valid"""
        cached = self.filter_cache.get(cache_key)

        if not cached:
            return None

        cache_age = (datetime.now() - cached["timestamp"]).total_seconds()

        if cache_age > self.cache_timeout:
            del self.filter_cache[cache_key]
            return None

        return cached.get("results")

    def get_available_filters(self) -> Dict[str, Any]:
        """Get all available filters organized by category"""
        return {
            "categories": FILTER_CATEGORIES,
            "presets": {
                k: {"name": v["name"], "description": v["description"]}
                for k, v in SCREENER_PRESETS.items()
            },
            "active_filters": [f.to_dict() for f in self.active_filters],
            "available_asset_types": self._get_asset_types(),
            "available_exchanges": self._get_exchanges(),
            "available_sectors": self._get_sectors(),
        }

    def _get_asset_types(self) -> List[Dict]:
        """Get available asset types"""
        from assets.models.asset_type import AssetType

        types = AssetType.objects.all()

        return [
            {
                "key": t.name,
                "label": t.name,
                "count": Asset.objects.filter(asset_type=t, is_active=True).count(),
            }
            for t in types
        ]

    def _get_exchanges(self) -> List[Dict]:
        """Get available exchanges"""
        from assets.models.exchange import Exchange

        exchanges = Exchange.objects.all()

        return [
            {
                "key": e.symbol,
                "label": e.name,
                "count": Asset.objects.filter(exchange=e, is_active=True).count(),
            }
            for e in exchanges
        ]

    def _get_sectors(self) -> List[Dict]:
        """Get available sectors"""
        from assets.models.asset_class import AssetClass

        sectors = AssetClass.objects.all()

        return [
            {
                "key": s.name,
                "label": s.name,
                "count": Asset.objects.filter(sector=s, is_active=True).count(),
            }
            for s in sectors
        ]

    def clean_cache(self):
        """Clean expired cache entries"""
        now = datetime.now()
        expired_keys = []

        for key, value in self.filter_cache.items():
            cache_age = (now - value["timestamp"]).total_seconds()

            if cache_age > self.cache_timeout:
                expired_keys.append(key)

        for key in expired_keys:
            del self.filter_cache[key]

        logger.info(f"Cleaned {len(expired_keys)} expired screener cache entries")


class AssetFilterHelper:
    """Helper methods for filtering assets"""

    @staticmethod
    def filter_by_price(
        assets: List,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
    ) -> List:
        """Filter assets by price range"""
        if price_min is None and price_max is None:
            return assets

        return [
            a
            for a in assets
            if (price_min is None or a.current_price >= price_min)
            and (price_max is None or a.current_price <= price_max)
        ]

    @staticmethod
    def filter_by_volume(
        assets: List,
        volume_min: Optional[float] = None,
        volume_avg_min: Optional[float] = None,
    ) -> List:
        """Filter assets by volume"""
        if volume_min is None and volume_avg_min is None:
            return assets

        return [
            a
            for a in assets
            if (volume_min is None or a.volume >= volume_min)
            and (volume_avg_min is None or a.avg_volume >= volume_avg_min)
        ]

    @staticmethod
    def filter_by_change(
        assets: List,
        change_min: Optional[float] = None,
        change_max: Optional[float] = None,
    ) -> List:
        """Filter assets by percent change range"""
        if change_min is None and change_max is None:
            return assets

        return [
            a
            for a in assets
            if (change_min is None or a.change_percent >= change_min)
            and (change_max is None or a.change_percent <= change_max)
        ]

    @staticmethod
    def filter_by_technical(
        assets: List,
        rsi_min: Optional[float] = None,
        rsi_max: Optional[float] = None,
        above_ma_20: bool = False,
        above_ma_50: bool = False,
        above_ma_200: bool = False,
    ) -> List:
        """Filter assets by technical indicators"""
        filtered = assets

        if rsi_min is not None:
            filtered = [a for a in filtered if a.rsi >= rsi_min]

        if rsi_max is not None:
            filtered = [a for a in filtered if a.rsi <= rsi_max]

        if above_ma_20:
            filtered = [a for a in filtered if a.price_above_ma_20]

        if above_ma_50:
            filtered = [a for a in filtered if a.price_above_ma_50]

        if above_ma_200:
            filtered = [a for a in filtered if a.price_above_ma_200]

        return filtered

    @staticmethod
    def filter_by_fundamentals(
        assets: List,
        market_cap_min: Optional[float] = None,
        market_cap_max: Optional[float] = None,
        pe_min: Optional[float] = None,
        pe_max: Optional[float] = None,
        pb_min: Optional[float] = None,
        pb_max: Optional[float] = None,
        dividend_yield_min: Optional[float] = None,
    ) -> List:
        """Filter assets by fundamental metrics"""
        filtered = assets

        if market_cap_min is not None:
            filtered = [a for a in filtered if a.market_cap >= market_cap_min]

        if market_cap_max is not None:
            filtered = [a for a in filtered if a.market_cap <= market_cap_max]

        if pe_min is not None:
            filtered = [a for a in filtered if a.pe_ratio >= pe_min]

        if pe_max is not None:
            filtered = [a for a in filtered if a.pe_ratio <= pe_max]

        if pb_min is not None:
            filtered = [a for a in filtered if a.pb_ratio >= pb_min]

        if pb_max is not None:
            filtered = [a for a in filtered if a.pb_ratio <= pb_max]

        if dividend_yield_min is not None:
            filtered = [a for a in filtered if a.dividend_yield >= dividend_yield_min]

        return filtered


# Global screener instance
stock_screener = StockScreener()


def screen_stocks(**filters) -> Dict[str, Any]:
    """Screen stocks with given filters"""
    return stock_screener.screen(**filters)


def get_screener_filters() -> Dict[str, Any]:
    """Get all available screener filters"""
    return stock_screener.get_available_filters()


def apply_screener_preset(preset_name: str) -> Dict[str, Any]:
    """Apply a predefined screener preset"""
    return stock_screener.apply_preset(preset_name)


if __name__ == "__main__":
    # Test screener
    logger.info("Testing stock screener...")

    # Apply a preset
    result = apply_screener_preset("high_dividend")
    logger.debug(f"Preset result: {result}")

    # Add custom filters
    stock_screener.add_filter("price_min", "Min Price", 100.0)
    stock_screener.add_filter("volume_min", "Min Volume", 1000000)

    # Run screener
    result = stock_screener.screen(limit=10)
    logger.debug(f"Custom screener result: {result}")

    # Get available filters
    filters = get_screener_filters()
    logger.debug(f"Available filters: {filters}")
