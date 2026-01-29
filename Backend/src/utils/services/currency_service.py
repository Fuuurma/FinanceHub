from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from django.core.cache import cache

from utils.constants.default import DEFAULT_CURRENCY, DEFAULT_CACHE_TTL
from utils.services.currency_utils import (
    get_currency_data,
    get_currency_symbol,
    get_currency_name,
    get_currency_decimal_digits,
    is_valid_currency_code,
    get_all_currencies,
    get_all_fiat_currencies,
    get_all_crypto_currencies,
    format_currency_amount,
    round_to_currency_precision,
)
from utils.services.exchange_rate_fetcher import (
    get_exchange_rate_fetcher,
    fetch_exchange_rate,
    convert_currency,
    get_all_exchange_rates,
    refresh_exchange_rates_cache,
)


CURRENCY_CONVERSION_CACHE_KEY = "currency_conversion_{from}_{to}"
CONVERSION_HISTORY_CACHE_KEY = "conversion_history_{user_id}"
POPULAR_PAIRS = [
    ("USD", "EUR"),
    ("USD", "GBP"),
    ("USD", "JPY"),
    ("USD", "CNY"),
    ("USD", "INR"),
    ("EUR", "USD"),
    ("EUR", "GBP"),
    ("GBP", "USD"),
    ("GBP", "EUR"),
]


class CurrencyServiceError(Exception):
    pass


class CurrencyService:
    def __init__(self, base_currency: str = DEFAULT_CURRENCY):
        self.base_currency = base_currency.upper()
        self.exchange_fetcher = get_exchange_rate_fetcher()

    def get_exchange_rate(
        self,
        base: str,
        quote: str,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Optional[float]:
        return fetch_exchange_rate(base, quote, date, use_cache)

    def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Optional[float]:
        return convert_currency(amount, from_currency, to_currency, date, use_cache)

    def convert_with_details(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        rate = self.get_exchange_rate(from_currency, to_currency, date, use_cache)
        converted_amount = None
        if rate is not None:
            converted_amount = amount * rate
        from_data = get_currency_data(from_currency)
        to_data = get_currency_data(to_currency)
        return {
            "original_amount": amount,
            "original_currency": from_currency.upper(),
            "original_currency_name": from_data.get("name", from_currency)
            if from_data
            else from_currency,
            "original_symbol": get_currency_symbol(from_currency),
            "converted_amount": converted_amount,
            "converted_currency": to_currency.upper(),
            "converted_currency_name": to_data.get("name", to_currency)
            if to_data
            else to_currency,
            "converted_symbol": get_currency_symbol(to_currency),
            "exchange_rate": rate,
            "date": date.isoformat() if date else datetime.now().isoformat(),
        }

    def convert_multiple(
        self,
        amount: float,
        from_currency: str,
        to_currencies: List[str],
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Dict[str, float]:
        results = {}
        for to_currency in to_currencies:
            converted = self.convert(
                amount, from_currency, to_currency, date, use_cache
            )
            if converted is not None:
                results[to_currency.upper()] = converted
        return results

    def get_all_rates(
        self,
        base: Optional[str] = None,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Dict[str, float]:
        base_currency = (base or self.base_currency).upper()
        rates = get_all_exchange_rates(base_currency, date, use_cache)
        return rates or {}

    def get_popular_rates(
        self,
        base: Optional[str] = None,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Dict[str, float]:
        base_currency = (base or self.base_currency).upper()
        all_rates = self.get_all_rates(base_currency, date, use_cache)
        popular_currencies = [
            pair[1] for pair in POPULAR_PAIRS if pair[0] == base_currency
        ]
        return {
            curr: all_rates.get(curr)
            for curr in popular_currencies
            if curr in all_rates
        }

    def convert_portfolio_value(
        self,
        holdings: List[Dict[str, Any]],
        to_currency: str,
        price_field: str = "current_price",
        currency_field: str = "currency",
        use_cache: bool = True,
    ) -> float:
        total_converted = 0.0
        for holding in holdings:
            try:
                amount = float(holding.get(price_field, 0))
                from_currency = holding.get(currency_field, self.base_currency)
                converted = self.convert(
                    amount, from_currency, to_currency, None, use_cache
                )
                if converted is not None:
                    total_converted += converted
            except (ValueError, TypeError):
                continue
        return total_converted

    def get_converted_holdings(
        self,
        holdings: List[Dict[str, Any]],
        to_currency: str,
        price_field: str = "current_price",
        currency_field: str = "currency",
        quantity_field: str = "quantity",
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        converted_holdings = []
        for holding in holdings:
            try:
                quantity = float(holding.get(quantity_field, 0))
                price = float(holding.get(price_field, 0))
                from_currency = holding.get(currency_field, self.base_currency)
                converted_price = self.convert(
                    price, from_currency, to_currency, None, use_cache
                )
                if converted_price is not None:
                    converted_value = quantity * converted_price
                    converted_holdings.append(
                        {
                            **holding,
                            "converted_price": converted_price,
                            "converted_value": converted_value,
                            "converted_currency": to_currency.upper(),
                        }
                    )
            except (ValueError, TypeError):
                continue
        return converted_holdings

    def calculate_total_value(
        self,
        holdings: List[Dict[str, Any]],
        value_field: str = "current_value",
        currency_field: str = "currency",
        to_currency: Optional[str] = None,
        use_cache: bool = True,
    ) -> Tuple[float, str]:
        target_currency = (to_currency or self.base_currency).upper()
        if currency_field not in holdings[0] if holdings else False:
            total = sum(h.get(value_field, 0) for h in holdings)
            return total, target_currency
        holdings_by_currency: Dict[str, List[Dict]] = {}
        for holding in holdings:
            currency = holding.get(currency_field, self.base_currency).upper()
            if currency not in holdings_by_currency:
                holdings_by_currency[currency] = []
            holdings_by_currency[currency].append(holding)
        total_converted = 0.0
        for currency, currency_holdings in holdings_by_currency.items():
            value = sum(h.get(value_field, 0) for h in currency_holdings)
            converted = self.convert(value, currency, target_currency, None, use_cache)
            if converted is not None:
                total_converted += converted
        return total_converted, target_currency

    def format_amount(
        self,
        amount: float,
        currency: str = DEFAULT_CURRENCY,
        include_symbol: bool = True,
        include_code: bool = False,
    ) -> str:
        return format_currency_amount(amount, currency, include_symbol, include_code)

    def format_converted_amount(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        include_symbol: bool = True,
        include_code: bool = False,
        use_cache: bool = True,
    ) -> str:
        converted = self.convert(amount, from_currency, to_currency, None, use_cache)
        if converted is None:
            return f"{amount} {from_currency}"
        return self.format_amount(converted, to_currency, include_symbol, include_code)

    def round_to_precision(
        self,
        amount: float,
        currency: str,
    ) -> float:
        return round_to_currency_precision(amount, currency)

    def get_currency_info(self, currency_code: str) -> Optional[Dict[str, Any]]:
        data = get_currency_data(currency_code)
        if data:
            return {
                "code": currency_code.upper(),
                "name": data.get("name"),
                "symbol": data.get("symbol"),
                "symbol_native": data.get("symbol_native"),
                "decimal_digits": data.get("decimal_digits"),
                "type": data.get("type"),
                "countries": data.get("countries", []),
            }
        return None

    def is_available(self, currency_code: str) -> bool:
        return is_valid_currency_code(currency_code)

    def get_supported_currencies(
        self, currency_type: Optional[str] = None
    ) -> Dict[str, Dict]:
        if currency_type == "fiat":
            return get_all_fiat_currencies()
        elif currency_type == "crypto":
            return get_all_crypto_currencies()
        return get_all_currencies()

    def refresh_rates(self, base: Optional[str] = None) -> bool:
        base_currency = (base or self.base_currency).upper()
        return refresh_exchange_rates_cache(base_currency)

    def get_cross_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Optional[float]:
        if from_currency.upper() == to_currency.upper():
            return 1.0
        return self.get_exchange_rate(from_currency, to_currency, date, use_cache)

    def get_inverse_rate(
        self,
        base: str,
        quote: str,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Optional[float]:
        rate = self.get_exchange_rate(base, quote, date, use_cache)
        if rate and rate > 0:
            return 1 / rate
        return None

    def convert_range(
        self,
        from_amount: float,
        to_amount: float,
        from_currency: str,
        to_currency: str,
        steps: int = 10,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> List[Dict[str, float]]:
        rate = self.get_exchange_rate(from_currency, to_currency, date, use_cache)
        if rate is None:
            return []
        step_size = (to_amount - from_amount) / steps if steps > 1 else 0
        results = []
        for i in range(steps + 1):
            amount = from_amount + (step_size * i)
            results.append(
                {
                    "original": amount,
                    "converted": amount * rate,
                }
            )
        return results

    def get_trend(
        self,
        base: str,
        quote: str,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        from datetime import timedelta

        rates = []
        end_date = datetime.now()
        for i in range(days, -1, -1):
            date = end_date - timedelta(days=i)
            rate = self.get_exchange_rate(base, quote, date, use_cache=True)
            rates.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "rate": rate,
                }
            )
        return rates


_currency_service: Optional[CurrencyService] = None


def get_currency_service(base_currency: str = DEFAULT_CURRENCY) -> CurrencyService:
    global _currency_service
    if (
        _currency_service is None
        or _currency_service.base_currency != base_currency.upper()
    ):
        _currency_service = CurrencyService(base_currency)
    return _currency_service


def convert_currency_amount(
    amount: float,
    from_currency: str,
    to_currency: str,
    date: Optional[datetime] = None,
    use_cache: bool = True,
) -> Optional[float]:
    return get_currency_service().convert(
        amount, from_currency, to_currency, date, use_cache
    )


def get_exchange_rate_quote(
    base: str,
    quote: str,
    date: Optional[datetime] = None,
    use_cache: bool = True,
) -> Optional[float]:
    return get_currency_service().get_exchange_rate(base, quote, date, use_cache)
