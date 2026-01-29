from datetime import datetime
from typing import List, Optional

from ninja import Router, Query
from pydantic import BaseModel, Field

from utils.constants.default import DEFAULT_CURRENCY
from utils.services.currency_service import get_currency_service, CurrencyService
from utils.services.currency_utils import (
    get_all_currencies,
    get_all_fiat_currencies,
    get_all_crypto_currencies,
    get_currency_data,
    is_valid_currency_code,
    get_currency_symbol,
)
from utils.services.number_utils import format_currency, format_percent


router = Router()


class ExchangeRateResponse(BaseModel):
    base: str
    quote: str
    rate: Optional[float]
    timestamp: str


class ConvertRequest(BaseModel):
    amount: float
    from_currency: str = Field(..., max_length=3, min_length=3)
    to_currency: str = Field(..., max_length=3, min_length=3)
    date: Optional[str] = None


class ConvertResponse(BaseModel):
    original_amount: float
    original_currency: str
    converted_amount: Optional[float]
    converted_currency: str
    exchange_rate: Optional[float]
    formatted_original: str
    formatted_converted: Optional[str]


class AllRatesResponse(BaseModel):
    base: str
    rates: dict
    timestamp: str


class CurrencyInfoResponse(BaseModel):
    code: str
    name: str
    symbol: str
    symbol_native: str
    decimal_digits: int
    type: str
    countries: List[str]


class CurrencyListResponse(BaseModel):
    currencies: List[CurrencyInfoResponse]
    total_count: int


class ConvertMultipleRequest(BaseModel):
    amount: float
    from_currency: str = Field(..., max_length=3, min_length=3)
    to_currencies: List[str] = Field(..., min_items=1, max_items=50)


class ConvertMultipleResponse(BaseModel):
    original_amount: float
    original_currency: str
    conversions: dict


class CrossRateRequest(BaseModel):
    from_currency: str = Field(..., max_length=3, min_length=3)
    to_currency: str = Field(..., max_length=3, min_length=3)


class CrossRateResponse(BaseModel):
    from_currency: str
    to_currency: str
    rate: Optional[float]
    inverse_rate: Optional[float]


class TrendRequest(BaseModel):
    base_currency: str = Field(default=DEFAULT_CURRENCY, max_length=3, min_length=3)
    quote_currency: str = Field(..., max_length=3, min_length=3)
    days: int = Field(default=30, ge=1, le=365)


class TrendPoint(BaseModel):
    date: str
    rate: Optional[float]


class TrendResponse(BaseModel):
    base: str
    quote: str
    days: int
    data: List[TrendPoint]


@router.get("/rates/{base}/{quote}", response=ExchangeRateResponse)
def get_exchange_rate(request, base: str, quote: str):
    service = get_currency_service()
    rate = service.get_exchange_rate(base, quote)
    return {
        "base": base.upper(),
        "quote": quote.upper(),
        "rate": rate,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/convert", response=ConvertResponse)
def convert_currency(request, data: ConvertRequest):
    service = get_currency_service()
    date = datetime.strptime(data.date, "%Y-%m-%d") if data.date else None
    converted = service.convert(data.amount, data.from_currency, data.to_currency, date)
    formatted_original = format_currency(data.amount, data.from_currency)
    formatted_converted = (
        format_currency(converted, data.to_currency) if converted else None
    )
    return {
        "original_amount": data.amount,
        "original_currency": data.from_currency.upper(),
        "converted_amount": converted,
        "converted_currency": data.to_currency.upper(),
        "exchange_rate": service.get_exchange_rate(
            data.from_currency, data.to_currency, date
        ),
        "formatted_original": formatted_original,
        "formatted_converted": formatted_converted,
    }


@router.get("/rates/{base}", response=AllRatesResponse)
def get_all_rates(request, base: str):
    service = get_currency_service()
    rates = service.get_all_rates(base)
    return {
        "base": base.upper(),
        "rates": rates,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/currencies", response=CurrencyListResponse)
def list_currencies(request, type: Optional[str] = None):
    if type == "fiat":
        currencies = get_all_fiat_currencies()
    elif type == "crypto":
        currencies = get_all_crypto_currencies()
    else:
        currencies = get_all_currencies()
    result = [
        {
            "code": code,
            "name": data.get("name", code),
            "symbol": data.get("symbol", f"{code} "),
            "symbol_native": data.get("symbol_native", data.get("symbol", f"{code} ")),
            "decimal_digits": data.get("decimal_digits", 2),
            "type": data.get("type", "fiat"),
            "countries": data.get("countries", []),
        }
        for code, data in currencies.items()
    ]
    return {
        "currencies": result,
        "total_count": len(result),
    }


@router.get("/currencies/{code}", response=CurrencyInfoResponse)
def get_currency_info(request, code: str):
    data = get_currency_data(code)
    if not data:
        return {"error": "Currency not found"}, 404
    return {
        "code": code.upper(),
        "name": data.get("name", code),
        "symbol": data.get("symbol", f"{code} "),
        "symbol_native": data.get("symbol_native", data.get("symbol", f"{code} ")),
        "decimal_digits": data.get("decimal_digits", 2),
        "type": data.get("type", "fiat"),
        "countries": data.get("countries", []),
    }


@router.post("/convert-multiple", response=ConvertMultipleResponse)
def convert_multiple(request, data: ConvertMultipleRequest):
    service = get_currency_service()
    conversions = service.convert_multiple(
        data.amount, data.from_currency, data.to_currencies
    )
    return {
        "original_amount": data.amount,
        "original_currency": data.from_currency.upper(),
        "conversions": conversions,
    }


@router.post("/cross-rate", response=CrossRateResponse)
def get_cross_rate(request, data: CrossRateRequest):
    service = get_currency_service()
    rate = service.get_cross_rate(data.from_currency, data.to_currency)
    inverse_rate = service.get_inverse_rate(data.from_currency, data.to_currency)
    return {
        "from_currency": data.from_currency.upper(),
        "to_currency": data.to_currency.upper(),
        "rate": rate,
        "inverse_rate": inverse_rate,
    }


@router.get("/trend", response=TrendResponse)
def get_rate_trend(
    request,
    base: str = DEFAULT_CURRENCY,
    quote: str = "USD",
    days: int = 30,
):
    service = get_currency_service()
    trend_data = service.get_trend(base, quote, days)
    return {
        "base": base.upper(),
        "quote": quote.upper(),
        "days": days,
        "data": [
            {"date": point["date"], "rate": point["rate"]} for point in trend_data
        ],
    }


@router.get("/popular")
def get_popular_rates(request, base: str = DEFAULT_CURRENCY):
    service = get_currency_service()
    popular_rates = service.get_popular_rates(base)
    return {
        "base": base.upper(),
        "rates": popular_rates,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/refresh")
def refresh_rates(request, base: str = DEFAULT_CURRENCY):
    success = get_currency_service().refresh_rates(base)
    return {
        "success": success,
        "base": base.upper(),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/check/{from_currency}/{to_currency}")
def check_rate_availability(request, from_currency: str, to_currency: str):
    available = is_valid_currency_code(from_currency) and is_valid_currency_code(
        to_currency
    )
    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "available": available,
    }
