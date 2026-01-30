from typing import Dict, List, Optional, Any

from utils.constants.default import DEFAULT_CURRENCY

CURRENCY_DATA = {
    "USD": {
        "name": "US Dollar",
        "symbol": "$",
        "symbol_native": "$",
        "decimal_digits": 2,
        "code": "USD",
        "name_plural": "US dollars",
        "type": "fiat",
        "countries": ["US", "EI", "TL", "VU", "ZW"],
    },
    "EUR": {
        "name": "Euro",
        "symbol": "€",
        "symbol_native": "€",
        "decimal_digits": 2,
        "code": "EUR",
        "name_plural": "euros",
        "type": "fiat",
        "countries": [
            "AT",
            "BE",
            "CY",
            "EE",
            "FI",
            "FR",
            "DE",
            "GR",
            "IE",
            "IT",
            "LV",
            "LT",
            "LU",
            "MT",
            "NL",
            "PT",
            "SK",
            "SI",
            "ES",
            "AD",
            "SM",
            "VA",
            "ME",
            "XK",
            "MK",
            "AL",
        ],
    },
    "GBP": {
        "name": "British Pound Sterling",
        "symbol": "£",
        "symbol_native": "£",
        "decimal_digits": 2,
        "code": "GBP",
        "name_plural": "British pounds sterling",
        "type": "fiat",
        "countries": ["GB", "IM", "GG", "JE", "GS"],
    },
    "JPY": {
        "name": "Japanese Yen",
        "symbol": "¥",
        "symbol_native": "￥",
        "decimal_digits": 0,
        "code": "JPY",
        "name_plural": "Japanese yen",
        "type": "fiat",
        "countries": ["JP"],
    },
    "CNY": {
        "name": "Chinese Yuan",
        "symbol": "¥",
        "symbol_native": "￥",
        "decimal_digits": 2,
        "code": "CNY",
        "name_plural": "Chinese yuan",
        "type": "fiat",
        "countries": ["CN", "HK", "MO"],
    },
    "INR": {
        "name": "Indian Rupee",
        "symbol": "₹",
        "symbol_native": "₹",
        "decimal_digits": 2,
        "code": "INR",
        "name_plural": "Indian rupees",
        "type": "fiat",
        "countries": ["IN"],
    },
    "RUB": {
        "name": "Russian Ruble",
        "symbol": "₽",
        "symbol_native": "₽",
        "decimal_digits": 2,
        "code": "RUB",
        "name_plural": "Russian rubles",
        "type": "fiat",
        "countries": ["RU", "AB"],
    },
    "KRW": {
        "name": "South Korean Won",
        "symbol": "₩",
        "symbol_native": "₩",
        "decimal_digits": 0,
        "code": "KRW",
        "name_plural": "South Korean won",
        "type": "fiat",
        "countries": ["KR"],
    },
    "BRL": {
        "name": "Brazilian Real",
        "symbol": "R$",
        "symbol_native": "R$",
        "decimal_digits": 2,
        "code": "BRL",
        "name_plural": "Brazilian reals",
        "type": "fiat",
        "countries": ["BR"],
    },
    "AUD": {
        "name": "Australian Dollar",
        "symbol": "A$",
        "symbol_native": "$",
        "decimal_digits": 2,
        "code": "AUD",
        "name_plural": "Australian dollars",
        "type": "fiat",
        "countries": ["AU", "CX", "CC", "HM", "KI", "NR", "NF", "TV"],
    },
    "CAD": {
        "name": "Canadian Dollar",
        "symbol": "C$",
        "symbol_native": "$",
        "decimal_digits": 2,
        "code": "CAD",
        "name_plural": "Canadian dollars",
        "type": "fiat",
        "countries": ["CA"],
    },
    "CHF": {
        "name": "Swiss Franc",
        "symbol": "CHF",
        "symbol_native": "CHF",
        "decimal_digits": 2,
        "code": "CHF",
        "name_plural": "Swiss francs",
        "type": "fiat",
        "countries": ["CH", "LI"],
    },
    "HKD": {
        "name": "Hong Kong Dollar",
        "symbol": "HK$",
        "symbol_native": "$",
        "decimal_digits": 2,
        "code": "HKD",
        "name_plural": "Hong Kong dollars",
        "type": "fiat",
        "countries": ["HK"],
    },
    "SGD": {
        "name": "Singapore Dollar",
        "symbol": "S$",
        "symbol_native": "$",
        "decimal_digits": 2,
        "code": "SGD",
        "name_plural": "Singapore dollars",
        "type": "fiat",
        "countries": ["SG"],
    },
    "NZD": {
        "name": "New Zealand Dollar",
        "symbol": "NZ$",
        "symbol_native": "$",
        "decimal_digits": 2,
        "code": "NZD",
        "name_plural": "New Zealand dollars",
        "type": "fiat",
        "countries": ["NZ", "CK", "NU", "PN", "TK"],
    },
    "SEK": {
        "name": "Swedish Krona",
        "symbol": "kr",
        "symbol_native": "kr",
        "decimal_digits": 2,
        "code": "SEK",
        "name_plural": "Swedish kronor",
        "type": "fiat",
        "countries": ["SE"],
    },
    "NOK": {
        "name": "Norwegian Krone",
        "symbol": "kr",
        "symbol_native": "kr",
        "decimal_digits": 2,
        "code": "NOK",
        "name_plural": "Norwegian kroner",
        "type": "fiat",
        "countries": ["NO", "SJ", "BV"],
    },
    "DKK": {
        "name": "Danish Krone",
        "symbol": "kr",
        "symbol_native": "kr",
        "decimal_digits": 2,
        "code": "DKK",
        "name_plural": "Danish kroner",
        "type": "fiat",
        "countries": ["DK", "FO", "GL"],
    },
    "PLN": {
        "name": "Polish Zloty",
        "symbol": "zł",
        "symbol_native": "zł",
        "decimal_digits": 2,
        "code": "PLN",
        "name_plural": "Polish zlotys",
        "type": "fiat",
        "countries": ["PL"],
    },
    "TRY": {
        "name": "Turkish Lira",
        "symbol": "₺",
        "symbol_native": "₺",
        "decimal_digits": 2,
        "code": "TRY",
        "name_plural": "Turkish Lira",
        "type": "fiat",
        "countries": ["TR"],
    },
    "ZAR": {
        "name": "South African Rand",
        "symbol": "R",
        "symbol_native": "R",
        "decimal_digits": 2,
        "code": "ZAR",
        "name_plural": "South African rand",
        "type": "fiat",
        "countries": ["ZA"],
    },
    "MXN": {
        "name": "Mexican Peso",
        "symbol": "$",
        "symbol_native": "$",
        "decimal_digits": 2,
        "code": "MXN",
        "name_plural": "Mexican pesos",
        "type": "fiat",
        "countries": ["MX"],
    },
    "THB": {
        "name": "Thai Baht",
        "symbol": "฿",
        "symbol_native": "฿",
        "decimal_digits": 2,
        "code": "THB",
        "name_plural": "Thai baht",
        "type": "fiat",
        "countries": ["TH"],
    },
    "IDR": {
        "name": "Indonesian Rupiah",
        "symbol": "Rp",
        "symbol_native": "Rp",
        "decimal_digits": 0,
        "code": "IDR",
        "name_plural": "Indonesian rupiahs",
        "type": "fiat",
        "countries": ["ID"],
    },
    "MYR": {
        "name": "Malaysian Ringgit",
        "symbol": "RM",
        "symbol_native": "RM",
        "decimal_digits": 2,
        "code": "MYR",
        "name_plural": "Malaysian ringgits",
        "type": "fiat",
        "countries": ["MY"],
    },
    "PHP": {
        "name": "Philippine Peso",
        "symbol": "₱",
        "symbol_native": "₱",
        "decimal_digits": 2,
        "code": "PHP",
        "name_plural": "Philippine pesos",
        "type": "fiat",
        "countries": ["PH"],
    },
    "CZK": {
        "name": "Czech Republic Koruna",
        "symbol": "Kč",
        "symbol_native": "Kč",
        "decimal_digits": 2,
        "code": "CZK",
        "name_plural": "Czech Republic korunas",
        "type": "fiat",
        "countries": ["CZ"],
    },
    "ILS": {
        "name": "Israeli New Sheqel",
        "symbol": "₪",
        "symbol_native": "₪",
        "decimal_digits": 2,
        "code": "ILS",
        "name_plural": "Israeli new sheqels",
        "type": "fiat",
        "countries": ["IL", "PS"],
    },
    "CLP": {
        "name": "Chilean Peso",
        "symbol": "$",
        "symbol_native": "$",
        "decimal_digits": 0,
        "code": "CLP",
        "name_plural": "Chilean pesos",
        "type": "fiat",
        "countries": ["CL"],
    },
    "AED": {
        "name": "United Arab Emirates Dirham",
        "symbol": "د.إ",
        "symbol_native": "د.إ",
        "decimal_digits": 2,
        "code": "AED",
        "name_plural": "UAE dirhams",
        "type": "fiat",
        "countries": ["AE"],
    },
    "SAR": {
        "name": "Saudi Riyal",
        "symbol": "﷼",
        "symbol_native": "﷼",
        "decimal_digits": 2,
        "code": "SAR",
        "name_plural": "Saudi riyals",
        "type": "fiat",
        "countries": ["SA"],
    },
    "TWD": {
        "name": "New Taiwan Dollar",
        "symbol": "NT$",
        "symbol_native": "$",
        "decimal_digits": 2,
        "code": "TWD",
        "name_plural": "New Taiwan dollars",
        "type": "fiat",
        "countries": ["TW"],
    },
    "ARS": {
        "name": "Argentine Peso",
        "symbol": "$",
        "symbol_native": "$",
        "decimal_digits": 2,
        "code": "ARS",
        "name_plural": "Argentine pesos",
        "type": "fiat",
        "countries": ["AR"],
    },
    "EGP": {
        "name": "Egyptian Pound",
        "symbol": "E£",
        "symbol_native": "E£",
        "decimal_digits": 2,
        "code": "EGP",
        "name_plural": "Egyptian pounds",
        "type": "fiat",
        "countries": ["EG"],
    },
    "PKR": {
        "name": "Pakistani Rupee",
        "symbol": "₨",
        "symbol_native": "₨",
        "decimal_digits": 2,
        "code": "PKR",
        "name_plural": "Pakistani rupees",
        "type": "fiat",
        "countries": ["PK"],
    },
    "BDT": {
        "name": "Bangladeshi Taka",
        "symbol": "৳",
        "symbol_native": "৳",
        "decimal_digits": 2,
        "code": "BDT",
        "name_plural": "Bangladeshi takas",
        "type": "fiat",
        "countries": ["BD"],
    },
    "NGN": {
        "name": "Nigerian Naira",
        "symbol": "₦",
        "symbol_native": "₦",
        "decimal_digits": 2,
        "code": "NGN",
        "name_plural": "Nigerian nairas",
        "type": "fiat",
        "countries": ["NG"],
    },
    "UAH": {
        "name": "Ukrainian Hryvnia",
        "symbol": "₴",
        "symbol_native": "₴",
        "decimal_digits": 2,
        "code": "UAH",
        "name_plural": "Ukrainian hryvnias",
        "type": "fiat",
        "countries": ["UA"],
    },
    "VND": {
        "name": "Vietnamese Dong",
        "symbol": "₫",
        "symbol_native": "₫",
        "decimal_digits": 0,
        "code": "VND",
        "name_plural": "Vietnamese dong",
        "type": "fiat",
        "countries": ["VN"],
    },
    "BTC": {
        "name": "Bitcoin",
        "symbol": "BTC",
        "symbol_native": "BTC",
        "decimal_digits": 8,
        "code": "BTC",
        "name_plural": "Bitcoins",
        "type": "crypto",
        "countries": [],
    },
    "ETH": {
        "name": "Ethereum",
        "symbol": "ETH",
        "symbol_native": "ETH",
        "decimal_digits": 18,
        "code": "ETH",
        "name_plural": "Ethereum",
        "type": "crypto",
        "countries": [],
    },
    "USDT": {
        "name": "Tether",
        "symbol": "USDT",
        "symbol_native": "USDT",
        "decimal_digits": 2,
        "code": "USDT",
        "name_plural": "Tether",
        "type": "crypto",
        "countries": [],
    },
    "BNB": {
        "name": "Binance Coin",
        "symbol": "BNB",
        "symbol_native": "BNB",
        "decimal_digits": 8,
        "code": "BNB",
        "name_plural": "Binance Coin",
        "type": "crypto",
        "countries": [],
    },
    "SOL": {
        "name": "Solana",
        "symbol": "SOL",
        "symbol_native": "SOL",
        "decimal_digits": 9,
        "code": "SOL",
        "name_plural": "Solana",
        "type": "crypto",
        "countries": [],
    },
    "XRP": {
        "name": "Ripple",
        "symbol": "XRP",
        "symbol_native": "XRP",
        "decimal_digits": 6,
        "code": "XRP",
        "name_plural": "Ripple",
        "type": "crypto",
        "countries": [],
    },
    "USDC": {
        "name": "USD Coin",
        "symbol": "USDC",
        "symbol_native": "USDC",
        "decimal_digits": 2,
        "code": "USDC",
        "name_plural": "USD Coin",
        "type": "crypto",
        "countries": [],
    },
    "ADA": {
        "name": "Cardano",
        "symbol": "ADA",
        "symbol_native": "ADA",
        "decimal_digits": 6,
        "code": "ADA",
        "name_plural": "Cardano",
        "type": "crypto",
        "countries": [],
    },
    "AVAX": {
        "name": "Avalanche",
        "symbol": "AVAX",
        "symbol_native": "AVAX",
        "decimal_digits": 9,
        "code": "AVAX",
        "name_plural": "Avalanche",
        "type": "crypto",
        "countries": [],
    },
    "DOGE": {
        "name": "Dogecoin",
        "symbol": "DOGE",
        "symbol_native": "DOGE",
        "decimal_digits": 8,
        "code": "DOGE",
        "name_plural": "Dogecoin",
        "type": "crypto",
        "countries": [],
    },
    "DOT": {
        "name": "Polkadot",
        "symbol": "DOT",
        "symbol_native": "DOT",
        "decimal_digits": 10,
        "code": "DOT",
        "name_plural": "Polkadot",
        "type": "crypto",
        "countries": [],
    },
    "MATIC": {
        "name": "Polygon",
        "symbol": "MATIC",
        "symbol_native": "MATIC",
        "decimal_digits": 18,
        "code": "MATIC",
        "name_plural": "Polygon",
        "type": "crypto",
        "countries": [],
    },
    "LTC": {
        "name": "Litecoin",
        "symbol": "LTC",
        "symbol_native": "LTC",
        "decimal_digits": 8,
        "code": "LTC",
        "name_plural": "Litecoin",
        "type": "crypto",
        "countries": [],
    },
    "LINK": {
        "name": "Chainlink",
        "symbol": "LINK",
        "symbol_native": "LINK",
        "decimal_digits": 18,
        "code": "LINK",
        "name_plural": "Chainlink",
        "type": "crypto",
        "countries": [],
    },
    "ATOM": {
        "name": "Cosmos",
        "symbol": "ATOM",
        "symbol_native": "ATOM",
        "decimal_digits": 6,
        "code": "ATOM",
        "name_plural": "Cosmos",
        "type": "crypto",
        "countries": [],
    },
    "UNI": {
        "name": "Uniswap",
        "symbol": "UNI",
        "symbol_native": "UNI",
        "decimal_digits": 18,
        "code": "UNI",
        "name_plural": "Uniswap",
        "type": "crypto",
        "countries": [],
    },
}

FIAT_CURRENCIES = {k: v for k, v in CURRENCY_DATA.items() if v["type"] == "fiat"}
CRYPTO_CURRENCIES = {k: v for k, v in CURRENCY_DATA.items() if v["type"] == "crypto"}
ALL_CURRENCIES = list(CURRENCY_DATA.keys())


def get_currency_data(currency_code: str) -> Optional[Dict[str, Any]]:
    return CURRENCY_DATA.get(currency_code.upper())


def get_currency_symbol(currency_code: str) -> str:
    data = get_currency_data(currency_code)
    if data:
        return data.get("symbol", f"{currency_code} ")
    return f"{currency_code} "


def get_currency_symbol_native(currency_code: str) -> str:
    data = get_currency_data(currency_code)
    if data:
        return data.get("symbol_native", data.get("symbol", f"{currency_code} "))
    return f"{currency_code} "


def get_currency_name(currency_code: str) -> str:
    data = get_currency_data(currency_code)
    if data:
        return data.get("name", currency_code)
    return currency_code


def get_currency_decimal_digits(currency_code: str) -> int:
    data = get_currency_data(currency_code)
    if data:
        return data.get("decimal_digits", 2)
    return 2


def get_currency_countries(currency_code: str) -> List[str]:
    data = get_currency_data(currency_code)
    if data:
        return data.get("countries", [])
    return []


def is_fiat_currency(currency_code: str) -> bool:
    data = get_currency_data(currency_code)
    if data:
        return data.get("type") == "fiat"
    return False


def is_crypto_currency(currency_code: str) -> bool:
    data = get_currency_data(currency_code)
    if data:
        return data.get("type") == "crypto"
    return False


def is_valid_currency_code(currency_code: str) -> bool:
    return currency_code.upper() in CURRENCY_DATA


def get_all_fiat_currencies() -> Dict[str, Dict[str, Any]]:
    return FIAT_CURRENCIES.copy()


def get_all_crypto_currencies() -> Dict[str, Dict[str, Any]]:
    return CRYPTO_CURRENCIES.copy()


def get_all_currencies() -> Dict[str, Dict[str, Any]]:
    return CURRENCY_DATA.copy()


def search_currencies_by_country(country_code: str) -> List[Dict[str, Any]]:
    results = []
    for code, data in CURRENCY_DATA.items():
        if country_code.upper() in data.get("countries", []):
            results.append({"code": code, **data})
    return results


def search_currencies_by_name(name_part: str) -> List[Dict[str, Any]]:
    name_lower = name_part.lower()
    results = []
    for code, data in CURRENCY_DATA.items():
        if (
            name_lower in data.get("name", "").lower()
            or name_lower in data.get("code", "").lower()
        ):
            results.append({"code": code, **data})
    return results


def get_popular_currencies() -> List[str]:
    return [
        "USD",
        "EUR",
        "GBP",
        "JPY",
        "CNY",
        "INR",
        "CHF",
        "CAD",
        "AUD",
        "HKD",
        "SGD",
        "NZD",
    ]


def get_default_currency_for_country(country_code: str) -> str:
    country_currencies = search_currencies_by_country(country_code)
    if country_currencies:
        return country_currencies[0]["code"]
    return DEFAULT_CURRENCY


def format_currency_amount(
    amount: float,
    currency_code: str = DEFAULT_CURRENCY,
    include_symbol: bool = True,
    include_code: bool = False,
) -> str:
    data = get_currency_data(currency_code)
    if not data:
        return f"{amount:,.2f} {currency_code}"
    decimals = data.get("decimal_digits", 2)
    symbol = data.get("symbol", f"{currency_code} ")
    formatted_amount = f"{amount:,.{decimals}f}"
    if include_code:
        return f"{formatted_amount} {currency_code}"
    if include_symbol:
        return f"{symbol}{formatted_amount}"
    return formatted_amount


def round_to_currency_precision(amount: float, currency_code: str) -> float:
    decimals = get_currency_decimal_digits(currency_code)
    factor = 10**decimals
    return round(amount * factor) / factor
