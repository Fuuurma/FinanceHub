from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
import math

from utils.services.number_utils import format_percent, format_ratio


def calculate_roi(
    initial_value: float,
    final_value: float,
    as_percent: bool = True,
    decimals: int = 2,
) -> float:
    try:
        if initial_value <= 0:
            return 0.0
        roi = (final_value - initial_value) / initial_value
        if as_percent:
            return roi * 100
        return roi
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def calculate_cagr(
    initial_value: float,
    final_value: float,
    years: float,
    as_percent: bool = True,
    decimals: int = 2,
) -> Optional[float]:
    try:
        if initial_value <= 0 or years <= 0:
            return None
        cagr = (final_value / initial_value) ** (1 / years) - 1
        if as_percent:
            return cagr * 100
        return cagr
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_volatility(
    returns: List[float],
    annualize: bool = True,
    trading_days: int = 252,
    decimals: int = 2,
) -> Optional[float]:
    try:
        if len(returns) < 2:
            return None
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)
        if annualize:
            volatility = std_dev * math.sqrt(trading_days)
        else:
            volatility = std_dev
        return round(volatility * 100, decimals) if decimals else volatility * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.0,
    annualize: bool = True,
    trading_days: int = 252,
    decimals: int = 2,
) -> Optional[float]:
    try:
        volatility = calculate_volatility(returns, annualize, trading_days, decimals=None)
        if volatility is None or volatility == 0:
            return None
        mean_return = sum(returns) / len(returns) if returns else 0
        excess_return = mean_return - (risk_free_rate / 100 / trading_days if annualize else risk_free_rate)
        sharpe = excess_return / (volatility / 100 if decimals else volatility)
        return round(sharpe, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_sortino_ratio(
    returns: List[float],
    risk_free_rate: float = 0.0,
    target_return: float = 0.0,
    annualize: bool = True,
    trading_days: int = 252,
    decimals: int = 2,
) -> Optional[float]:
    try:
        mean_return = sum(returns) / len(returns) if returns else 0
        downside_returns = [r for r in returns if r < target_return]
        if not downside_returns:
            return float('inf')
        downside_variance = sum((r - mean_return) ** 2 for r in downside_returns) / len(downside_returns)
        downside_std_dev = math.sqrt(downside_variance)
        if annualize:
            downside_std_dev *= math.sqrt(trading_days)
        if *= downside_std_dev == 0:
            return None
        excess_return = mean_return - (risk_free_rate / 100 / trading_days if annualize else risk_free_rate)
        sortino = excess_return / downside_std_dev
        return round(sortino, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_beta(
    asset_returns: List[float],
    benchmark_returns: List[float],
    decimals: int = 4,
) -> Optional[float]:
    try:
        if len(asset_returns) != len(benchmark_returns) or len(asset_returns) < 2:
            return None
        mean_asset = sum(asset_returns) / len(asset_returns)
        mean_benchmark = sum(benchmark_returns) / len(benchmark_returns)
        covariance = sum(
            (a - mean_asset) * (b - mean_benchmark)
            for a, b in zip(asset_returns, benchmark_returns)
        ) / (len(asset_returns) - 1)
        variance_benchmark = sum((b - mean_benchmark) ** 2 for b in benchmark_returns) / (len(benchmark_returns) - 1)
        if variance_benchmark == 0:
            return None
        beta = covariance / variance_benchmark
        return round(beta, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_alpha(
    asset_return: float,
    benchmark_return: float,
    beta: float,
    risk_free_rate: float = 0.0,
    decimals: int = 2,
) -> float:
    try:
        alpha = asset_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))
        return round(alpha, decimals)
    except (ValueError, TypeError):
        return 0.0


def calculate_r_squared(
    asset_returns: List[float],
    benchmark_returns: List[float],
    decimals: int = 4,
) -> Optional[float]:
    try:
        if len(asset_returns) != len(benchmark_returns) or len(asset_returns) < 2:
            return None
        mean_asset = sum(asset_returns) / len(asset_returns)
        mean_benchmark = sum(benchmark_returns) / len(benchmark_returns)
        ss_total = sum((a - mean_asset) ** 2 for a in asset_returns)
        ss_res = sum((a - b) ** 2 for a, b in zip(asset_returns, benchmark_returns))
        if ss_total == 0:
            return None
        r_squared = 1 - (ss_res / ss_total)
        return round(r_squared, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_max_drawdown(values: List[float], decimals: int = 2) -> Optional[float]:
    try:
        if len(values) < 2:
            return None
        max_drawdown = 0.0
        peak = values[0]
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        return round(max_drawdown * 100, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_calmar_ratio(
    annualized_return: float,
    max_drawdown: float,
    decimals: int = 2,
) -> Optional[float]:
    try:
        if max_drawdown <= 0:
            return None
        calmar = annualized_return / max_drawdown
        return round(calmar, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_sma(data: List[float], period: int) -> List[Optional[float]]:
    try:
        if len(data) < period or period <= 0:
            return [None] * len(data)
        sma_values = []
        for i in range(len(data)):
            if i < period - 1:
                sma_values.append(None)
            else:
                window = data[i - period + 1:i + 1]
                sma_values.append(sum(window) / period)
        return sma_values
    except (ValueError, TypeError):
        return [None] * len(data)


def calculate_ema(data: List[float], period: int, smoothing: int = 2) -> List[Optional[float]]:
    try:
        if len(data) < period or period <= 0:
            return [None] * len(data)
        multiplier = smoothing / (period + 1)
        ema_values = []
        first_sma = sum(data[:period]) / period
        ema_values.append(first_sma)
        for i in range(period, len(data)):
            ema = (data[i] - ema_values[-1]) * multiplier + ema_values[-1]
            ema_values.append(ema)
        padding = [None] * (period - 1)
        return padding + ema_values
    except (ValueError, TypeError):
        return [None] * len(data)


def calculate_rsi(
    data: List[float],
    period: int = 14,
    decimals: int = 2,
) -> List[Optional[float]]:
    try:
        if len(data) < period + 1 or period <= 0:
            return [None] * len(data)
        rsi_values = []
        deltas = [data[i] - data[i - 1] for i in range(1, len(data))]
        for i in range(len(deltas)):
            if i < period - 1:
                rsi_values.append(None)
            elif i == period - 1:
                avg_gain = sum(d for d in deltas[:period] if d > 0) / period
                avg_loss = sum(-d for d in deltas[:period] if d < 0) / period
                if avg_loss == 0:
                    rsi_values.append(100.0)
                else:
                    rs = avg_gain / avg_loss
                    rsi_values.append(100 - (100 / (1 + rs)))
            else:
                prev_ema_gain = rsi_values[-1] if rsi_values[-1] is not None else 0
                prev_ema_loss = 100 - prev_ema_gain if prev_ema_gain < 100 else 50
                current_gain = deltas[i] if deltas[i] > 0 else 0
                current_loss = -deltas[i] if deltas[i] < 0 else 0
                avg_gain = (prev_ema_gain * (period - 1) + current_gain) / period
                avg_loss = (prev_ema_loss * (period - 1) + current_loss) / period
                if avg_loss == 0:
                    rsi_values.append(100.0)
                else:
                    rs = avg_gain / avg_loss
                    rsi_values.append(100 - (100 / (1 + rs)))
        return [round(r, decimals) if r is not None else None for r in rsi_values]
    except (ValueError, TypeError, ZeroDivisionError):
        return [None] * len(data)


def calculate_macd(
    data: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    try:
        fast_ema = calculate_ema(data, fast_period)
        slow_ema = calculate_ema(data, slow_period)
        macd_line = []
        for i in range(len(fast_ema)):
            if fast_ema[i] is not None and slow_ema[i] is not None:
                macd_line.append(fast_ema[i] - slow_ema[i])
            else:
                macd_line.append(None)
        signal_line = calculate_ema([v for v in macd_line if v is not None], signal_period)
        signal_line = [None] * (len(macd_line) - len(signal_line)) + signal_line
        histogram = []
        for i in range(len(macd_line)):
            if macd_line[i] is not None and signal_line[i] is not None:
                histogram.append(macd_line[i] - signal_line[i])
            else:
                histogram.append(None)
        return macd_line, signal_line, histogram
    except (ValueError, TypeError):
        return [None] * len(data), [None] * len(data), [None] * len(data)


def calculate_bollinger_bands(
    data: List[float],
    period: int = 20,
    std_dev: float = 2.0,
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    try:
        sma = calculate_sma(data, period)
        upper_band = []
        lower_band = []
        for i in range(len(data)):
            if i < period - 1 or sma[i] is None:
                upper_band.append(None)
                lower_band.append(None)
            else:
                window = data[i - period + 1:i + 1]
                window_sma = sma[i]
                variance = sum((v - window_sma) ** 2 for v in window) / period
                std = math.sqrt(variance)
                upper_band.append(window_sma + (std_dev * std))
                lower_band.append(window_sma - (std_dev * std))
        return upper_band, sma, lower_band
    except (ValueError, TypeError):
        return [None] * len(data), [None] * len(data), [None] * len(data)


def calculate_obv(
    prices: List[float],
    volumes: List[float],
) -> List[Optional[float]]:
    try:
        if len(prices) != len(volumes):
            return [None] * len(prices)
        obv = []
        cumulative = 0
        for i in range(len(prices)):
            if i == 0:
                obv.append(cumulative + volumes[i])
            else:
                if prices[i] > prices[i - 1]:
                    cumulative += volumes[i]
                elif prices[i] < prices[i - 1]:
                    cumulative -= volumes[i]
                obv.append(cumulative)
        return obv
    except (ValueError, TypeError):
        return [None] * len(prices)


def calculate_atr(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    period: int = 14,
    decimals: int = 2,
) -> List[Optional[float]]:
    try:
        if len(highs) != len(lows) or len(highs) != len(closes):
            return [None] * len(highs)
        true_ranges = []
        for i in range(len(highs)):
            if i == 0:
                tr = highs[i] - lows[i]
            else:
                tr = max(
                    highs[i] - lows[i],
                    abs(highs[i] - closes[i - 1]),
                    abs(lows[i] - closes[i - 1]),
                )
            true_ranges.append(tr)
        atr = calculate_ema(true_ranges, period)
        return [round(v, decimals) if v is not None else None for v in atr]
    except (ValueError, TypeError):
        return [None] * len(highs)


def calculate_standard_deviation(
    values: List[float],
    decimals: int = 4,
) -> Optional[float]:
    try:
        if len(values) < 2:
            return None
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        std_dev = math.sqrt(variance)
        return round(std_dev, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_variance(
    values: List[float],
    decimals: int = 6,
) -> Optional[float]:
    try:
        if len(values) < 2:
            return None
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        return round(variance, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_correlation(
    values1: List[float],
    values2: List[float],
    decimals: int = 4,
) -> Optional[float]:
    try:
        if len(values1) != len(values2) or len(values1) < 2:
            return None
        mean1 = sum(values1) / len(values1)
        mean2 = sum(values2) / len(values2)
        covariance = sum(
            (v1 - mean1) * (v2 - mean2)
            for v1, v2 in zip(values1, values2)
        ) / (len(values1) - 1)
        std1 = math.sqrt(calculate_variance(values1, decimals=None) or 0)
        std2 = math.sqrt(calculate_variance(values2, decimals=None) or 0)
        if std1 == 0 or std2 == 0:
            return None
        correlation = covariance / (std1 * std2)
        return round(correlation, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_covariance(
    values1: List[float],
    values2: List[float],
    decimals: float = 6,
) -> Optional[float]:
    try:
        if len(values1) != len(values2) or len(values1) < 2:
            return None
        mean1 = sum(values1) / len(values1)
        mean2 = sum(values2) / len(values2)
        covariance = sum(
            (v1 - mean1) * (v2 - mean2)
            for v1, v2 in zip(values1, values2)
        ) / (len(values1) - 1)
        return round(covariance, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_percentile(
    values: List[float],
    percentile: float,
    decimals: int = 2,
) -> Optional[float]:
    try:
        if not values or percentile < 0 or percentile > 100:
            return None
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_values) - 1)
        weight = index - lower
        result = sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight
        return round(result, decimals)
    except (ValueError, TypeError):
        return None


def calculate_returns(
    prices: List[float],
    as_percent: bool = True,
    decimals: int = 4,
) -> List[Optional[float]]:
    try:
        returns = []
        for i in range(1, len(prices)):
            if prices[i - 1] <= 0:
                returns.append(None)
            else:
                ret = (prices[i] - prices[i - 1]) / prices[i - 1]
                returns.append(ret * 100 if as_percent else ret)
        return [round(r, decimals) if r is not None else None for r in returns]
    except (ValueError, TypeError, ZeroDivisionError):
        return [None] * (len(prices) - 1)


def calculate_log_returns(
    prices: List[float],
    decimals: int = 6,
) -> List[Optional[float]]:
    try:
        returns = []
        for i in range(1, len(prices)):
            if prices[i - 1] <= 0 or prices[i] <= 0:
                returns.append(None)
            else:
                ret = math.log(prices[i] / prices[i - 1])
                returns.append(round(ret, decimals))
        return returns
    except (ValueError, TypeError, ZeroDivisionError):
        return [None] * (len(prices) - 1)


def calculate_annualized_return(
    total_return: float,
    years: float,
    decimals: int = 2,
) -> Optional[float]:
    try:
        if years <= 0:
            return None
        annualized = ((1 + total_return / 100) ** (1 / years) - 1) * 100
        return round(annualized, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_treynor_ratio(
    portfolio_return: float,
    beta: float,
    risk_free_rate: float = 0.0,
    decimals: int = 2,
) -> Optional[float]:
    try:
        if beta == 0:
            return None
        excess_return = portfolio_return - risk_free_rate
        treynor = excess_return / beta
        return round(treynor, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_information_ratio(
    portfolio_returns: List[float],
    benchmark_returns: List[float],
    risk_free_rate: float = 0.0,
    decimals: int = 2,
) -> Optional[float]:
    try:
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
            return None
        active_returns = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
        tracking_error = calculate_standard_deviation(active_returns, decimals=None)
        if tracking_error is None or tracking_error == 0:
            return None
        mean_active = sum(active_returns) / len(active_returns) - risk_free_rate
        information_ratio = mean_active / tracking_error
        return round(information_ratio, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def format_financial_ratio(value: float, ratio_type: str = 'percent', decimals: int = 2) -> str:
    ratio_formatters = {
        'percent': lambda v: format_percent(v, decimals=decimals),
        'ratio': lambda v: format_ratio(v, decimals=decimals),
        'multiplier': lambda v: f'{v:.{decimals}f}x',
        'bps': lambda v: f'{v:.{decimals}f} bps',
    }
    formatter = ratio_formatters.get(ratio_type, ratio_formatters['ratio'])
    return formatter(value)


def calculate_weighted_average(
    values: List[float],
    weights: List[float],
    decimals: int = 4,
) -> Optional[float]:
    try:
        if len(values) != len(weights) or not weights:
            return None
        total_weight = sum(weights)
        if total_weight == 0:
            return None
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        return round(weighted_sum / total_weight, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_geometric_mean(
    values: List[float],
    decimals: int = 4,
) -> Optional[float]:
    try:
        if not values or any(v <= 0 for v in values):
            return None
        product = 1.0
        for v in values:
            product *= v
        n = len(values)
        geometric_mean = product ** (1 / n)
        return round(geometric_mean, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_harmonic_mean(
    values: List[float],
    decimals: int = 4,
) -> Optional[float]:
    try:
        if not values or any(v == 0 for v in values):
            return None
        n = len(values)
        reciprocal_sum = sum(1 / v for v in values)
        harmonic_mean = n / reciprocal_sum
        return round(harmonic_mean, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return None
