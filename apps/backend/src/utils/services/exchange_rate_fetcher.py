import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List

import requests
from forex_python.converter import CurrencyRates
from django.core.cache import cache

from utils.constants.default import DEFAULT_CURRENCY, DEFAULT_CACHE_TTL

logger = logging.getLogger(__name__)

EXCHANGE_RATE_API_KEY = os.environ.get("EXCHANGERATE_API_KEY", "")
EXCHANGE_RATE_API_BASE = "https://v6.exchangerate-api.com/v6"
EXCHANGE_RATE_CACHE_KEY = "exchange_rate_{base}_{quote}_{date}"
EXCHANGE_RATE_LIST_CACHE_KEY = "exchange_rate_list_{base}_{date}"
FALLBACK_CACHE_TTL = 300
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 1


class ExchangeRateAPIError(Exception):
    pass


class ExchangeRateFetcher:
    def __init__(self):
        self.api_key = EXCHANGE_RATE_API_KEY
        self.use_api = bool(self.api_key)
        self.rates_cache: Dict[str, float] = {}
        self.cached_at: Optional[datetime] = None

    def _get_cache_key(self, base: str, quote: str, date_str: str = "latest") -> str:
        return EXCHANGE_RATE_CACHE_KEY.format(
            base=base.upper(), quote=quote.upper(), date=date_str
        )

    def _get_list_cache_key(self, base: str, date_str: str = "latest") -> str:
        return EXCHANGE_RATE_LIST_CACHE_KEY.format(base=base.upper(), date=date_str)

    def _get_cached_rate(
        self, base: str, quote: str, date_str: str = "latest"
    ) -> Optional[float]:
        cache_key = self._get_cache_key(base, quote, date_str)
        return cache.get(cache_key)

    def _set_cached_rate(
        self,
        base: str,
        quote: str,
        rate: float,
        date_str: str = "latest",
        ttl: int = DEFAULT_CACHE_TTL,
    ) -> None:
        cache_key = self._get_cache_key(base, quote, date_str)
        cache.set(cache_key, rate, ttl)

    def _get_cached_rates(
        self, base: str, date_str: str = "latest"
    ) -> Optional[Dict[str, float]]:
        cache_key = self._get_list_cache_key(base, date_str)
        return cache.get(cache_key)

    def _set_cached_rates(
        self,
        base: str,
        rates: Dict[str, float],
        date_str: str = "latest",
        ttl: int = DEFAULT_CACHE_TTL,
    ) -> None:
        cache_key = self._get_list_cache_key(base, date_str)
        cache.set(cache_key, rates, ttl)

    def fetch_exchange_rate(
        self,
        base: str = DEFAULT_CURRENCY,
        quote: str = "USD",
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Optional[float]:
        if use_cache:
            date_str = date.strftime("%Y-%m-%d") if date else "latest"
            cached_rate = self._get_cached_rate(base, quote, date_str)
            if cached_rate is not None:
                return cached_rate

        try:
            if self.use_api:
                rate = self._fetch_from_api(base, quote, date)
                if rate is not None:
                    if use_cache:
                        ttl = DEFAULT_CACHE_TTL if date is None else 86400
                        self._set_cached_rate(base, quote, rate, date_str, ttl)
                    return rate
            rate = self._fetch_from_fallback(base, quote)
            if rate is not None and use_cache:
                self._set_cached_rate(base, quote, rate, date_str, FALLBACK_CACHE_TTL)
            return rate
        except Exception as e:
            logger.error(f"Error fetching exchange rate {base}/{quote}: {e}")
            return None

    def _fetch_from_api(
        self,
        base: str = DEFAULT_CURRENCY,
        quote: str = "USD",
        date: Optional[datetime] = None,
    ) -> Optional[float]:
        if not self.api_key:
            return None
        for attempt in range(MAX_RETRIES):
            try:
                date_str = date.strftime("%Y-%m-%d") if date else "latest"
                url = f"{EXCHANGE_RATE_API_BASE}/{self.api_key}/pair/{base.upper()}/{quote.upper()}/{date_str}"
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                if data.get("result") == "success":
                    return data.get("conversion_rate")
                return None
            except (requests.RequestException, ValueError) as e:
                logger.warning(f"API attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
        return None

    def _fetch_from_fallback(
        self,
        base: str = DEFAULT_CURRENCY,
        quote: str = "USD",
    ) -> Optional[float]:
        try:
            rates = self._fetch_all_rates_fallback(base)
            if rates:
                return rates.get(quote.upper())
            return None
        except Exception as e:
            logger.error(f"Fallback rate fetch failed: {e}")
            return None

    def fetch_all_rates(
        self,
        base: str = DEFAULT_CURRENCY,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Optional[Dict[str, float]]:
        if use_cache:
            date_str = date.strftime("%Y-%m-%d") if date else "latest"
            cached_rates = self._get_cached_rates(base, date_str)
            if cached_rates is not None:
                return cached_rates

        try:
            if self.use_api:
                rates = self._fetch_all_from_api(base, date)
                if rates:
                    if use_cache:
                        ttl = DEFAULT_CACHE_TTL if date is None else 86400
                        self._set_cached_rates(base, rates, date_str, ttl)
                    return rates
            rates = self._fetch_all_rates_fallback(base)
            if rates and use_cache:
                self._set_cached_rates(base, rates, date_str, FALLBACK_CACHE_TTL)
            return rates
        except Exception as e:
            logger.error(f"Error fetching all rates for {base}: {e}")
            return None

    def _fetch_all_from_api(
        self,
        base: str = DEFAULT_CURRENCY,
        date: Optional[datetime] = None,
    ) -> Optional[Dict[str, float]]:
        if not self.api_key:
            return None
        for attempt in range(MAX_RETRIES):
            try:
                date_str = date.strftime("%Y-%m-%d") if date else "latest"
                url = f"{EXCHANGE_RATE_API_BASE}/{self.api_key}/latest/{base.upper()}"
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                if data.get("result") == "success":
                    return data.get("conversion_rates", {})
                return None
            except (requests.RequestException, ValueError) as e:
                logger.warning(f"API attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
        return None

    def _fetch_all_rates_fallback(
        self,
        base: str = DEFAULT_CURRENCY,
    ) -> Optional[Dict[str, float]]:
        try:
            c = CurrencyRates()
            rates = {}
            quote_currencies = [
                "USD",
                "EUR",
                "GBP",
                "JPY",
                "CNY",
                "INR",
                "RUB",
                "KRW",
                "BRL",
                "AUD",
                "CAD",
                "CHF",
                "HKD",
                "SGD",
                "NZD",
                "SEK",
                "NOK",
                "DKK",
                "PLN",
                "TRY",
                "ZAR",
                "MXN",
                "THB",
                "IDR",
                "MYR",
                "PHP",
                "CZK",
                "ILS",
                "CLP",
                "AED",
                "SAR",
                "TWD",
                "ARS",
                "EGP",
                "PKR",
                "BDT",
            ]
            for quote in quote_currencies:
                try:
                    rate = c.get_rate(base.upper(), quote)
                    rates[quote] = rate
                except Exception:
                    continue
            return rates if rates else None
        except Exception as e:
            logger.error(f"Fallback rates fetch failed: {e}")
            return None

    def convert_amount(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> Optional[float]:
        if from_currency.upper() == to_currency.upper():
            return amount
        rate = self.fetch_exchange_rate(from_currency, to_currency, date, use_cache)
        if rate is not None:
            return amount * rate
        return None

    def get_historical_rate(
        self,
        base: str,
        quote: str,
        date: datetime,
    ) -> Optional[float]:
        return self.fetch_exchange_rate(base, quote, date, use_cache=True)

    def get_historical_rates(
        self,
        base: str,
        quotes: List[str],
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Dict[str, float]]:
        rates_by_date = {}
        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            all_rates = self.fetch_all_rates(base, current, use_cache=True)
            if all_rates:
                rates_by_date[date_str] = {
                    q: all_rates.get(q) for q in quotes if q in all_rates
                }
            current += timedelta(days=1)
        return rates_by_date

    def is_rate_available(self, base: str, quote: str) -> bool:
        return self.fetch_exchange_rate(base, quote, use_cache=False) is not None

    def refresh_cache(self, base: str = DEFAULT_CURRENCY) -> bool:
        try:
            rates = self._fetch_all_from_api(base)
            if rates:
                self._set_cached_rates(base, rates, "latest", DEFAULT_CACHE_TTL)
                return True
            return False
        except Exception as e:
            logger.error(f"Error refreshing cache: {e}")
            return False


_exchange_rate_fetcher: Optional[ExchangeRateFetcher] = None


def get_exchange_rate_fetcher() -> ExchangeRateFetcher:
    global _exchange_rate_fetcher
    if _exchange_rate_fetcher is None:
        _exchange_rate_fetcher = ExchangeRateFetcher()
    return _exchange_rate_fetcher


def fetch_exchange_rate(
    base: str = DEFAULT_CURRENCY,
    quote: str = "USD",
    date: Optional[datetime] = None,
    use_cache: bool = True,
) -> Optional[float]:
    return get_exchange_rate_fetcher().fetch_exchange_rate(base, quote, date, use_cache)


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    date: Optional[datetime] = None,
    use_cache: bool = True,
) -> Optional[float]:
    return get_exchange_rate_fetcher().convert_amount(
        amount, from_currency, to_currency, date, use_cache
    )


def get_all_exchange_rates(
    base: str = DEFAULT_CURRENCY,
    date: Optional[datetime] = None,
    use_cache: bool = True,
) -> Optional[Dict[str, float]]:
    return get_exchange_rate_fetcher().fetch_all_rates(base, date, use_cache)


def refresh_exchange_rates_cache(base: str = DEFAULT_CURRENCY) -> bool:
    return get_exchange_rate_fetcher().refresh_cache(base)
