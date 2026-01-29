import locale
from decimal import Decimal
from typing import Optional

from utils.constants.default import DEFAULT_CURRENCY, DEFAULT_LOCALE

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CNY": "¥",
    "INR": "₹",
    "RUB": "₽",
    "KRW": "₩",
    "BRL": "R$",
    "AUD": "A$",
    "CAD": "C$",
    "CHF": "CHF ",
    "HKD": "HK$",
    "SGD": "S$",
    "NZD": "NZ$",
    "SEK": "kr",
    "NOK": "kr",
    "DKK": "kr",
    "PLN": "zł",
    "TRY": "₺",
    "ZAR": "R",
    "MXN": "$",
    "THB": "฿",
    "IDR": "Rp",
    "MYR": "RM",
    "PHP": "₱",
    "CZK": "Kč",
    "ILS": "₪",
    "CLP": "$",
    "AED": "د.إ",
    "SAR": "﷼",
    "TWD": "NT$",
    "ARS": "$",
    "EGP": "E£",
    "PKR": "₨",
    "BDT": "৳",
    "NGN": "₦",
}

LARGE_NUMBER_SUFFIXES = [
    (1e12, "T"),
    (1e9, "B"),
    (1e6, "M"),
    (1e3, "K"),
]


def format_currency(
    amount: float,
    currency_code: str = DEFAULT_CURRENCY,
    locale_str: str = DEFAULT_LOCALE,
    include_symbol: bool = True,
) -> str:
    try:
        locale.setlocale(locale.LC_ALL, locale_str)
    except locale.Error:
        locale.setlocale(locale.LC_ALL, DEFAULT_LOCALE)

    try:
        formatted = locale.currency(amount, symbol=include_symbol, grouping=True)
        return formatted
    except (ValueError, TypeError):
        symbol = CURRENCY_SYMBOLS.get(currency_code, f"{currency_code} ")
        return f"{symbol}{amount:,.2f}"


def format_number(value: float, decimals: int = 2, use_grouping: bool = True) -> str:
    try:
        return f"{value:,.{decimals}f}" if use_grouping else f"{value:.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_percent(
    value: float,
    decimals: int = 2,
    show_sign: bool = True,
    include_percent_sign: bool = True,
) -> str:
    sign = "+" if show_sign and value > 0 else ""
    percent_str = (
        f"{value:.{decimals}f}%" if include_percent_sign else f"{value:.{decimals}f}"
    )
    return f"{sign}{percent_str}"


def format_large_number(value: float, decimals: int = 1) -> str:
    try:
        abs_value = abs(value)
        for threshold, suffix in LARGE_NUMBER_SUFFIXES:
            if abs_value >= threshold:
                scaled = value / threshold
                return f"{scaled:.{decimals}f}{suffix}"
        return f"{value:,.0f}"
    except (ValueError, TypeError, ZeroDivisionError):
        return str(value)


def format_volume(value: float) -> str:
    return format_large_number(value, decimals=0)


def format_market_cap(value: float) -> str:
    return format_large_number(value, decimals=2)


def format_price(value: float, decimals: int = 2) -> str:
    return format_number(value, decimals)


def format_change(value: float, decimals: int = 2) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}"


def format_bps(value: float, decimals: int = 0) -> str:
    return f"{value:.{decimals}f} bps"


def format_ratio(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}x"


def format_multiplier(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}x"


def format_yield(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}%"


def parse_currency_string(value_str: str) -> Optional[Decimal]:
    try:
        cleaned = value_str.replace(",", "").strip()
        return Decimal(cleaned)
    except (ValueError, ArithmeticError):
        return None


def parse_percent_string(value_str: str) -> Optional[Decimal]:
    try:
        cleaned = value_str.replace("%", "").replace(",", "").strip()
        return Decimal(cleaned) / 100
    except (ValueError, ArithmeticError):
        return None


def round_to_nearest(value: float, nearest: float) -> float:
    try:
        return round(value / nearest) * nearest
    except (ValueError, TypeError, ZeroDivisionError):
        return value


def clamp_value(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def normalize_percentage(value: float) -> float:
    return clamp_value(value, 0, 1)


def calculate_percentage_change(current: float, previous: float) -> Optional[float]:
    try:
        if previous == 0:
            return None
        return (current - previous) / abs(previous)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def format_compact(value: float, decimals: int = 1) -> str:
    return format_large_number(value, decimals)


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m" if mins else f"{hours}h"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h" if hours else f"{days}d"


def get_currency_symbol(currency_code: str) -> str:
    return CURRENCY_SYMBOLS.get(currency_code.upper(), f"{currency_code} ")


def format_with_symbol(
    amount: float,
    currency_code: str = DEFAULT_CURRENCY,
    decimals: int = 2,
) -> str:
    symbol = get_currency_symbol(currency_code)
    formatted = format_number(amount, decimals)
    return f"{symbol}{formatted}"


def format_fiat_amount(
    amount: float,
    currency_code: str = DEFAULT_CURRENCY,
    locale_str: str = DEFAULT_LOCALE,
    show_symbol: bool = True,
    show_code: bool = False,
) -> str:
    if show_code:
        code = currency_code.upper()
        return f"{format_number(amount, 2)} {code}"
    return format_currency(
        amount, currency_code, locale_str, include_symbol=show_symbol
    )


def format_crypto_amount(
    amount: float,
    currency_code: str = "BTC",
    decimals: int = 8,
    show_symbol: bool = True,
) -> str:
    symbol = get_currency_symbol(currency_code) if show_symbol else ""
    formatted = format_number(amount, decimals)
    return f"{symbol}{formatted}"


def format_account_balance(
    amount: float,
    currency_code: str = DEFAULT_CURRENCY,
    locale_str: str = DEFAULT_LOCALE,
) -> str:
    sign = "-" if amount < 0 else ""
    abs_amount = abs(amount)
    return f"{sign}{format_currency(abs_amount, currency_code, locale_str)}"


def format_portfolio_value(
    value: float,
    currency_code: str = DEFAULT_CURRENCY,
    locale_str: str = DEFAULT_LOCALE,
) -> str:
    return format_currency(value, currency_code, locale_str)


def format_gain_loss(
    value: float,
    currency_code: str = DEFAULT_CURRENCY,
    locale_str: str = DEFAULT_LOCALE,
) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{format_currency(value, currency_code, locale_str)}"


def format_percentage_change(
    value: float,
    decimals: int = 2,
    include_sign: bool = True,
    include_percent: bool = True,
) -> str:
    sign = "+" if include_sign and value > 0 else ""
    percent_str = (
        f"{value:.{decimals}f}%" if include_percent else f"{value:.{decimals}f}"
    )
    return f"{sign}{percent_str}"


def format_ratio_value(
    numerator: float,
    denominator: float,
    decimals: int = 2,
) -> Optional[str]:
    try:
        if denominator == 0:
            return None
        ratio = numerator / denominator
        return f"{ratio:.{decimals}f}"
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def format_scientific_notation(value: float, decimals: int = 2) -> str:
    try:
        return f"{value:.{decimals}e}"
    except (ValueError, TypeError):
        return str(value)


def format_basis_points(value: float, decimals: int = 0) -> str:
    return f"{value:.{decimals}f} bps"


def parse_basis_points_string(value_str: str) -> Optional[float]:
    try:
        cleaned = (
            value_str.replace("bps", "")
            .replace("BP", "")
            .replace("BP", "")
            .replace(",", "")
            .strip()
        )
        return float(cleaned) / 10000
    except (ValueError, ArithmeticError):
        return None


def format_weight(value: float, decimals: int = 2) -> str:
    percent = value * 100
    return f"{percent:.{decimals}f}%"


def parse_weight_string(value_str: str) -> Optional[float]:
    try:
        cleaned = value_str.replace("%", "").replace(",", "").strip()
        return float(cleaned) / 100
    except (ValueError, ArithmeticError):
        return None
