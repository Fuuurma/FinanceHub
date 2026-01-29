"""
Tests for Standardized Exception System
"""
import pytest
from datetime import datetime

from core.exceptions import (
    APIException,
    ErrorResponse,
    NotFoundException,
    ValidationException,
    RateLimitException,
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    DuplicateResourceException,
    ServiceException,
    DatabaseException,
    ExternalAPIException,
    ERROR_CODES,
)


class TestErrorResponse:
    """Tests for ErrorResponse schema."""

    def test_error_response_creation(self):
        """Test basic error response creation."""
        response = ErrorResponse(
            error="Test error",
            code="test_error",
            status=400,
        )
        
        assert response.success is False
        assert response.error == "Test error"
        assert response.code == "test_error"
        assert response.status == 400
        assert response.timestamp is not None

    def test_error_response_with_details(self):
        """Test error response with additional details."""
        response = ErrorResponse(
            error="Validation failed",
            code="validation_error",
            status=422,
            details={"field": "email", "reason": "invalid format"},
        )
        
        assert response.details == {"field": "email", "reason": "invalid format"}

    def test_error_response_timestamp(self):
        """Test that timestamp is auto-generated."""
        before = datetime.utcnow().isoformat()
        response = ErrorResponse(error="test", code="test", status=400)
        after = datetime.utcnow().isoformat()
        
        assert response.timestamp >= before
        assert response.timestamp <= after


class TestAPIException:
    """Tests for base APIException class."""

    def test_api_exception_creation(self):
        """Test basic APIException creation."""
        exc = APIException("Test error", "test_error", 400)
        
        assert exc.message == "Test error"
        assert exc.code == "test_error"
        assert exc.status == 400
        assert exc.details == {}

    def test_api_exception_with_details(self):
        """Test APIException with details."""
        exc = APIException(
            "Validation failed",
            "validation_error",
            422,
            {"field": "email"},
        )
        
        assert exc.details == {"field": "email"}

    def test_api_exception_to_response(self):
        """Test conversion to ErrorResponse."""
        exc = APIException("Test error", "test_error", 400, {"key": "value"})
        response = exc.to_response()
        
        assert isinstance(response, ErrorResponse)
        assert response.error == "Test error"
        assert response.code == "test_error"
        assert response.status == 400
        assert response.details == {"key": "value"}


class TestNotFoundException:
    """Tests for NotFoundException."""

    def test_not_found_without_id(self):
        """Test NotFoundException without resource ID."""
        exc = NotFoundException("Alert")
        
        assert exc.message == "Alert not found"
        assert exc.code == "not_found"
        assert exc.status == 404

    def test_not_found_with_id(self):
        """Test NotFoundException with resource ID."""
        exc = NotFoundException("Alert", "alert-123")
        
        assert exc.message == "Alert with id 'alert-123' not found"
        assert exc.code == "not_found"
        assert exc.status == 404


class TestValidationException:
    """Tests for ValidationException."""

    def test_validation_exception(self):
        """Test basic ValidationException."""
        exc = ValidationException("Invalid input")
        
        assert exc.message == "Invalid input"
        assert exc.code == "validation_error"
        assert exc.status == 422

    def test_validation_exception_with_errors(self):
        """Test ValidationException with field errors."""
        errors = {"email": "invalid format", "age": "must be positive"}
        exc = ValidationException("Validation failed", errors=errors)
        
        assert exc.details == {"email": "invalid format", "age": "must be positive"}

    def test_validation_exception_with_field_errors(self):
        """Test ValidationException with structured field errors."""
        field_errors = [
            {"field": "email", "message": "invalid format"},
            {"field": "age", "message": "must be positive"},
        ]
        exc = ValidationException("Validation failed", field_errors=field_errors)
        
        assert "field_errors" in exc.details
        assert len(exc.details["field_errors"]) == 2


class TestRateLimitException:
    """Tests for RateLimitException."""

    def test_rate_limit_exception(self):
        """Test basic RateLimitException."""
        exc = RateLimitException()
        
        assert "Rate limit exceeded" in exc.message
        assert exc.code == "rate_limit_exceeded"
        assert exc.status == 429
        assert exc.details["retry_after"] == 60

    def test_rate_limit_exception_custom_retry(self):
        """Test RateLimitException with custom retry time."""
        exc = RateLimitException(retry_after=120)
        
        assert exc.details["retry_after"] == 120

    def test_rate_limit_exception_custom_message(self):
        """Test RateLimitException with custom message."""
        exc = RateLimitException(message="Custom rate limit message", retry_after=30)
        
        assert exc.message == "Custom rate limit message"


class TestAuthenticationException:
    """Tests for AuthenticationException."""

    def test_authentication_exception(self):
        """Test basic AuthenticationException."""
        exc = AuthenticationException()
        
        assert exc.message == "Authentication required"
        assert exc.code == "authentication_required"
        assert exc.status == 401

    def test_authentication_exception_custom_message(self):
        """Test AuthenticationException with custom message."""
        exc = AuthenticationException("Token expired")
        
        assert exc.message == "Token expired"


class TestAuthorizationException:
    """Tests for AuthorizationException."""

    def test_authorization_exception(self):
        """Test basic AuthorizationException."""
        exc = AuthorizationException()
        
        assert exc.message == "Permission denied"
        assert exc.code == "permission_denied"
        assert exc.status == 403

    def test_authorization_exception_custom_message(self):
        """Test AuthorizationException with custom message."""
        exc = AuthorizationException("Admin access required")
        
        assert exc.message == "Admin access required"


class TestBusinessLogicException:
    """Tests for BusinessLogicException."""

    def test_business_logic_exception(self):
        """Test basic BusinessLogicException."""
        exc = BusinessLogicException("Insufficient funds")
        
        assert exc.message == "Insufficient funds"
        assert exc.code == "business_error"
        assert exc.status == 400

    def test_business_logic_exception_with_details(self):
        """Test BusinessLogicException with details."""
        exc = BusinessLogicException(
            "Cannot sell more than owned",
            details={"symbol": "AAPL", "owned": 10, "requested": 15},
        )
        
        assert exc.details == {"symbol": "AAPL", "owned": 10, "requested": 15}


class TestDuplicateResourceException:
    """Tests for DuplicateResourceException."""

    def test_duplicate_resource_exception(self):
        """Test basic DuplicateResourceException."""
        exc = DuplicateResourceException("Alert", "test-alert")
        
        assert exc.message == "Alert 'test-alert' already exists"
        assert exc.code == "duplicate_resource"
        assert exc.status == 409


class TestServiceException:
    """Tests for ServiceException."""

    def test_service_exception(self):
        """Test basic ServiceException."""
        exc = ServiceException()
        
        assert "Service temporarily unavailable" in exc.message
        assert exc.code == "service_error"
        assert exc.status == 503

    def test_service_exception_custom_message(self):
        """Test ServiceException with custom message."""
        exc = ServiceException("Database connection failed")
        
        assert exc.message == "Database connection failed"


class TestDatabaseException:
    """Tests for DatabaseException."""

    def test_database_exception(self):
        """Test basic DatabaseException."""
        exc = DatabaseException()
        
        assert "Database error" in exc.message
        assert exc.code == "database_error"
        assert exc.status == 500


class TestExternalAPIException:
    """Tests for ExternalAPIException."""

    def test_external_api_exception(self):
        """Test basic ExternalAPIException."""
        exc = ExternalAPIException("Alpha Vantage")
        
        assert "External API error: Alpha Vantage" in exc.message
        assert exc.code == "external_api_error"
        assert exc.status == 502

    def test_external_api_exception_custom_message(self):
        """Test ExternalAPIException with custom message."""
        exc = ExternalAPIException("Yahoo Finance", message="Rate limit exceeded")
        
        assert exc.message == "Rate limit exceeded"


class TestErrorCodes:
    """Tests for error code constants."""

    def test_error_codes_structure(self):
        """Test that error codes have correct structure."""
        assert "validation_error" in ERROR_CODES
        assert "not_found" in ERROR_CODES
        assert "authentication_required" in ERROR_CODES
        assert "permission_denied" in ERROR_CODES
        assert "rate_limit_exceeded" in ERROR_CODES
        assert "service_error" in ERROR_CODES
        assert "database_error" in ERROR_CODES
        assert "external_api_error" in ERROR_CODES

    def test_error_codes_http_status_mapping(self):
        """Test that error codes map to correct HTTP status codes."""
        assert ERROR_CODES["validation_error"] == 422
        assert ERROR_CODES["not_found"] == 404
        assert ERROR_CODES["authentication_required"] == 401
        assert ERROR_CODES["permission_denied"] == 403
        assert ERROR_CODES["rate_limit_exceeded"] == 429
        assert ERROR_CODES["service_error"] == 503
        assert ERROR_CODES["database_error"] == 500
        assert ERROR_CODES["external_api_error"] == 502


class TestExceptionInheritance:
    """Tests for exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_api_exception(self):
        """Verify all custom exceptions inherit from APIException."""
        exceptions = [
            NotFoundException("test"),
            ValidationException("test"),
            RateLimitException(),
            AuthenticationException(),
            AuthorizationException(),
            BusinessLogicException("test"),
            DuplicateResourceException("test", "id"),
            ServiceException(),
            DatabaseException(),
            ExternalAPIException("test"),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, APIException)

    def test_all_exceptions_produce_error_response(self):
        """Verify all exceptions can produce ErrorResponse."""
        exceptions = [
            NotFoundException("test"),
            ValidationException("test"),
            RateLimitException(),
            AuthenticationException(),
            AuthorizationException(),
            BusinessLogicException("test"),
            DuplicateResourceException("test", "id"),
            ServiceException(),
            DatabaseException(),
            ExternalAPIException("test"),
        ]
        
        for exc in exceptions:
            response = exc.to_response()
            assert isinstance(response, ErrorResponse)
            assert response.success is False
            assert response.error == exc.message
            assert response.code == exc.code
            assert response.status == exc.status
