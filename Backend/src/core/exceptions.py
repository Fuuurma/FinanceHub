"""
Standardized API Exception System
Provides consistent error handling across all API endpoints.
"""
from ninja import Schema, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorDetail(Schema):
    """Individual error detail for validation errors."""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")


class ErrorResponse(Schema):
    """Standardized error response format for all API errors."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    status: int = Field(..., description="HTTP status code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO format timestamp"
    )


class APIException(Exception):
    """
    Base exception class for all API exceptions.
    
    All API exceptions inherit from this class and produce
    standardized ErrorResponse objects.
    """
    
    def __init__(
        self,
        message: str,
        code: str,
        status: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status = status
        self.details = details or {}
        super().__init__(self.message)
    
    def to_response(self) -> ErrorResponse:
        """Convert exception to standardized ErrorResponse."""
        return ErrorResponse(
            error=self.message,
            code=self.code,
            status=self.status,
            details=self.details if self.details else None,
        )


class NotFoundException(APIException):
    """Resource not found exception (404)."""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        else:
            message = f"{resource} not found"
        super().__init__(message, "not_found", 404)


class ValidationException(APIException):
    """Validation error exception (422)."""
    
    def __init__(
        self,
        message: str,
        errors: Optional[Dict[str, Any]] = None,
        field_errors: Optional[list] = None,
    ):
        details = errors or {}
        if field_errors:
            details["field_errors"] = field_errors
        super().__init__(message, "validation_error", 422, details)


class RateLimitException(APIException):
    """Rate limit exceeded exception (429)."""
    
    def __init__(self, retry_after: int = 60, message: Optional[str] = None):
        details = {"retry_after": retry_after}
        super().__init__(
            message or "Rate limit exceeded. Please try again later.",
            "rate_limit_exceeded",
            429,
            details,
        )


class AuthenticationException(APIException):
    """Authentication required exception (401)."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "authentication_required", 401)


class AuthorizationException(APIException):
    """Permission denied exception (403)."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "permission_denied", 403)


class BusinessLogicException(APIException):
    """Business logic error exception (400)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "business_error", 400, details)


class DuplicateResourceException(APIException):
    """Resource already exists exception (409)."""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} '{identifier}' already exists"
        super().__init__(message, "duplicate_resource", 409)


class ServiceException(APIException):
    """Service temporarily unavailable exception (503)."""
    
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, "service_error", 503)


class DatabaseException(APIException):
    """Database error exception (500)."""
    
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, "database_error", 500)


class ExternalAPIException(APIException):
    """External API error exception (502)."""
    
    def __init__(self, service: str, message: Optional[str] = None):
        error_message = message or f"External API error: {service}"
        super().__init__(error_message, "external_api_error", 502)


# Error code constants for consistent usage
ERROR_CODES = {
    # Client errors (4xx)
    "validation_error": 422,
    "not_found": 404,
    "duplicate_resource": 409,
    "authentication_required": 401,
    "permission_denied": 403,
    "rate_limit_exceeded": 429,
    "invalid_input": 400,
    "business_error": 400,
    # Server errors (5xx)
    "service_error": 503,
    "database_error": 500,
    "external_api_error": 502,
    "internal_error": 500,
}
