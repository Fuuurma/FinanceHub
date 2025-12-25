# """Custom exception classes for the application"""

# from typing import Optional, Dict, Any
# from django.utils.translation import gettext_lazy as _

# # todo: expand docstrings for all exceptions, do using constants, httpCodes from Library


# class BaseAPIException(Exception):
#     """Base exception class for all API exceptions"""

#     status_code = 500
#     default_code = "error"
#     default_message = _("An error occurred")

#     def __init__(
#         self,
#         message: Optional[str] = None,
#         code: Optional[str] = None,
#         status_code: Optional[int] = None,
#         details: Optional[Dict[str, Any]] = None,
#     ):
#         self.message = message or self.default_message
#         self.code = code or self.default_code
#         self.status_code = status_code or self.status_code
#         self.details = details or {}
#         super().__init__(self.message)

#     def to_dict(self) -> Dict[str, Any]:
#         """Convert exception to dictionary"""
#         error_dict = {
#             "error": {
#                 "code": self.code,
#                 "message": str(self.message),
#                 "status": self.status_code,
#             }
#         }

#         if self.details:
#             error_dict["error"]["details"] = self.details

#         return error_dict


# # Authentication Exceptions
# class AuthenticationException(BaseAPIException):
#     """Base authentication exception"""

#     status_code = 401
#     default_code = "authentication_failed"
#     default_message = _("Authentication failed")


# class InvalidCredentialsException(AuthenticationException):
#     """Invalid username or password"""

#     default_code = "invalid_credentials"
#     default_message = _("Invalid email or password")


# class TokenExpiredException(AuthenticationException):
#     """Token has expired"""

#     default_code = "token_expired"
#     default_message = _("Token has expired")


# class InvalidTokenException(AuthenticationException):
#     """Invalid or malformed token"""

#     default_code = "invalid_token"
#     default_message = _("Invalid token")


# class AccountLockedException(AuthenticationException):
#     """Account is locked"""

#     status_code = 403
#     default_code = "account_locked"
#     default_message = _(
#         "Account is temporarily locked due to multiple failed login attempts"
#     )


# class TwoFactorRequiredException(AuthenticationException):
#     """Two-factor authentication required"""

#     default_code = "two_factor_required"
#     default_message = _("Two-factor authentication is required")


# class InvalidTwoFactorCodeException(AuthenticationException):
#     """Invalid 2FA code"""

#     default_code = "invalid_two_factor_code"
#     default_message = _("Invalid two-factor authentication code")


# # Authorization Exceptions
# class PermissionDeniedException(BaseAPIException):
#     """User does not have permission"""

#     status_code = 403
#     default_code = "permission_denied"
#     default_message = _("You do not have permission to perform this action")


# class InsufficientPrivilegesException(PermissionDeniedException):
#     """Insufficient privileges for action"""

#     default_code = "insufficient_privileges"
#     default_message = _("Insufficient privileges")


# # Validation Exceptions
# class ValidationException(BaseAPIException):
#     """Validation error"""

#     status_code = 422
#     default_code = "validation_error"
#     default_message = _("Validation failed")


# class InvalidInputException(ValidationException):
#     """Invalid input data"""

#     default_code = "invalid_input"
#     default_message = _("Invalid input data")


# class DuplicateResourceException(ValidationException):
#     """Resource already exists"""

#     status_code = 409
#     default_code = "duplicate_resource"
#     default_message = _("Resource already exists")


# # Resource Exceptions
# class ResourceNotFoundException(BaseAPIException):
#     """Resource not found"""

#     status_code = 404
#     default_code = "resource_not_found"
#     default_message = _("Resource not found")


# class ResourceGoneException(BaseAPIException):
#     """Resource has been deleted"""

#     status_code = 410
#     default_code = "resource_gone"
#     default_message = _("Resource has been deleted")


# # Rate Limiting
# class RateLimitExceededException(BaseAPIException):
#     """Rate limit exceeded"""

#     status_code = 429
#     default_code = "rate_limit_exceeded"
#     default_message = _("Rate limit exceeded. Please try again later.")


# # Business Logic Exceptions
# class BusinessLogicException(BaseAPIException):
#     """Business logic error"""

#     status_code = 400
#     default_code = "business_logic_error"
#     default_message = _("Business logic error")


# class InsufficientFundsException(BusinessLogicException):
#     """Insufficient funds for transaction"""

#     default_code = "insufficient_funds"
#     default_message = _("Insufficient funds")


# class InvalidTransactionException(BusinessLogicException):
#     """Invalid transaction"""

#     default_code = "invalid_transaction"
#     default_message = _("Invalid transaction")


# # Service Exceptions
# class ServiceUnavailableException(BaseAPIException):
#     """External service unavailable"""

#     status_code = 503
#     default_code = "service_unavailable"
#     default_message = _("Service temporarily unavailable")


# class ExternalAPIException(BaseAPIException):
#     """External API error"""

#     status_code = 502
#     default_code = "external_api_error"
#     default_message = _("External API error")


# class DatabaseException(BaseAPIException):
#     """Database error"""

#     status_code = 500
#     default_code = "database_error"
#     default_message = _("Database error occurred")
