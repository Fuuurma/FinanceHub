# Test Cases for Security Fixes

**Created:** Feb 1, 2026
**Author:** GRACE (QA/Testing Engineer)
**Status:** DRAFT - Ready for Implementation

---

## G-001: Test S-009 - Decimal Financial Calculations

### Test File
`apps/backend/src/tests/test_decimal_precision.py`

### Test Cases

#### TestToDecimal
- test_none_value: None returns default value
- test_none_with_custom_default: None with custom default
- test_integer_conversion: Integer to Decimal
- test_float_conversion: Float to Decimal
- test_decimal_passthrough:
- test_string Decimal passed through unchanged_without_currency: Plain string number
- test_string_with_currency: String with currency symbol
- test_string_with_commas: String with thousand separators
- test_invalid_string: Invalid string returns default

#### TestSafeAdd
- test_basic_addition: Basic addition
- test_decimal_precision: 0.1 + 0.2 = 0.3 exactly
- test_float_precision_edge_case: Problematic float addition
- test_with_none: Addition with None
- test_both_none: Both values None

#### TestSafeSubtract
- test_basic_subtraction: Basic subtraction
- test_negative_result: Negative result
- test_with_none: Subtraction with None

#### TestSafeMultiply
- test_basic_multiplication: Basic multiplication
- test_fractional_multiplication: Fractional multiplication precision
- test_with_none: Multiplication with None

#### TestSafeDivide
- test_basic_division: Basic division
- test_division_by_zero: Division by zero returns default
- test_division_by_zero_custom_default: Division by zero with custom default
- test_with_none: Division with None

#### TestRoundDecimal
- test_basic_rounding: Basic rounding to 2 decimals
- test_half_up_rounding: Half up rounding (0.5 rounds up)
- test_rounding_negative: Rounding negative numbers

#### TestPortfolioCalculations
- test_portfolio_value_calculation: Portfolio value calculation precision
- test_portfolio_pnl_calculation: Portfolio P&L calculation
- test_fractional_shares_calculation: Fractional shares dont cause precision errors
- test_many_small_positions: Many small positions maintain precision

#### TestTechnicalIndicators
- test_bollinger_bands_precision: Bollinger Bands calculation precision
- test_macd_calculation_precision: MACD calculation precision

#### TestAlertEvaluation
- test_above_alert_triggers: Above alert triggers correctly
- test_below_alert_triggers: Below alert triggers correctly
- test_alert_precision_boundary: Alert at exact boundary

#### TestSentimentCalculation
- test_sentiment_score_precision: Sentiment score calculation precision
- test_sentiment_classification: Sentiment classification

---

## G-002: Test S-010 - Token Race Conditions

### Test File
`apps/backend/src/tests/test_token_security.py`

### Test Cases

#### TestTokenRaceConditions
- test_concurrent_token_refresh_no_race: Concurrent token refreshes dont cause race conditions
- test_token_not_shared_across_requests: Tokens are not improperly shared
- test_token_refresh_is_idempotent: Token refresh is idempotent
- test_token_rotation_prevents_replay: Token rotation prevents replay attacks
- test_refresh_token_blocked_during_refresh: Token refresh blocks during ongoing refresh

#### TestTokenStorage
- test_tokens_not_in_localstorage: Tokens are not stored in localStorage
- test_tokens_use_httponly_cookies: Tokens use HTTP-only cookies

#### TestTokenExpiration
- test_expired_token_rejected: Expired tokens are rejected
- test_refresh_before_expiration: Automatic refresh before expiration
- test_no_refresh_for_fresh_token: Fresh tokens dont trigger refresh

---

## G-003: Test S-011 - Remove Print Statements

### Test File
`apps/backend/src/tests/test_logging.py`

### Test Cases

#### TestNoPrintStatements
- test_no_print_in_production_code: Verify no print() in production code
- test_no_print_in_exceptions: Verify no print in exception handlers
- test_no_print_in_debug_code: Verify no print in debug code

#### TestLoggingConfiguration
- test_logging_configured: Verify logging is configured
- test_log_levels_used_correctly: Verify log levels are used correctly
- test_no_sensitive_data_in_logs: Verify no sensitive data in log messages

#### TestLoggingBehavior
- test_error_logged: Errors are logged properly
- test_warning_logged: Warnings are logged properly
- test_info_logged: Info messages are logged properly
- test_debug_logged: Debug messages are logged properly

---

## Coverage Summary

| Security Fix | Test Cases | Priority |
|--------------|------------|----------|
| S-009 Decimal | 25+ tests | P0 CRITICAL |
| S-010 Token Race | 8 tests | P0 CRITICAL |
| S-011 Print Stmts | 9 tests | P0 CRITICAL |

**Total: 42+ test cases**

---

## Next Steps

1. Install pytest and dependencies
2. Create test files
3. Run tests to verify they pass
4. Document coverage

---

**GRACE - QA/Testing Engineer**
