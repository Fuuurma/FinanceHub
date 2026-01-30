import re
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone_number(phone: str) -> bool:
    pattern = r"^\+?[1-9]\d{6,14}$"
    return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))


def validate_isin(isin: str) -> bool:
    if not re.match(r"^[A-Z]{2}[A-Z0-9]{9}\d$", isin):
        return False
    alphanumeric = isin[2:] + str(ord(isin[0]) - 55) + str(ord(isin[1]) - 55)
    digits = "".join(str(ord(c) - 55) if c.isalpha() else c for c in alphanumeric)
    total = sum(
        int(d) * (10**i) if i % 2 == 0 else int(d) * 2 * (10 ** (i - 1))
        for i, d in enumerate(reversed(digits))
    )
    return total % 10 == 0


def validate_cusip(cusip: str) -> bool:
    if len(cusip) != 9:
        return False
    alphanumeric = cusip[:6] + cusip[7]
    digits = ""
    for char in alphanumeric:
        if char.isdigit():
            digits += char
        elif char.isalpha():
            val = ord(char.upper()) - 55
            if val > 9:
                digits += str(val // 10) + str(val % 10)
            else:
                digits += str(val)
        else:
            return False
    try:
        checksum = int(cusip[8])
        total = sum(int(d) for d in digits)
        calculated = (10 - (total % 10)) % 10
        return checksum == calculated
    except (ValueError, IndexError):
        return False


def validate_ticker(ticker: str, exchange: Optional[str] = None) -> bool:
    pattern = r"^[A-Z]{1,5}(\.[A-Z])?$"
    if not re.match(pattern, ticker.upper()):
        return False
    if exchange:
        exchange_tickers = {
            "NYSE": ["A", "AA", "AAA", "AAPL"],
            "NASDAQ": ["AAPL", "GOOGL", "MSFT", "TSLA"],
            "LSE": ["AAL", "ABF", "ADM", "AAL"],
        }
        return ticker.upper() in exchange_tickers.get(exchange, [])
    return True


def validate_url(url: str) -> bool:
    pattern = r"^https?:\/\/[\w\-]+(\.[\w\-]+)+[\w\-.,@?^=%&:/~+#]*$"
    return bool(re.match(pattern, url))


def validate_ip_address(ip: str) -> bool:
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    octets = ip.split(".")
    return all(0 <= int(o) <= 255 for o in octets)


def validate_credit_card(card_number: str) -> bool:
    digits = card_number.replace(" ", "").replace("-", "")
    if not digits.isdigit() or len(digits) not in [13, 15, 16, 19]:
        return False
    total = 0
    is_second = False
    for digit in reversed(digits):
        d = int(digit)
        if is_second:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        is_second = not is_second
    return total % 10 == 0


def validate_password_strength(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digits: bool = True,
    require_special: bool = True,
) -> Dict[str, Any]:
    result = {
        "is_valid": True,
        "errors": [],
        "score": 0,
    }
    if len(password) < min_length:
        result["is_valid"] = False
        result["errors"].append(f"Password must be at least {min_length} characters")
    else:
        result["score"] += 1
    if require_uppercase and not re.search(r"[A-Z]", password):
        result["is_valid"] = False
        result["errors"].append("Password must contain at least one uppercase letter")
    else:
        result["score"] += 1
    if require_lowercase and not re.search(r"[a-z]", password):
        result["is_valid"] = False
        result["errors"].append("Password must contain at least one lowercase letter")
    else:
        result["score"] += 1
    if require_digits and not re.search(r"\d", password):
        result["is_valid"] = False
        result["errors"].append("Password must contain at least one digit")
    else:
        result["score"] += 1
    if require_special and not re.search(
        r'[!@#$%^&*()_+\-=\[\]{};\'\\|:",.<>?]', password
    ):
        result["is_valid"] = False
        result["errors"].append("Password must contain at least one special character")
    else:
        result["score"] += 1
    return result


def validate_date(
    date_str: str,
    format_str: str = "%Y-%m-%d",
    min_date: Optional[datetime] = None,
    max_date: Optional[datetime] = None,
) -> Tuple[bool, Optional[str]]:
    try:
        date = datetime.strptime(date_str, format_str)
        if min_date and date < min_date:
            return False, f"Date must be on or after {min_date.strftime(format_str)}"
        if max_date and date > max_date:
            return False, f"Date must be on or before {max_date.strftime(format_str)}"
        return True, None
    except ValueError:
        return False, f"Invalid date format. Expected {format_str}"


def validate_amount(
    amount: float,
    min_amount: float = 0.0,
    max_amount: Optional[float] = None,
    allow_zero: bool = False,
) -> Tuple[bool, Optional[str]]:
    if allow_zero and amount == 0:
        return True, None
    if amount < min_amount:
        return False, f"Amount must be at least {min_amount}"
    if max_amount is not None and amount > max_amount:
        return False, f"Amount must not exceed {max_amount}"
    return True, None


def validate_quantity(
    quantity: float,
    min_quantity: float = 0.000001,
    max_quantity: Optional[float] = None,
    allow_fractional: bool = True,
) -> Tuple[bool, Optional[str]]:
    if quantity < min_quantity:
        return False, f"Quantity must be at least {min_quantity}"
    if max_quantity is not None and quantity > max_quantity:
        return False, f"Quantity must not exceed {max_quantity}"
    if not allow_fractional and not quantity.is_integer():
        return False, "Quantity must be a whole number"
    return True, None


def validate_symbol(symbol: str) -> bool:
    return bool(re.match(r"^[A-Z]{1,5}(\.[A-Z])?$", symbol.upper()))


def validate_percentage(
    percentage: float, allow_negative: bool = False
) -> Tuple[bool, Optional[str]]:
    if not allow_negative and percentage < 0:
        return False, "Percentage cannot be negative"
    if percentage > 100:
        return False, "Percentage cannot exceed 100"
    return True, None


def validate_uuid(uuid_string: str) -> bool:
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(pattern, uuid_string.lower()))


def validate_hex_color(hex_color: str) -> bool:
    return bool(re.match(r"^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", hex_color))


def validate_slug(slug: str) -> bool:
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def validate_mac_address(mac: str) -> bool:
    pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return bool(re.match(pattern, mac))


def validate_iban(iban: str) -> bool:
    iban = iban.replace(" ", "").upper()
    if not re.match(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}$", iban):
        return False
    rearranged = iban[4:] + iban[:4]
    digits = ""
    for char in rearranged:
        if char.isalpha():
            digits += str(ord(char) - 55)
        else:
            digits += char
    return int(digits) % 97 == 1


def validate_bic(bic: str) -> bool:
    return bool(re.match(r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$", bic.upper()))


def sanitize_string(
    text: str,
    max_length: Optional[int] = None,
    allowed_chars: Optional[str] = None,
    remove_html: bool = True,
) -> str:
    if remove_html:
        text = re.sub(r"<[^>]+>", "", text)
    if allowed_chars:
        text = "".join(c for c in text if c in allowed_chars)
    if max_length:
        text = text[:max_length]
    return text.strip()


def sanitize_email(email: str) -> Optional[str]:
    email = email.strip().lower()
    if validate_email(email):
        return email
    return None


def sanitize_ticker(ticker: str) -> Optional[str]:
    ticker = ticker.strip().upper()
    if validate_symbol(ticker):
        return ticker
    return None


def sanitize_amount(amount_str: str) -> Optional[float]:
    try:
        cleaned = amount_str.replace(",", "").replace(" ", "")
        amount = float(cleaned)
        is_valid, _ = validate_amount(amount)
        if is_valid:
            return amount
        return None
    except (ValueError, TypeError):
        return None


def get_validation_errors(
    data: Dict[str, Any], rules: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    errors = {}
    for field, field_rules in rules.items():
        value = data.get(field)
        for rule in field_rules:
            if rule == "required" and (value is None or value == ""):
                if field not in errors:
                    errors[field] = []
                errors[field].append(f"{field} is required")
            elif rule == "email" and value and not validate_email(str(value)):
                if field not in errors:
                    errors[field] = []
                errors[field].append(f"{field} must be a valid email")
            elif rule == "ticker" and value and not validate_symbol(str(value)):
                if field not in errors:
                    errors[field] = []
                errors[field].append(f"{field} must be a valid ticker symbol")
            elif rule.startswith("min_"):
                try:
                    min_val = float(rule.split("_")[1])
                    is_valid, _ = validate_amount(float(value), min_amount=min_val)
                    if not is_valid:
                        if field not in errors:
                            errors[field] = []
                        errors[field].append(f"{field} must be at least {min_val}")
                except (ValueError, IndexError):
                    pass
            elif rule.startswith("max_"):
                try:
                    max_val = float(rule.split("_")[1])
                    is_valid, _ = validate_amount(float(value), max_amount=max_val)
                    if not is_valid:
                        if field not in errors:
                            errors[field] = []
                        errors[field].append(f"{field} must not exceed {max_val}")
                except (ValueError, IndexError):
                    pass
    return errors
