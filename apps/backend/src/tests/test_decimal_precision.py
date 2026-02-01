"""
Decimal Precision Tests - S-009

Tests for financial calculations to ensure proper Decimal usage
instead of float() to prevent precision errors.

Created by: ARIA (for GRACE/GAUDÍ)
Date: February 1, 2026
Status: TEMPLATE - Needs completion
"""

import pytest
from decimal import Decimal, ROUND_HALF_UP
from src.utils.financial import (
    to_decimal,
    safe_add,
    safe_subtract,
    safe_multiply,
    safe_divide,
    round_currency,
    calculate_percentage,
)


class TestToDecimal:
    """Test to_decimal utility function."""

    def test_float_to_decimal(self):
        """Convert float to Decimal correctly."""
        result = to_decimal(0.1)
        assert result == Decimal("0.1")

    def test_string_to_decimal(self):
        """Convert string to Decimal."""
        result = to_decimal("123.45")
        assert result == Decimal("123.45")

    def test_int_to_decimal(self):
        """Convert integer to Decimal."""
        result = to_decimal(100)
        assert result == Decimal("100")

    def test_precision_maintained(self):
        """Ensure 4 decimal places for currency."""
        result = to_decimal("123.4567")
        assert str(result) == "123.4567"


class TestSafeAdd:
    """Test safe_add for currency addition."""

    def test_simple_addition(self):
        """0.1 + 0.2 should equal 0.3"""
        result = safe_add(0.1, 0.2)
        assert result == Decimal("0.3")

    def test_currency_addition(self):
        """Add currency amounts."""
        result = safe_add("100.50", "200.25")
        assert result == Decimal("300.75")

    def test_multiple_addition(self):
        """Add multiple values."""
        result = safe_add("1.00", "2.00", "3.00")
        assert result == Decimal("6.00")


class TestSafeSubtract:
    """Test safe_subtract for currency subtraction."""

    def test_simple_subtraction(self):
        """0.3 - 0.1 should equal 0.2"""
        result = safe_subtract(0.3, 0.1)
        assert result == Decimal("0.2")

    def test_currency_subtraction(self):
        """Subtract currency amounts."""
        result = safe_subtract("100.00", "25.50")
        assert result == Decimal("74.50")


class TestSafeMultiply:
    """Test safe_multiply for currency multiplication."""

    def test_simple_multiplication(self):
        """0.1 * 2 should equal 0.2"""
        result = safe_multiply(0.1, 2)
        assert result == Decimal("0.2")

    def test_currency_multiplication(self):
        """Multiply currency by quantity."""
        result = safe_multiply("10.00", 5)
        assert result == Decimal("50.00")


class TestSafeDivide:
    """Test safe_divide for currency division."""

    def test_simple_division(self):
        """0.3 / 3 should equal 0.1"""
        result = safe_divide(0.3, 3)
        assert result == Decimal("0.1")

    def test_division_by_zero(self):
        """Handle division by zero gracefully."""
        with pytest.raises(ValueError):
            safe_divide("100.00", 0)


class TestRoundCurrency:
    """Test round_currency for proper rounding."""

    def test_standard_rounding(self):
        """Round to 2 decimal places."""
        result = round_currency("123.456")
        assert result == Decimal("123.46")

    def test_half_up_rounding(self):
        """Test ROUND_HALF_UP behavior."""
        result = round_currency("123.455")
        assert result == Decimal("123.46")

    def test_banking_rounding(self):
        """Test rounding at boundary."""
        result = round_currency("123.454")
        assert result == Decimal("123.45")


class TestCalculatePercentage:
    """Test calculate_percentage for percentage calculations."""

    def test_simple_percentage(self):
        """10% of 100 should be 10."""
        result = calculate_percentage(100, 10)
        assert result == Decimal("10.00")

    def test_percentage_with_decimals(self):
        """Calculate percentage with decimals."""
        result = calculate_percentage("100.00", 12.5)
        assert result == Decimal("12.50")

    def test_percentage_result_format(self):
        """Ensure result has 2 decimal places."""
        result = calculate_percentage("100.00", 33.33)
        assert str(result) == "33.33"


class TestPrecisionEdgeCases:
    """Test edge cases for decimal precision."""

    def test_float_precision_issue(self):
        """
        THE CLASSIC BUG: 0.1 + 0.2 != 0.3 in float
        Should be equal in Decimal.
        """
        # This should work with Decimal
        result = to_decimal(0.1) + to_decimal(0.2)
        assert result == to_decimal(0.3)

        # This would fail with float
        # float(0.1) + float(0.2) == 0.30000000000000004  # WRONG!
        # to_decimal(0.1) + to_decimal(0.2) == 0.3       # CORRECT!

    def test_large_numbers(self):
        """Handle large currency values."""
        result = safe_multiply("999999.99", 100)
        assert result == Decimal("99999999.00")

    def test_many_decimal_places(self):
        """Handle many decimal places correctly."""
        result = safe_divide("1.00", 3)
        # Should not be 0.33333333333333331 like float
        assert str(result) == "0.3333333333333333333333333333"

    def test_negative_values(self):
        """Handle negative currency values."""
        result = safe_add("-100.00", "50.00")
        assert result == Decimal("-50.00")

    def test_zero_handling(self):
        """Ensure zero is handled correctly."""
        result = safe_add("0.00", "100.00")
        assert result == Decimal("100.00")


class TestFinancialCalculationPerformance:
    """Performance tests for financial calculations."""

    def test_1000_operations_performance(self):
        """Ensure 1000 operations complete quickly."""
        import time

        start = time.time()

        for _ in range(1000):
            safe_add("1.00", "2.00")
            safe_subtract("3.00", "1.00")
            safe_multiply("2.00", 5)
            safe_divide("10.00", 2)

        elapsed = time.time() - start
        assert elapsed < 1.0  # Should complete in under 1 second


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
