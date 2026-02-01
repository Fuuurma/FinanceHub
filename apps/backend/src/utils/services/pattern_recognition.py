"""
Pattern Recognition Service for FinanceHub

Detects common technical analysis chart patterns.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from scipy.signal import find_peaks, savgol_filter
from scipy.ndimage import gaussian_filter1d
import numpy as np
import polars as pl

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class PatternType(Enum):
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_AND_SHOULDERS = "inverse_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    BULLISH_FLAG = "bullish_flag"
    BEARISH_FLAG = "bearish_flag"
    RISING_WEDGE = "rising_wedge"
    FALLING_WEDGE = "falling_wedge"
    SUPPORT_LEVEL = "support_level"
    RESISTANCE_LEVEL = "resistance_level"


class PatternDirection(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class PatternPoint:
    index: int
    price: float
    timestamp: str
    point_type: str


@dataclass
class DetectedPattern:
    pattern_type: PatternType
    direction: PatternDirection
    confidence: float
    start_index: int
    end_index: int
    start_timestamp: str
    end_timestamp: str
    points: List[PatternPoint]
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternRecognition:
    def __init__(
        self,
        smoothing_window: int = 5,
        peak_prominence_factor: float = 0.02,
        min_touch_count: int = 3,
        pattern_tolerance: float = 0.03,
    ):
        self.smoothing_window = smoothing_window
        self.peak_prominence_factor = peak_prominence_factor
        self.min_touch_count = min_touch_count
        self.pattern_tolerance = pattern_tolerance
        self.logger = logger

    def _prepare_data(self, data: List[Dict[str, Any]]) -> pl.DataFrame:
        if len(data) < 10:
            raise ValueError("Minimum 10 data points required")
        df = pl.DataFrame(data)
        required = ["timestamp", "open", "high", "low", "close"]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        df = df.with_columns(
            [
                pl.col("high").cast(pl.Float64),
                pl.col("low").cast(pl.Float64),
                pl.col("close").cast(pl.Float64),
            ]
        )
        return df

    def _smooth_prices(self, prices: np.ndarray) -> np.ndarray:
        if len(prices) < self.smoothing_window:
            return prices
        try:
            return savgol_filter(
                prices, min(self.smoothing_window, len(prices) // 2 * 2 + 1), 3
            )
        except Exception:
            return gaussian_filter1d(prices, sigma=1)

    def _find_peaks_and_troughs(
        self, highs: np.ndarray, lows: np.ndarray
    ) -> Tuple[List[int], List[int]]:
        price_range = np.max(highs) - np.min(lows)
        min_prominence = price_range * self.peak_prominence_factor
        peak_indices, _ = find_peaks(
            highs, prominence=min_prominence, distance=5, width=2
        )
        trough_indices, _ = find_peaks(
            -lows, prominence=min_prominence, distance=5, width=2
        )
        return list(peak_indices), list(trough_indices)

    def detect_head_and_shoulders(
        self, data: List[Dict[str, Any]], min_confidence: float = 60.0
    ) -> List[DetectedPattern]:
        patterns = []
        try:
            df = self._prepare_data(data)
            closes = df["close"].to_numpy()
            highs = df["high"].to_numpy()
            timestamps = df["timestamp"].to_list()
            smoothed_highs = self._smooth_prices(highs)
            peak_indices, _ = self._find_peaks_and_troughs(smoothed_highs, closes)
            if len(peak_indices) < 3:
                return patterns
            for i in range(len(peak_indices) - 2):
                left_idx, head_idx, right_idx = (
                    peak_indices[i],
                    peak_indices[i + 1],
                    peak_indices[i + 2],
                )
                left_shoulder, head, right_shoulder = (
                    highs[left_idx],
                    highs[head_idx],
                    highs[right_idx],
                )
                left_low_idx = left_idx + np.argmin(closes[left_idx:head_idx])
                right_low_idx = head_idx + np.argmin(closes[head_idx:right_idx])
                neckline = (closes[left_low_idx] + closes[right_low_idx]) / 2
                shoulder_sym = 1 - abs(left_shoulder - right_shoulder) / (
                    head - min(left_shoulder, right_shoulder) + 0.001
                )
                head_prom = (head - neckline) / (head + 0.001) * 100
                confidence = shoulder_sym * 40 + min(head_prom, 30)
                if confidence >= min_confidence:
                    pattern = DetectedPattern(
                        pattern_type=PatternType.HEAD_AND_SHOULDERS,
                        direction=PatternDirection.BEARISH,
                        confidence=min(confidence, 100),
                        start_index=left_idx,
                        end_index=right_idx,
                        start_timestamp=timestamps[left_idx],
                        end_timestamp=timestamps[right_idx],
                        points=[
                            PatternPoint(
                                left_idx,
                                left_shoulder,
                                timestamps[left_idx],
                                "left_shoulder",
                            ),
                            PatternPoint(head_idx, head, timestamps[head_idx], "head"),
                            PatternPoint(
                                right_idx,
                                right_shoulder,
                                timestamps[right_idx],
                                "right_shoulder",
                            ),
                        ],
                        target_price=neckline - (head - neckline) * 0.5,
                        stop_loss=max(left_shoulder, right_shoulder) * 1.02,
                        description=f"Head and Shoulders. Neckline: ${neckline:.2f}",
                        metadata={
                            "left_shoulder": left_shoulder,
                            "head": head,
                            "right_shoulder": right_shoulder,
                            "neckline": neckline,
                        },
                    )
                    patterns.append(pattern)
            self.logger.info(f"Detected {len(patterns)} Head and Shoulders patterns")
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.logger.error(f"Error detecting Head and Shoulders: {e}")
        return patterns

    def detect_double_top(
        self, data: List[Dict[str, Any]], min_confidence: float = 60.0
    ) -> List[DetectedPattern]:
        patterns = []
        try:
            df = self._prepare_data(data)
            highs = df["high"].to_numpy()
            closes = df["close"].to_numpy()
            timestamps = df["timestamp"].to_list()
            peak_indices, trough_indices = self._find_peaks_and_troughs(
                self._smooth_prices(highs), closes
            )
            if len(peak_indices) < 2:
                return patterns
            for i in range(len(peak_indices) - 1):
                first_idx, second_idx = peak_indices[i], peak_indices[i + 1]
                if second_idx - first_idx < 10:
                    continue
                first_peak, second_peak = highs[first_idx], highs[second_idx]
                avg_price = (first_peak + second_peak) / 2
                symmetry = 1 - abs(first_peak - second_peak) / avg_price
                min_trough = np.min(closes[first_idx:second_idx])
                breakdown = (avg_price - min_trough) / avg_price * 100
                confidence = symmetry * 50 + min(breakdown, 50)
                if confidence >= min_confidence:
                    pattern = DetectedPattern(
                        pattern_type=PatternType.DOUBLE_TOP,
                        direction=PatternDirection.BEARISH,
                        confidence=min(confidence, 100),
                        start_index=first_idx,
                        end_index=second_idx,
                        start_timestamp=timestamps[first_idx],
                        end_timestamp=timestamps[second_idx],
                        points=[
                            PatternPoint(
                                first_idx,
                                first_peak,
                                timestamps[first_idx],
                                "first_peak",
                            ),
                            PatternPoint(
                                second_idx,
                                second_peak,
                                timestamps[second_idx],
                                "second_peak",
                            ),
                        ],
                        target_price=min_trough - (avg_price - min_trough) * 0.5,
                        stop_loss=avg_price * 1.02,
                        description=f"Double Top. Resistance: ${avg_price:.2f}",
                        metadata={
                            "resistance_level": avg_price,
                            "support_level": min_trough,
                        },
                    )
                    patterns.append(pattern)
            self.logger.info(f"Detected {len(patterns)} Double Top patterns")
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.logger.error(f"Error detecting Double Top: {e}")
        return patterns

    def detect_double_bottom(
        self, data: List[Dict[str, Any]], min_confidence: float = 60.0
    ) -> List[DetectedPattern]:
        patterns = []
        try:
            df = self._prepare_data(data)
            lows = df["low"].to_numpy()
            closes = df["close"].to_numpy()
            timestamps = df["timestamp"].to_list()
            _, trough_indices = self._find_peaks_and_troughs(
                closes, self._smooth_prices(lows)
            )
            if len(trough_indices) < 2:
                return patterns
            for i in range(len(trough_indices) - 1):
                first_idx, second_idx = trough_indices[i], trough_indices[i + 1]
                if second_idx - first_idx < 10:
                    continue
                first_trough, second_trough = lows[first_idx], lows[second_idx]
                avg_price = (first_trough + second_trough) / 2
                symmetry = 1 - abs(first_trough - second_trough) / avg_price
                max_peak = np.max(closes[first_idx:second_idx])
                breakout = (max_peak - avg_price) / avg_price * 100
                confidence = symmetry * 50 + min(breakout, 50)
                if confidence >= min_confidence:
                    pattern = DetectedPattern(
                        pattern_type=PatternType.DOUBLE_BOTTOM,
                        direction=PatternDirection.BULLISH,
                        confidence=min(confidence, 100),
                        start_index=first_idx,
                        end_index=second_idx,
                        start_timestamp=timestamps[first_idx],
                        end_timestamp=timestamps[second_idx],
                        points=[
                            PatternPoint(
                                first_idx,
                                first_trough,
                                timestamps[first_idx],
                                "first_trough",
                            ),
                            PatternPoint(
                                second_idx,
                                second_trough,
                                timestamps[second_idx],
                                "second_trough",
                            ),
                        ],
                        target_price=max_peak + (max_peak - avg_price) * 0.5,
                        stop_loss=avg_price * 0.98,
                        description=f"Double Bottom. Support: ${avg_price:.2f}",
                        metadata={
                            "support_level": avg_price,
                            "resistance_level": max_peak,
                        },
                    )
                    patterns.append(pattern)
            self.logger.info(f"Detected {len(patterns)} Double Bottom patterns")
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.logger.error(f"Error detecting Double Bottom: {e}")
        return patterns

    def detect_triangle(
        self, data: List[Dict[str, Any]], min_confidence: float = 60.0
    ) -> List[DetectedPattern]:
        patterns = []
        try:
            df = self._prepare_data(data)
            highs = df["high"].to_numpy()
            lows = df["low"].to_numpy()
            timestamps = df["timestamp"].to_list()
            peak_indices, trough_indices = self._find_peaks_and_troughs(highs, lows)
            if len(peak_indices) < 2 or len(trough_indices) < 2:
                return patterns
            x = np.arange(len(highs))
            high_slope = np.polyfit(
                peak_indices[-3:], [highs[i] for i in peak_indices[-3:]], 1
            )[0]
            low_slope = np.polyfit(
                trough_indices[-3:], [lows[i] for i in trough_indices[-3:]], 1
            )[0]
            price_range = np.max(highs[-20:]) - np.min(lows[-20:])
            convergence = abs(high_slope) + abs(low_slope)
            if convergence > 0:
                if abs(high_slope) < 0.1 and low_slope > 0.1:
                    pattern_type = PatternType.ASCENDING_TRIANGLE
                    direction = PatternDirection.BULLISH
                elif abs(high_slope) < 0.1 and low_slope < -0.1:
                    pattern_type = PatternType.DESCENDING_TRIANGLE
                    direction = PatternDirection.BEARISH
                elif high_slope * low_slope < 0:
                    pattern_type = PatternType.SYMMETRICAL_TRIANGLE
                    direction = PatternDirection.NEUTRAL
                else:
                    return patterns
                confidence = min(convergence / (price_range / 10) * 40 + 60, 100)
                if confidence >= min_confidence:
                    pattern = DetectedPattern(
                        pattern_type=pattern_type,
                        direction=direction,
                        confidence=confidence,
                        start_index=peak_indices[0],
                        end_index=len(highs) - 1,
                        start_timestamp=timestamps[peak_indices[0]],
                        end_timestamp=timestamps[-1],
                        points=[
                            PatternPoint(
                                peak_indices[0],
                                highs[peak_indices[0]],
                                timestamps[peak_indices[0]],
                                "first_peak",
                            ),
                            PatternPoint(
                                trough_indices[0],
                                lows[trough_indices[0]],
                                timestamps[trough_indices[0]],
                                "first_trough",
                            ),
                        ],
                        description=f"{pattern_type.value.replace('_', ' ').title()} detected",
                        metadata={"high_slope": high_slope, "low_slope": low_slope},
                    )
                    patterns.append(pattern)
            self.logger.info(f"Detected {len(patterns)} Triangle patterns")
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.logger.error(f"Error detecting Triangle: {e}")
        return patterns

    def detect_support_resistance(
        self, data: List[Dict[str, Any]], min_touches: int = 3
    ) -> Dict[str, List]:
        support_levels = []
        resistance_levels = []
        try:
            df = self._prepare_data(data)
            closes = df["close"].to_numpy()
            highs = df["high"].to_numpy()
            lows = df["low"].to_numpy()
            timestamps = df["timestamp"].to_list()
            price_range = np.max(highs) - np.min(lows)
            num_bins = min(20, len(data) // 5)
            bin_size = price_range / num_bins
            bins = {}
            for i, (high, low, ts) in enumerate(zip(highs, lows, timestamps)):
                for price in np.arange(low, high + bin_size, bin_size):
                    bin_key = int(price / bin_size)
                    if bin_key not in bins:
                        bins[bin_key] = {"touches": 0, "price": price, "timestamps": []}
                    bins[bin_key]["touches"] += 1
                    bins[bin_key]["timestamps"].append(ts)
            for bin_data in bins.values():
                strength = min(bin_data["touches"] / min_touches * 100, 100)
                if strength >= 50:
                    level = {
                        "price": bin_data["price"],
                        "strength": strength,
                        "touch_count": bin_data["touches"],
                        "timestamps": bin_data["timestamps"],
                    }
                    if bin_data["price"] < np.mean(closes):
                        support_levels.append(level)
                    else:
                        resistance_levels.append(level)
            support_levels.sort(key=lambda x: x["strength"], reverse=True)
            resistance_levels.sort(key=lambda x: x["strength"], reverse=True)
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.logger.error(f"Error detecting Support/Resistance: {e}")
        return {"support": support_levels[:10], "resistance": resistance_levels[:10]}

    def detect_all_patterns(
        self, data: List[Dict[str, Any]], min_confidence: float = 60.0
    ) -> List[DetectedPattern]:
        patterns = []
        patterns.extend(self.detect_head_and_shoulders(data, min_confidence))
        patterns.extend(self.detect_double_top(data, min_confidence))
        patterns.extend(self.detect_double_bottom(data, min_confidence))
        patterns.extend(self.detect_triangle(data, min_confidence))
        return sorted(patterns, key=lambda p: p.confidence, reverse=True)


def get_pattern_recognition() -> PatternRecognition:
    return PatternRecognition()
