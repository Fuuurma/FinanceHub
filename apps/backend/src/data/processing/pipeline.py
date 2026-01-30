"""
Data Processing Pipeline
Handles data normalization, validation, enrichment, and technical indicators calculation
"""

import orjson
import numpy as np
import polars as pl
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from assets.models.asset import Asset
from assets.models.historic.prices import AssetPricesHistoric
from assets.models.historic.metrics import AssetMetricsHistoric
from utils.helpers.logger.logger import get_logger
from utils.services.circuit_breaker import get_circuit_breaker

logger = get_logger(__name__)


# Constants for technical indicators
MA_PERIODS = [5, 10, 20, 50, 100, 200]
EMA_PERIODS = [12, 26, 50, 200]
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BOLLINGER_PERIOD = 20
BOLLINGER_STD_DEV = 2

# Data quality thresholds
MIN_VOLUME_THRESHOLD = 1000
MAX_PRICE_CHANGE_PERCENT = 50  # Warn if price changes > 50%
MIN_DATA_POINTS = 20  # Minimum data points for technical analysis


@dataclass
class ProcessedAssetData:
    """Container for processed asset data"""

    symbol: str
    source: str
    raw_data: Dict[str, Any]
    normalized_data: Optional[Dict[str, Any]] = None
    enriched_data: Optional[Dict[str, Any]] = None
    technical_indicators: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = None
    is_valid: bool = True
    processed_at: Optional[datetime] = None


class DataProcessor:
    """Base data processor with common functionality"""

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """Normalize symbol to uppercase and remove invalid chars"""
        return symbol.upper().strip().replace("-", ".")

    @staticmethod
    def validate_price_data(price: float) -> bool:
        """Validate price data point"""
        return price > 0 and price < 10000000  # Reasonable range

    @staticmethod
    def validate_volume(volume: float) -> bool:
        """Validate volume data point"""
        return volume >= MIN_VOLUME_THRESHOLD

    @staticmethod
    def validate_timestamp(timestamp: datetime) -> bool:
        """Validate timestamp is recent enough"""
        cutoff = datetime.now() - timedelta(days=10)
        return timestamp >= cutoff

    @staticmethod
    def calculate_change_percent(current: float, previous: float) -> float:
        """Calculate percentage change between two prices"""
        if previous == 0:
            return 0.0
        change = ((current - previous) / previous) * 100
        return round(change, 2)

    @staticmethod
    def detect_anomalies(prices: List[float]) -> List[int]:
        """Detect price anomalies using simple z-score method"""
        if len(prices) < MIN_DATA_POINTS:
            return []

        prices_array = np.array(prices)
        mean = np.mean(prices_array)
        std = np.std(prices_array)

        # Anomalies are more than 3 standard deviations from mean
        threshold = 3
        z_scores = (
            np.abs((prices_array - mean) / std)
            if std > 0
            else np.zeros_like(prices_array)
        )

        return np.where(z_scores > threshold)[0].tolist()


class PriceDataProcessor(DataProcessor):
    """Processor for price data from various sources"""

    def __init__(self):
        self.source_configs = {
            "yahoo": {"price_field": "close", "volume_field": "volume"},
            "alpha": {"price_field": "close", "volume_field": "volume"},
            "binance": {"price_field": "close", "volume_field": "volume"},
            "coingecko": {"price_field": "price", "volume_field": "volume"},
            "coinmarketcap": {"price_field": "close", "volume_field": "volume"},
        }

    def normalize_price_data(
        self, raw_data: Dict[str, Any], source: str
    ) -> Optional[Dict[str, Any]]:
        """Normalize price data from different sources to common format"""
        try:
            config = self.source_configs.get(source)
            if not config:
                logger.warning(f"Unknown source: {source}")
                return None

            normalized = {
                "symbol": self.normalize_symbol(raw_data.get("symbol", "")),
                "source": source,
                "timestamp": self._parse_timestamp(raw_data.get("timestamp")),
                "open": self._parse_float(raw_data.get("open", 0)),
                "high": self._parse_float(raw_data.get("high", 0)),
                "low": self._parse_float(raw_data.get("low", 0)),
                "close": self._parse_float(
                    raw_data.get("close", raw_data.get("price", 0))
                ),
                "volume": self._parse_float(raw_data.get("volume", 0)),
                "raw": raw_data,
            }

            # Validate data
            if not self.validate_price_data(normalized["close"]):
                logger.warning(f"Invalid price data for {normalized['symbol']}")
                return None

            if not self.validate_volume(normalized["volume"]):
                logger.warning(f"Invalid volume data for {normalized['symbol']}")
                return None

            if not self.validate_timestamp(normalized["timestamp"]):
                logger.warning(f"Old timestamp for {normalized['symbol']}")
                return None

            return normalized

        except Exception as e:
            logger.error(f"Error normalizing price data: {str(e)}")
            return None

    def process_historical_data(
        self, raw_data: List[Dict], source: str
    ) -> List[Dict[str, Any]]:
        """Process multiple historical data points"""
        processed = []

        for item in raw_data:
            normalized = self.normalize_price_data(item, source)
            if normalized:
                processed.append(normalized)

        return processed

    def enrich_price_data(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich price data with calculated fields"""
        enriched = price_data.copy()

        # Calculate changes if possible
        if "previous_close" in price_data:
            change = enriched["close"] - price_data["previous_close"]
            enriched["change"] = round(change, 2)
            enriched["change_percent"] = self.calculate_change_percent(
                enriched["close"], price_data["previous_close"]
            )

        # Calculate daily range
        if enriched["high"] > 0 and enriched["low"] > 0:
            enriched["daily_range"] = round(enriched["high"] - enriched["low"], 2)
            enriched["daily_range_percent"] = round(
                (enriched["daily_range"] / enriched["close"]) * 100, 2
            )

        return enriched

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        """Parse timestamp from various formats"""
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except:
                return datetime.now()
        elif isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        return datetime.now()

    @staticmethod
    def _parse_float(value: Any) -> float:
        """Parse float from various formats"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            try:
                return float(value)
            except:
                return 0.0
        return 0.0


class TechnicalIndicatorsCalculator:
    """Calculate technical indicators using Polars for performance"""

    def __init__(self):
        pass

    def calculate_all_indicators(
        self, price_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate all technical indicators for a price series"""
        if len(price_data) < MIN_DATA_POINTS:
            logger.warning(
                f"Not enough data points for technical indicators: {len(price_data)}"
            )
            return {}

        try:
            # Convert to Polars DataFrame for fast computation
            df = pl.DataFrame(price_data)

            indicators = {}

            # Moving Averages
            indicators["ma"] = self._calculate_moving_averages(df)

            # Exponential Moving Averages
            indicators["ema"] = self._calculate_ema(df)

            # RSI
            indicators["rsi"] = self._calculate_rsi(df)

            # MACD
            indicators["macd"] = self._calculate_macd(df)

            # Bollinger Bands
            indicators["bollinger"] = self._calculate_bollinger_bands(df)

            # ATR (Average True Range)
            indicators["atr"] = self._calculate_atr(df)

            # Volume indicators
            indicators["volume_ma"] = self._calculate_volume_ma(df)

            # Support/Resistance levels
            indicators["support_resistance"] = self._calculate_support_resistance(df)

            return indicators

        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}

    def _calculate_moving_averages(self, df: pl.DataFrame) -> Dict[str, List[float]]:
        """Calculate Simple Moving Averages for multiple periods"""
        result = {}
        close_series = df["close"]

        for period in MA_PERIODS:
            if len(df) >= period:
                ma = close_series.rolling_mean(window_size=period)
                result[f"ma_{period}"] = ma.to_list()

        return result

    def _calculate_ema(self, df: pl.DataFrame) -> Dict[str, List[float]]:
        """Calculate Exponential Moving Averages"""
        result = {}
        close_series = df["close"]

        # Polars uses exponential moving average
        for period in EMA_PERIODS:
            if len(df) >= period:
                alpha = 2 / (period + 1)
                ema = self._calculate_ema_series(close_series.to_list(), alpha)
                result[f"ema_{period}"] = ema

        return result

    @staticmethod
    def _calculate_ema_series(prices: List[float], alpha: float) -> List[float]:
        """Calculate EMA series manually"""
        ema = [prices[0]]

        for price in prices[1:]:
            ema.append(alpha * price + (1 - alpha) * ema[-1])

        return ema

    def _calculate_rsi(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Calculate Relative Strength Index"""
        close_series = df["close"].to_list()

        if len(close_series) < RSI_PERIOD + 1:
            return {}

        # Calculate price changes
        gains = []
        losses = []

        for i in range(1, len(close_series)):
            change = close_series[i] - close_series[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        # Calculate average gains and losses
        avg_gain = sum(gains[-RSI_PERIOD:]) / RSI_PERIOD
        avg_loss = sum(losses[-RSI_PERIOD:]) / RSI_PERIOD

        if avg_loss == 0:
            rsi_values = [100] * len(close_series)
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi_values = [rsi] * len(close_series)

        return {
            "rsi": rsi_values[-1],
            "rsi_period": RSI_PERIOD,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            "rsi_status": "overbought"
            if rsi > 70
            else "oversold"
            if rsi < 30
            else "neutral",
        }

    def _calculate_macd(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        close_series = df["close"]

        if len(df) < MACD_SLOW + 1:
            return {}

        # Calculate EMAs
        ema_fast = self._calculate_ema_series(
            close_series.to_list(), 2 / (MACD_FAST + 1)
        )
        ema_slow = self._calculate_ema_series(
            close_series.to_list(), 2 / (MACD_SLOW + 1)
        )

        # MACD line
        macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]

        # Signal line (EMA of MACD)
        signal_line = self._calculate_ema_series(macd_line, 2 / (MACD_SIGNAL + 1))

        # Histogram
        histogram = [m - s for m, s in zip(macd_line, signal_line)]

        return {
            "macd": macd_line[-1] if macd_line else None,
            "signal": signal_line[-1] if signal_line else None,
            "histogram": histogram[-1] if histogram else None,
            "macd_cross": "bullish"
            if histogram[-2] < 0 and histogram[-1] > 0
            else "bearish"
            if histogram[-2] > 0 and histogram[-1] < 0
            else "none",
            "fast_period": MACD_FAST,
            "slow_period": MACD_SLOW,
            "signal_period": MACD_SIGNAL,
        }

    def _calculate_bollinger_bands(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Calculate Bollinger Bands"""
        close_series = df["close"]

        if len(df) < BOLLINGER_PERIOD:
            return {}

        # Calculate middle band (SMA)
        middle_band = close_series.rolling_mean(window_size=BOLLINGER_PERIOD)

        # Calculate standard deviation
        std_dev = close_series.rolling_std(window_size=BOLLINGER_PERIOD)

        # Calculate upper and lower bands
        upper_band = middle_band + (BOLLINGER_STD_DEV * std_dev)
        lower_band = middle_band - (BOLLINGER_STD_DEV * std_dev)

        # Calculate bandwidth and percent B
        bandwidth = (upper_band - lower_band) / middle_band
        percent_b = (close_series - lower_band) / (upper_band - lower_band) * 100

        last_idx = len(df) - 1

        return {
            "upper": upper_band.to_list()[last_idx],
            "middle": middle_band.to_list()[last_idx],
            "lower": lower_band.to_list()[last_idx],
            "bandwidth": bandwidth.to_list()[last_idx],
            "percent_b": percent_b.to_list()[last_idx],
            "period": BOLLINGER_PERIOD,
            "std_dev": BOLLINGER_STD_DEV,
            "squeeze": bandwidth.to_list()[last_idx]
            < 0.02,  # Narrow bands indicate squeeze
            "status": "overbought"
            if percent_b.to_list()[last_idx] > 80
            else "oversold"
            if percent_b.to_list()[last_idx] < 20
            else "neutral",
        }

    def _calculate_atr(self, df: pl.DataFrame) -> Optional[float]:
        """Calculate Average True Range"""
        if len(df) < 15:
            return None

        high = df["high"]
        low = df["low"]
        close = df["close"]

        # Calculate True Range
        tr_list = []
        for i in range(1, len(df)):
            high_low = high[i] - low[i]
            high_close_prev = abs(high[i] - close[i - 1])
            low_close_prev = abs(low[i] - close[i - 1])
            tr = max(high_low, high_close_prev, low_close_prev)
            tr_list.append(tr)

        # Calculate ATR (14-period average)
        atr = sum(tr_list[-14:]) / 14 if len(tr_list) >= 14 else None

        return atr

    def _calculate_volume_ma(self, df: pl.DataFrame) -> Dict[str, List[float]]:
        """Calculate Volume Moving Averages"""
        result = {}
        volume_series = df["volume"]

        for period in [20, 50]:
            if len(df) >= period:
                vol_ma = volume_series.rolling_mean(window_size=period)
                result[f"volume_ma_{period}"] = vol_ma.to_list()

        return result

    def _calculate_support_resistance(
        self, df: pl.DataFrame, lookback: int = 50
    ) -> Dict[str, Any]:
        """Calculate support and resistance using pivot points and volume confirmation"""
        if len(df) < lookback:
            return {}

        recent = df.tail(lookback)

        close_prices = recent["close"].to_list()
        highs = recent["high"].to_list()
        lows = recent["low"].to_list()

        if not close_prices:
            return {}

        pivot_high = max(highs)
        pivot_low = min(lows)
        pivot_point = (pivot_high + pivot_low + close_prices[-1]) / 3

        s1 = 2 * pivot_point - pivot_high
        s2 = pivot_point - (pivot_high - pivot_low)
        s3 = pivot_low - 2 * (pivot_high - pivot_point)

        r1 = 2 * pivot_point - pivot_low
        r2 = pivot_point + (pivot_high - pivot_low)
        r3 = pivot_high + 2 * (pivot_point - pivot_low)

        return {
            "pivot_point": round(pivot_point, 2),
            "pivot_high": round(pivot_high, 2),
            "pivot_low": round(pivot_low, 2),
            "support_levels": [round(s1, 2), round(s2, 2), round(s3, 2)],
            "resistance_levels": [round(r1, 2), round(r2, 2), round(r3, 2)],
            "current_support": round(s1, 2),
            "current_resistance": round(r1, 2),
            "lookback_period": lookback,
        }


class DataPipeline:
    """Orchestrate the complete data pipeline: fetch → process → store"""

    def __init__(self):
        self.price_processor = PriceDataProcessor()
        self.indicators_calculator = TechnicalIndicatorsCalculator()
        self.api_breaker = get_circuit_breaker(
            "data_api", failure_threshold=5, timeout_seconds=60
        )
        self._metrics = {
            "total_processed": 0,
            "total_saved": 0,
            "total_errors": 0,
            "processing_times": [],
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline performance metrics"""
        times = self._metrics["processing_times"]
        return {
            "total_processed": self._metrics["total_processed"],
            "total_saved": self._metrics["total_saved"],
            "total_errors": self._metrics["total_errors"],
            "avg_processing_time_ms": sum(times) / len(times) if times else 0,
            "min_processing_time_ms": min(times) if times else 0,
            "max_processing_time_ms": max(times) if times else 0,
            "success_rate": (
                (self._metrics["total_processed"] - self._metrics["total_errors"])
                / max(self._metrics["total_processed"], 1)
                * 100
            ),
        }

    def _fetch_from_source(self, source: str, symbol: str) -> Dict[str, Any]:
        """Internal fetch method (wrapped by circuit breaker)"""
        from data.fetchers import get_fetcher

        fetcher = get_fetcher(source)
        return fetcher.fetch_symbol_data(symbol)

    def fetch_external_data(self, source: str, symbol: str) -> Dict[str, Any]:
        """Fetch data with circuit breaker protection"""
        return self.api_breaker.call(
            self._fetch_from_source, source=source, symbol=symbol
        )

    def process_raw_data(
        self, raw_data: Dict[str, Any], source: str, asset_type: str = "stock"
    ) -> ProcessedAssetData:
        """Complete pipeline for a single data point"""
        processed = ProcessedAssetData(
            symbol=raw_data.get("symbol", ""),
            source=source,
            raw_data=raw_data,
            validation_errors=[],
            processed_at=datetime.now(),
        )

        try:
            # Step 1: Normalize data
            if asset_type in ["stock", "crypto"]:
                processed.normalized_data = self.price_processor.normalize_price_data(
                    raw_data, source
                )

            # Step 2: Validate data
            if not processed.normalized_data:
                processed.is_valid = False
                processed.validation_errors.append("Normalization failed")
                return processed

            # Step 3: Enrich data
            processed.enriched_data = self.price_processor.enrich_price_data(
                processed.normalized_data
            )

            processed.is_valid = True

        except Exception as e:
            processed.is_valid = False
            processed.validation_errors.append(f"Processing error: {str(e)}")
            logger.error(f"Error processing data for {processed.symbol}: {str(e)}")

        return processed

    def process_with_indicators(
        self, historical_data: List[Dict[str, Any]], source: str
    ) -> Dict[str, Any]:
        """Process historical data and calculate all indicators"""
        try:
            # Process and normalize historical data
            processed_data = self.price_processor.process_historical_data(
                historical_data, source
            )

            if not processed_data:
                return {"error": "No valid data after processing"}

            # Calculate technical indicators
            indicators = self.indicators_calculator.calculate_all_indicators(
                processed_data
            )

            return {
                "processed_data": processed_data,
                "indicators": indicators,
                "count": len(processed_data),
                "source": source,
                "processed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing with indicators: {str(e)}")
            return {"error": str(e)}

    def save_to_database_batch(
        self, processed_data_list: List[ProcessedAssetData]
    ) -> Dict[str, Any]:
        """Save multiple processed data points in batch"""
        if not processed_data_list:
            return {"saved": 0, "skipped": 0}

        valid_data = [
            d for d in processed_data_list if d.is_valid and d.normalized_data
        ]
        if not valid_data:
            return {"saved": 0, "skipped": len(processed_data_list)}

        try:
            asset_prices_map = {}

            for processed in valid_data:
                asset, _ = Asset.objects.get_or_create(
                    symbol__iexact=processed.symbol,
                    defaults={"symbol": processed.symbol, "name": processed.symbol},
                )

                if asset not in asset_prices_map:
                    asset_prices_map[asset] = []

                asset_prices_map[asset].append(
                    AssetPricesHistoric(
                        asset=asset,
                        timestamp=processed.normalized_data["timestamp"],
                        open=processed.normalized_data.get("open", 0),
                        high=processed.normalized_data.get("high", 0),
                        low=processed.normalized_data.get("low", 0),
                        close=processed.normalized_data.get("close", 0),
                        volume=processed.normalized_data.get("volume", 0),
                    )
                )

            total_saved = 0
            total_skipped = 0

            for asset, price_objects in asset_prices_map.items():
                existing_timestamps = set(
                    AssetPricesHistoric.objects.filter(
                        asset=asset, timestamp__in=[p.timestamp for p in price_objects]
                    ).values_list("timestamp", flat=True)
                )

                new_prices = [
                    p for p in price_objects if p.timestamp not in existing_timestamps
                ]

                if new_prices:
                    AssetPricesHistoric.objects.bulk_create(new_prices, batch_size=500)
                    total_saved += len(new_prices)
                    total_skipped += len(price_objects) - len(new_prices)

            logger.info(
                f"Batch save: {total_saved} saved, {total_skipped} skipped (duplicates)"
            )

            return {
                "saved": total_saved,
                "skipped": total_skipped,
                "total": len(valid_data),
            }

        except Exception as e:
            logger.error(f"Batch save failed: {str(e)}")
            raise

    def save_to_database(self, processed_data: ProcessedAssetData) -> bool:
        """Save processed data to database"""
        if not processed_data.is_valid or not processed_data.normalized_data:
            logger.warning(f"Skipping invalid data for {processed_data.symbol}")
            return False

        try:
            # Get or create asset
            asset, _ = Asset.objects.get_or_create(
                symbol__iexact=processed_data.symbol,
                defaults={
                    "symbol": processed_data.symbol,
                    "name": processed_data.raw_data.get("name", processed_data.symbol),
                },
            )

            # Save price data
            if processed_data.normalized_data:
                AssetPricesHistoric.objects.create(
                    asset=asset,
                    timestamp=processed_data.normalized_data["timestamp"],
                    open=processed_data.normalized_data.get("open", 0),
                    high=processed_data.normalized_data.get("high", 0),
                    low=processed_data.normalized_data.get("low", 0),
                    close=processed_data.normalized_data.get("close", 0),
                    volume=processed_data.normalized_data.get("volume", 0),
                )

            # Save technical indicators if available
            if processed_data.technical_indicators:
                # Store the latest indicators
                # This would need a separate model for storing indicators
                pass

            logger.info(f"Saved processed data for {processed_data.symbol}")
            return True

        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            return False


def create_pipeline() -> DataPipeline:
    """Factory function to create data pipeline"""
    return DataPipeline()


if __name__ == "__main__":
    # Test the pipeline
    pipeline = create_pipeline()

    # Test data processing
    test_data = {
        "symbol": "AAPL",
        "timestamp": datetime.now(),
        "open": 150.0,
        "high": 152.0,
        "low": 149.0,
        "close": 151.5,
        "volume": 50000000,
        "source": "yahoo",
    }

    processed = pipeline.process_raw_data(test_data, "yahoo", "stock")
    print(f"Processed: {processed}")

    pipeline.save_to_database(processed)
