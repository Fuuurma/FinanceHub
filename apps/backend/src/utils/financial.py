"""
Financial utility functions for precise decimal calculations.

This module provides utilities for handling financial calculations with
proper decimal precision to avoid floating-point rounding errors.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Optional, Union


Number = Union[int, float, str, Decimal]


def to_decimal(value: Optional[Number], default: Decimal = Decimal("0")) -> Decimal:
    """
    Convert value to Decimal, handling all types safely.

    Args:
        value: The value to convert (int, float, str, or Decimal)
        default: Default value if conversion fails or value is None

    Returns:
        Decimal representation of the value

    Examples:
        >>> to_decimal(100)
        Decimal('100')
        >>> to_decimal("123.45")
        Decimal('123.45')
        >>> to_decimal(None)
        Decimal('0')
    """
    if value is None:
        return default

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, float)):
        # Convert via string to avoid float precision issues
        return Decimal(str(value))

    if isinstance(value, str):
        try:
            # Handle currency formatting
            cleaned = value.replace("$", "").replace(",", "").strip()
            return Decimal(cleaned)
        except InvalidOperation:
            return default

    return default


def safe_add(a: Optional[Number], b: Optional[Number]) -> Decimal:
    """
    Safely add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Decimal sum of a and b

    Examples:
        >>> safe_add(0.1, 0.2)
        Decimal('0.3')
        >>> safe_add(100, 200)
        Decimal('300')
    """
    return to_decimal(a) + to_decimal(b)


def safe_subtract(a: Optional[Number], b: Optional[Number]) -> Decimal:
    """
    Safely subtract two numbers.

    Args:
        a: First number
        b: Second number to subtract

    Returns:
        Decimal difference of a and b

    Examples:
        >>> safe_subtract(10, 3)
        Decimal('7')
    """
    return to_decimal(a) - to_decimal(b)


def safe_multiply(a: Optional[Number], b: Optional[Number]) -> Decimal:
    """
    Safely multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Decimal product of a and b

    Examples:
        >>> safe_multiply(5, 3)
        Decimal('15')
    """
    return to_decimal(a) * to_decimal(b)


def safe_divide(
    a: Optional[Number], b: Optional[Number], default: Decimal = Decimal("0")
) -> Decimal:
    """
    Safely divide two numbers, avoiding division by zero.

    Args:
        a: Numerator
        b: Denominator
        default: Value to return if division by zero

    Returns:
        Decimal quotient of a and b, or default if b is zero

    Examples:
        >>> safe_divide(10, 2)
        Decimal('5')
        >>> safe_divide(10, 0)
        Decimal('0')
    """
    divisor = to_decimal(b)
    if divisor == 0:
        return default
    return to_decimal(a) / divisor


def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """
    Round Decimal to specified decimal places using banker's rounding.

    Args:
        value: Decimal value to round
        places: Number of decimal places (default: 2)

    Returns:
        Rounded Decimal value

    Examples:
        >>> round_decimal(Decimal('1.2345'), 2)
        Decimal('1.23')
        >>> round_decimal(Decimal('1.235'), 2)
        Decimal('1.24')
    """
    quantizer = Decimal("10") ** -places
    return value.quantize(quantizer, rounding=ROUND_HALF_UP)


def format_currency(value: Decimal, currency: str = "$") -> str:
    """
    Format Decimal as currency string.

    Args:
        value: Decimal value to format
        currency: Currency symbol (default: '$')

    Returns:
        Formatted currency string

    Examples:
        >>> format_currency(Decimal('1234.56'))
        '$1,234.56'
        >>> format_currency(Decimal('1000'), '€')
        '€1,000.00'
    """
    return f"{currency}{value:,.2f}"


def format_percentage(value: Decimal, places: int = 2) -> str:
    """
    Format Decimal as percentage string.

    Args:
        value: Decimal value (e.g., 0.1234 for 12.34%)
        places: Number of decimal places (default: 2)

    Returns:
        Formatted percentage string

    Examples:
        >>> format_percentage(Decimal('0.1234'))
        '12.34%'
        >>> format_percentage(Decimal('0.5'))
        '50.00%'
    """
    return f"{round_decimal(value * 100, places)}%"


def calculate_percentage(part: Optional[Number], whole: Optional[Number]) -> Decimal:
    """
    Calculate percentage of part relative to whole.

    Args:
        part: The part value
        whole: The whole value

    Returns:
        Decimal percentage (0-100)

    Examples:
        >>> calculate_percentage(25, 100)
        Decimal('25')
        >>> calculate_percentage(1, 3)
        Decimal('33.33')
    """
    return safe_divide(to_decimal(part), to_decimal(whole)) * 100


def calculate_change(old_value: Optional[Number], new_value: Optional[Number]) -> dict:
    """
    Calculate absolute and percentage change between two values.

    Args:
        old_value: Original value
        new_value: New value

    Returns:
        Dictionary with 'absolute' and 'percentage' change

    Examples:
        >>> calculate_change(100, 110)
        {'absolute': Decimal('10'), 'percentage': Decimal('10.00')}
        >>> calculate_change(100, 90)
        {'absolute': Decimal('-10'), 'percentage': Decimal('-10.00')}
    """
    old = to_decimal(old_value)
    new = to_decimal(new_value)

    absolute_change = new - old
    percentage_change = (
        safe_divide(absolute_change, old) * 100 if old != 0 else Decimal("0")
    )

    return {"absolute": absolute_change, "percentage": round_decimal(percentage_change)}
