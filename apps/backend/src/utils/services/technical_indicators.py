import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

import polars as pl
import numpy as np
from django.utils import timezone

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class IndicatorType(Enum):
    SMA = "sma"
    EMA = "ema"
    RSI = "rsi"
    MACD = "macd"
    BOLLINGER = "bollinger"
    STOCHASTIC = "stochastic"
    WILLIAMS_R = "williams_r"
    ATR = "atr"
    OBV = "obv"
    CCI = "cci"
    WMA = "wma"
    MFI = "mfi"
    VWAP = "vwap"
    ICHIMOKU = "ichimoku"
    PARABOLIC_SAR = "parabolic_sar"


class TechnicalIndicators:
    def __init__(self):
        self.logger = logger

    def calculate_sma(
        self, data: List[Dict[str, Any]], period: int, price_key: str = "close"
    ) -> List[Dict[str, float]]:
        df = pl.DataFrame(data)

        if len(df) < period:
            return []

        df = df.with_columns(
            pl.col(price_key).rolling_mean(window_size=period).alias("sma")
        )

        result = df.select(
            [pl.col("timestamp"), pl.col(price_key), pl.col("sma")]
        ).to_dicts()

        return result

    def calculate_ema(
        self, data: List[Dict[str, Any]], period: int, price_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []

        df = pl.DataFrame(data)

        multiplier = 2 / (period + 1)

        ema_values = []
        close_prices = df[price_key].to_list()

        ema = close_prices[0]
        ema_values.append(ema)

        for price in close_prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            ema_values.append(ema)

        timestamps = df["timestamp"].to_list()

        return [
            {"timestamp": timestamps[i], "close": close_prices[i], "ema": ema_values[i]}
            for i in range(len(timestamps))
        ]

    def calculate_rsi(
        self, data: List[Dict[str, Any]], period: int = 14, price_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < period + 1:
            return []

        df = pl.DataFrame(data)

        close_prices = df[price_key].to_list()

        deltas = []
        for i in range(1, len(close_prices)):
            delta = close_prices[i] - close_prices[i - 1]
            deltas.append(delta)

        gains = []
        losses = []
        for delta in deltas:
            if delta > 0:
                gains.append(delta)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(delta))

        rsi_values = [None] * period

        for i in range(period, len(gains)):
            avg_gain = np.mean(gains[max(0, i - period) : i + 1])
            avg_loss = np.mean(losses[max(0, i - period) : i + 1])

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

        timestamps = df["timestamp"].to_list()[period:]
        close_prices_result = close_prices[period:]

        return [
            {
                "timestamp": timestamps[i],
                "close": close_prices_result[i],
                "rsi": rsi_values[i],
            }
            for i in range(len(timestamps))
        ]

    def calculate_macd(
        self,
        data: List[Dict[str, Any]],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        price_key: str = "close",
    ) -> List[Dict[str, float]]:
        if len(data) < slow_period:
            return []

        df = pl.DataFrame(data)
        close_prices = df[price_key].to_list()
        timestamps = df["timestamp"].to_list()

        ema_fast = self._calculate_ema_array(close_prices, fast_period)
        ema_slow = self._calculate_ema_array(close_prices, slow_period)

        macd_line = []
        for i in range(len(ema_slow)):
            macd_line.append(ema_fast[i] - ema_slow[i])

        signal_line = self._calculate_ema_array(macd_line, signal_period)

        histogram = []
        for i in range(len(signal_line)):
            histogram.append(macd_line[i] - signal_line[i])

        result = []
        min_len = min(len(timestamps), len(macd_line))

        for i in range(min_len):
            result.append(
                {
                    "timestamp": timestamps[i],
                    "close": close_prices[i],
                    "macd": macd_line[i] if i < len(macd_line) else None,
                    "signal": signal_line[i] if i < len(signal_line) else None,
                    "histogram": histogram[i] if i < len(histogram) else None,
                }
            )

        return result

    def _calculate_ema_array(self, data: List[float], period: int) -> List[float]:
        if len(data) < period:
            return []

        multiplier = 2 / (period + 1)
        ema = data[0]
        ema_values = [ema]

        for price in data[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            ema_values.append(ema)

        return ema_values

    def calculate_bollinger_bands(
        self,
        data: List[Dict[str, Any]],
        period: int = 20,
        std_dev: float = 2.0,
        price_key: str = "close",
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []

        df = pl.DataFrame(data)

        df = df.with_columns(
            pl.col(price_key).rolling_mean(window_size=period).alias("sma")
        )

        rolling_std = df[price_key].rolling_std(window_size=period).to_list()

        upper_band = []
        lower_band = []
        sma_values = df["sma"].to_list()
        close_prices = df[price_key].to_list()
        timestamps = df["timestamp"].to_list()

        for i in range(len(sma_values)):
            if rolling_std[i] is None:
                upper_band.append(None)
                lower_band.append(None)
            else:
                upper_band.append(sma_values[i] + (std_dev * rolling_std[i]))
                lower_band.append(sma_values[i] - (std_dev * rolling_std[i]))

        result = []
        for i in range(len(timestamps)):
            result.append(
                {
                    "timestamp": timestamps[i],
                    "close": close_prices[i],
                    "sma": sma_values[i],
                    "upper_band": upper_band[i],
                    "lower_band": lower_band[i],
                    "bandwidth": upper_band[i] - lower_band[i]
                    if upper_band[i] and lower_band[i]
                    else None,
                }
            )

        return result

    def calculate_stochastic(
        self,
        data: List[Dict[str, Any]],
        k_period: int = 14,
        d_period: int = 3,
        smooth_k: int = 3,
        high_key: str = "high",
        low_key: str = "low",
        close_key: str = "close",
    ) -> List[Dict[str, float]]:
        if len(data) < k_period + d_period:
            return []

        df = pl.DataFrame(data)

        high_prices = df[high_key].to_list()
        low_prices = df[low_key].to_list()
        close_prices = df[close_key].to_list()
        timestamps = df["timestamp"].to_list()

        raw_k = []
        for i in range(k_period, len(high_prices)):
            high_range = max(high_prices[i - k_period : i + 1])
            low_range = min(low_prices[i - k_period : i + 1])

            if low_range == high_range:
                k_value = 50
            else:
                k_value = 100 * (
                    (close_prices[i] - low_range) / (high_range - low_range)
                )

            raw_k.append(k_value)

        full_k = [None] * (k_period + d_period - 1) + raw_k

        k_values = self._calculate_sma_array(full_k, smooth_k)

        d_values = []
        for k in k_values:
            if k is None:
                d_values.append(None)
            else:
                d_values.append(self._calculate_sma_value([k], d_period))

        result = []
        min_len = min(len(timestamps), len(k_values))

        for i in range(min_len):
            result.append(
                {
                    "timestamp": timestamps[i],
                    "close": close_prices[i],
                    "k": k_values[i],
                    "d": d_values[i],
                }
            )

        return result

    def _calculate_sma_array(
        self, data: List[Optional[float]], period: int
    ) -> List[Optional[float]]:
        if len(data) < period:
            return data[:]

        sma_values = data[: period - 1]

        for i in range(period - 1, len(data)):
            window = [x for x in data[i - period + 1 : i + 1] if x is not None]
            if window:
                sma_values.append(np.mean(window))
            else:
                sma_values.append(None)

        return sma_values

    def _calculate_sma_value(self, data: List[float], period: int) -> float:
        if len(data) < period:
            return 0
        return np.mean(data[-period:])

    def calculate_williams_r(
        self,
        data: List[Dict[str, Any]],
        period: int = 14,
        high_key: str = "high",
        low_key: str = "low",
        close_key: str = "close",
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []

        df = pl.DataFrame(data)

        high_prices = df[high_key].to_list()
        low_prices = df[low_key].to_list()
        close_prices = df[close_key].to_list()
        timestamps = df["timestamp"].to_list()

        williams_r_values = [None] * (period - 1)

        for i in range(period - 1, len(close_prices)):
            high_range = max(high_prices[i - period + 1 : i + 1])
            low_range = min(low_prices[i - period + 1 : i + 1])

            if high_range == low_range:
                wr = 0
            else:
                wr = -100 * ((high_range - close_prices[i]) / (high_range - low_range))

            williams_r_values.append(wr)

        result = []
        min_len = min(len(timestamps), len(williams_r_values))

        for i in range(min_len):
            result.append(
                {
                    "timestamp": timestamps[i],
                    "close": close_prices[i],
                    "williams_r": williams_r_values[i],
                }
            )

        return result

    def calculate_atr(
        self,
        data: List[Dict[str, Any]],
        period: int = 14,
        high_key: str = "high",
        low_key: str = "low",
        close_key: str = "close",
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []

        df = pl.DataFrame(data)

        high_prices = df[high_key].to_list()
        low_prices = df[low_key].to_list()
        close_prices = df[close_key].to_list()
        timestamps = df["timestamp"].to_list()

        true_ranges = []
        for i in range(1, len(close_prices)):
            high_low = high_prices[i] - low_prices[i]
            high_close = abs(high_prices[i] - close_prices[i - 1])
            low_close = abs(low_prices[i] - close_prices[i - 1])

            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)

        atr_values = []
        for i in range(len(true_ranges)):
            start_idx = max(0, i - period + 1)
            window = true_ranges[start_idx : i + 1]

            if window:
                atr = np.mean(window)
            else:
                atr = 0

            atr_values.append(atr)

        result = []
        offset = len(timestamps) - len(atr_values)

        for i in range(len(atr_values)):
            result.append(
                {
                    "timestamp": timestamps[offset + i],
                    "close": close_prices[offset + i],
                    "atr": atr_values[i],
                }
            )

        return result

    def calculate_obv(
        self,
        data: List[Dict[str, Any]],
        volume_key: str = "volume",
        close_key: str = "close",
    ) -> List[Dict[str, float]]:
        if len(data) < 2:
            return []

        df = pl.DataFrame(data)

        close_prices = df[close_key].to_list()
        volumes = df[volume_key].to_list()
        timestamps = df["timestamp"].to_list()

        obv_values = [0]

        for i in range(1, len(close_prices)):
            if close_prices[i] > close_prices[i - 1]:
                obv = obv_values[-1] + volumes[i]
            elif close_prices[i] < close_prices[i - 1]:
                obv = obv_values[-1] - volumes[i]
            else:
                obv = obv_values[-1]

            obv_values.append(obv)

        result = []
        min_len = min(len(timestamps), len(obv_values))

        for i in range(min_len):
            result.append(
                {
                    "timestamp": timestamps[i],
                    "close": close_prices[i],
                    "volume": volumes[i],
                    "obv": obv_values[i],
                }
            )

        return result

    def calculate_cci(
        self,
        data: List[Dict[str, Any]],
        period: int = 20,
        high_key: str = "high",
        low_key: str = "low",
        close_key: str = "close",
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []

        df = pl.DataFrame(data)

        high_prices = df[high_key].to_list()
        low_prices = df[low_key].to_list()
        close_prices = df[close_key].to_list()
        timestamps = df["timestamp"].to_list()

        typical_prices = []
        for i in range(len(close_prices)):
            tp = (high_prices[i] + low_prices[i] + close_prices[i]) / 3
            typical_prices.append(tp)

        sma_tp = self._calculate_sma_array(typical_prices, period)

        mean_deviations = []
        for i in range(len(typical_prices)):
            start_idx = max(0, i - period + 1)
            window = typical_prices[start_idx : i + 1]

            if window and sma_tp[i]:
                deviations = [abs(x - sma_tp[i]) for x in window]
                mean_dev = np.mean(deviations) if deviations else 0
            else:
                mean_dev = 0

            mean_deviations.append(mean_dev)

        cci_values = []
        for i in range(len(mean_deviations)):
            if mean_deviations[i] == 0:
                cci = 0
            else:
                cci = (typical_prices[i] - sma_tp[i]) / (0.015 * mean_deviations[i])

            cci_values.append(cci)

        result = []
        min_len = min(len(timestamps), len(cci_values))

        for i in range(min_len):
            result.append(
                {
                    "timestamp": timestamps[i],
                    "close": close_prices[i],
                    "cci": cci_values[i],
                }
            )

        return result

    async def calculate_all(
        self,
        data: List[Dict[str, Any]],
        indicators: Optional[List[IndicatorType]] = None,
    ) -> Dict[str, List[Dict[str, float]]]:
        if indicators is None:
            indicators = [
                IndicatorType.SMA,
                IndicatorType.EMA,
                IndicatorType.RSI,
                IndicatorType.MACD,
                IndicatorType.BOLLINGER,
                IndicatorType.STOCHASTIC,
                IndicatorType.WILLIAMS_R,
                IndicatorType.ATR,
                IndicatorType.OBV,
                IndicatorType.CCI,
            ]

        results = {}

        tasks = []

        if IndicatorType.SMA in indicators:
            tasks.append(
                ("sma", asyncio.to_thread(self.calculate_sma, data, period=20))
            )

        if IndicatorType.EMA in indicators:
            tasks.append(
                ("ema", asyncio.to_thread(self.calculate_ema, data, period=20))
            )

        if IndicatorType.RSI in indicators:
            tasks.append(
                ("rsi", asyncio.to_thread(self.calculate_rsi, data, period=14))
            )

        if IndicatorType.MACD in indicators:
            tasks.append(("macd", asyncio.to_thread(self.calculate_macd, data)))

        if IndicatorType.BOLLINGER in indicators:
            tasks.append(
                ("bollinger", asyncio.to_thread(self.calculate_bollinger_bands, data))
            )

        if IndicatorType.STOCHASTIC in indicators:
            tasks.append(
                ("stochastic", asyncio.to_thread(self.calculate_stochastic, data))
            )

        if IndicatorType.WILLIAMS_R in indicators:
            tasks.append(
                ("williams_r", asyncio.to_thread(self.calculate_williams_r, data))
            )

        if IndicatorType.ATR in indicators:
            tasks.append(("atr", asyncio.to_thread(self.calculate_atr, data)))

        if IndicatorType.OBV in indicators:
            tasks.append(("obv", asyncio.to_thread(self.calculate_obv, data)))

        if IndicatorType.CCI in indicators:
            tasks.append(("cci", asyncio.to_thread(self.calculate_cci, data)))

        for indicator_name, task in tasks:
            try:
                results[indicator_name] = await task
                self.logger.debug(f"Calculated {indicator_name} indicator")
            except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
                self.logger.error(f"Failed to calculate {indicator_name}: {e}")
                results[indicator_name] = []

        return results

    def calculate_wma(
        self, data: List[Dict[str, Any]], period: int, price_key: str = "close"
    ) -> List[Dict[str, float]]:
        """Calculate Weighted Moving Average"""
        if len(data) < period:
            return []

        prices = np.array([d.get(price_key, 0) for d in data], dtype=float)
        timestamps = [d.get("timestamp") for d in data]

        weights = np.arange(1, period + 1)
        wma = np.convolve(prices, weights, mode="valid") / weights.sum()

        result = []
        offset = len(data) - len(wma)
        for i, value in enumerate(wma):
            result.append(
                {
                    "timestamp": timestamps[i + offset],
                    "wma": round(float(value), 4),
                    "price": prices[i + offset],
                }
            )

        return result

    def calculate_mfi(
        self, data: List[Dict[str, Any]], period: int = 14, price_key: str = "close"
    ) -> List[Dict[str, float]]:
        """Calculate Money Flow Index"""
        if len(data) < period + 1:
            return []

        highs = np.array([d.get("high", 0) for d in data], dtype=float)
        lows = np.array([d.get("low", 0) for d in data], dtype=float)
        closes = np.array([d.get(price_key, 0) for d in data], dtype=float)
        volumes = np.array([d.get("volume", 0) for d in data], dtype=float)

        typical_price = (highs + lows + closes) / 3
        raw_money_flow = typical_price * volumes

        positive_flow = np.zeros(len(data))
        negative_flow = np.zeros(len(data))

        for i in range(1, len(data)):
            if typical_price[i] > typical_price[i - 1]:
                positive_flow[i] = raw_money_flow[i]
            else:
                negative_flow[i] = raw_money_flow[i]

        money_ratio = np.zeros(len(data))
        for i in range(period, len(data)):
            pos_sum = positive_flow[i - period + 1 : i + 1].sum()
            neg_sum = negative_flow[i - period + 1 : i + 1].sum()
            if neg_sum > 0:
                money_ratio[i] = pos_sum / neg_sum

        mfi = np.zeros(len(data))
        for i in range(period, len(data)):
            if money_ratio[i] != 0:
                mfi[i] = 100 - (100 / (1 + money_ratio[i]))

        result = []
        for i in range(period, len(data)):
            result.append(
                {
                    "timestamp": data[i].get("timestamp"),
                    "mfi": round(float(mfi[i]), 4),
                    "signal": "overbought"
                    if mfi[i] > 80
                    else "oversold"
                    if mfi[i] < 20
                    else "neutral",
                }
            )

        return result

    def calculate_vwap(
        self, data: List[Dict[str, Any]], price_key: str = "close"
    ) -> List[Dict[str, float]]:
        """Calculate Volume Weighted Average Price"""
        if len(data) == 0:
            return []

        df = pl.DataFrame(data)

        df = df.with_columns(
            [
                ((pl.col("high") + pl.col("low") + pl.col(price_key)) / 3).alias(
                    "typical_price"
                ),
                (pl.col("typical_price") * pl.col("volume")).alias("pv"),
            ]
        )

        df = df.with_columns(
            [
                pl.col("pv").cum_sum().alias("cum_pv"),
                pl.col("volume").cum_sum().alias("cum_vol"),
            ]
        )

        df = df.with_columns([(pl.col("cum_pv") / pl.col("cum_vol")).alias("vwap")])

        result = df.select(
            [pl.col("timestamp"), pl.col(price_key), pl.col("vwap")]
        ).to_dicts()

        return result

    def calculate_ichimoku(
        self,
        data: List[Dict[str, Any]],
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_span_b_period: int = 52,
        price_key: str = "close",
    ) -> Dict[str, List[Dict[str, float]]]:
        """Calculate Ichimoku Cloud components"""
        if len(data) < senkou_span_b_period:
            return {
                "tenkan": [],
                "kijun": [],
                "senkou_a": [],
                "senkou_b": [],
                "chikou": [],
            }

        highs = np.array([d.get("high", 0) for d in data], dtype=float)
        lows = np.array([d.get("low", 0) for d in data], dtype=float)
        closes = np.array([d.get(price_key, 0) for d in data], dtype=float)
        timestamps = [d.get("timestamp") for d in data]

        def rolling_max(arr, period):
            result = np.zeros(len(arr))
            for i in range(len(arr)):
                if i < period - 1:
                    result[i] = np.nan
                else:
                    result[i] = np.max(arr[i - period + 1 : i + 1])
            return result

        def rolling_min(arr, period):
            result = np.zeros(len(arr))
            for i in range(len(arr)):
                if i < period - 1:
                    result[i] = np.nan
                else:
                    result[i] = np.min(arr[i - period + 1 : i + 1])
            return result

        tenkan_sen = (
            rolling_max(highs, tenkan_period) + rolling_min(lows, tenkan_period)
        ) / 2
        kijun_sen = (
            rolling_max(highs, kijun_period) + rolling_min(lows, kijun_period)
        ) / 2
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        senkou_span_b = (
            rolling_max(highs, senkou_span_b_period)
            + rolling_min(lows, senkou_span_b_period)
        ) / 2

        chikou_span = np.roll(closes, kijun_period)

        result = {
            "tenkan": [],
            "kijun": [],
            "senkou_a": [],
            "senkou_b": [],
            "chikou": [],
        }

        for i in range(len(data)):
            if not np.isnan(tenkan_sen[i]):
                result["tenkan"].append(
                    {
                        "timestamp": timestamps[i],
                        "tenkan": round(float(tenkan_sen[i]), 4),
                    }
                )
            if not np.isnan(kijun_sen[i]):
                result["kijun"].append(
                    {"timestamp": timestamps[i], "kijun": round(float(kijun_sen[i]), 4)}
                )

        for i in range(kijun_period, len(data)):
            if not np.isnan(senkou_span_a[i]):
                result["senkou_a"].append(
                    {
                        "timestamp": timestamps[i + kijun_period],
                        "senkou_a": round(float(senkou_span_a[i]), 4),
                    }
                )
            if not np.isnan(senkou_span_b[i]):
                result["senkou_b"].append(
                    {
                        "timestamp": timestamps[i + kijun_period],
                        "senkou_b": round(float(senkou_span_b[i]), 4),
                    }
                )

        for i in range(kijun_period, len(chikou_span)):
            if i < len(closes):
                result["chikou"].append(
                    {
                        "timestamp": timestamps[i],
                        "chikou": round(float(chikou_span[i]), 4),
                    }
                )

        return result

    def calculate_parabolic_sar(
        self,
        data: List[Dict[str, Any]],
        acceleration: float = 0.02,
        maximum: float = 0.2,
        price_key: str = "close",
    ) -> List[Dict[str, float]]:
        """Calculate Parabolic SAR"""
        if len(data) < 2:
            return []

        highs = np.array([d.get("high", 0) for d in data], dtype=float)
        lows = np.array([d.get("low", 0) for d in data], dtype=float)
        closes = np.array([d.get(price_key, 0) for d in data], dtype=float)
        timestamps = [d.get("timestamp") for d in data]

        sar = np.zeros(len(highs))
        ep = np.zeros(len(highs))
        trend = np.zeros(len(highs))

        sar[0] = lows[0]
        ep[0] = highs[0]
        trend[0] = 1

        for i in range(1, len(highs)):
            if trend[i - 1] == 1:
                sar[i] = sar[i - 1] + acceleration * (ep[i - 1] - sar[i - 1])
                if highs[i] > ep[i - 1]:
                    ep[i] = highs[i]
                    if ep[i] - sar[i] > maximum:
                        sar[i] = ep[i] - maximum
                else:
                    sar[i] = sar[i]
            else:
                sar[i] = sar[i - 1] + acceleration * (ep[i - 1] - sar[i - 1])
                if lows[i] < ep[i - 1]:
                    ep[i] = lows[i]
                    if sar[i] - ep[i] > maximum:
                        sar[i] = ep[i] + maximum
                else:
                    sar[i] = sar[i]

            if (trend[i - 1] == 1 and closes[i] < sar[i]) or (
                trend[i - 1] == -1 and closes[i] > sar[i]
            ):
                trend[i] = -trend[i - 1]
                if trend[i] == 1:
                    ep[i] = highs[i]
                    sar[i] = lows[i]
                else:
                    ep[i] = lows[i]
                    sar[i] = highs[i]
            else:
                trend[i] = trend[i - 1]

        result = []
        for i in range(len(data)):
            result.append(
                {
                    "timestamp": timestamps[i],
                    "psar": round(float(sar[i]), 4),
                    "trend": "bullish" if trend[i] == 1 else "bearish",
                    "signal": "reversal"
                    if (i > 0 and trend[i] != trend[i - 1])
                    else "continuation",
                }
            )

        return result


_technical_indicators_instance: Optional[TechnicalIndicators] = None


def get_technical_indicators() -> TechnicalIndicators:
    global _technical_indicators_instance
    if _technical_indicators_instance is None:
        _technical_indicators_instance = TechnicalIndicators()
    return _technical_indicators_instance
