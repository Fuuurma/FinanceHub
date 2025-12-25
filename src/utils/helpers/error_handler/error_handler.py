"""Global error handler for Django Ninja API"""

import traceback
import jwt
import sys
from typing import Any, Dict
from django.http import HttpRequest, JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.db import DatabaseError, IntegrityError
from pydantic import ValidationError as PydanticValidationError
from utils.helpers.error_handler.exceptions import (
    AuthenticationException,
    BaseAPIException,
    DatabaseException,
    PermissionDeniedException,
    ResourceNotFoundException,
    ValidationException,
)

logger = get_logger(__name__)


class GlobalErrorHandler:
    """Global error handler for all API exceptions"""

    @staticmethod
    def handle_base_api_exception(
        request: HttpRequest, exc: BaseAPIException
    ) -> JsonResponse:
        """Handle custom API exceptions"""
        logger.warning(
            f"API Exception: {exc.code}",
            extra={
                "status_code": exc.status_code,
                "message": str(exc.message),
                "details": exc.details,
                "path": request.path,
                "method": request.method,
                "user": getattr(request, "user", None),
            },
        )

        return JsonResponse(exc.to_dict(), status=exc.status_code)

    @staticmethod
    def handle_authentication_exception(
        request: HttpRequest, exc: Exception
    ) -> JsonResponse:
        """Handle authentication-related exceptions"""
        if isinstance(exc, jwt.ExpiredSignatureError):
            exception = AuthenticationException(
                message="Token has expired", code="token_expired"
            )
        elif isinstance(exc, jwt.InvalidTokenError):
            exception = AuthenticationException(
                message="Invalid token", code="invalid_token"
            )
        else:
            exception = AuthenticationException(
                message=str(exc), code="authentication_failed"
            )

        return GlobalErrorHandler.handle_base_api_exception(request, exception)

    @staticmethod
    def handle_permission_denied(
        request: HttpRequest, exc: PermissionDenied
    ) -> JsonResponse:
        """Handle Django permission denied exceptions"""
        exception = PermissionDeniedException(message=str(exc) if str(exc) else None)

        return GlobalErrorHandler.handle_base_api_exception(request, exception)

    @staticmethod
    def handle_validation_error(request: HttpRequest, exc: Exception) -> JsonResponse:
        """Handle validation errors"""
        details = {}

        if isinstance(exc, ValidationError):
            if hasattr(exc, "error_dict"):
                details = {
                    field: [str(error) for error in errors]
                    for field, errors in exc.error_dict.items()
                }
            elif hasattr(exc, "error_list"):
                details = {"non_field_errors": [str(e) for e in exc.error_list]}
            else:
                details = {"non_field_errors": [str(exc)]}

        elif isinstance(exc, PydanticValidationError):
            details = {
                "validation_errors": [
                    {
                        "field": ".".join(str(loc) for loc in error["loc"]),
                        "message": error["msg"],
                        "type": error["type"],
                    }
                    for error in exc.errors()
                ]
            }

        exception = ValidationException(message="Validation failed", details=details)

        return GlobalErrorHandler.handle_base_api_exception(request, exception)

    @staticmethod
    def handle_object_not_found(
        request: HttpRequest, exc: ObjectDoesNotExist
    ) -> JsonResponse:
        """Handle Django ObjectDoesNotExist exceptions"""
        exception = ResourceNotFoundException(
            message=str(exc) if str(exc) else "Resource not found"
        )

        return GlobalErrorHandler.handle_base_api_exception(request, exception)

    @staticmethod
    def handle_database_error(request: HttpRequest, exc: Exception) -> JsonResponse:
        """Handle database-related exceptions"""
        logger.error(
            f"Database error: {str(exc)}",
            extra={
                "path": request.path,
                "method": request.method,
                "user": getattr(request, "user", None),
            },
            exc_info=True,
        )

        if isinstance(exc, IntegrityError):
            message = "Database integrity error. Resource may already exist."
            code = "integrity_error"
        else:
            message = "Database error occurred"
            code = "database_error"

        exception = DatabaseException(message=message, code=code)

        return GlobalErrorHandler.handle_base_api_exception(request, exception)

    @staticmethod
    def handle_generic_exception(request: HttpRequest, exc: Exception) -> JsonResponse:
        """Handle unexpected exceptions"""
        # Log full traceback for debugging
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)

        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "traceback": "".join(tb_lines),
                "path": request.path,
                "method": request.method,
                "user": getattr(request, "user", None),
            },
            exc_info=True,
        )

        # Don't expose internal errors to users in production
        from django.conf import settings

        if settings.DEBUG:
            message = f"{exc.__class__.__name__}: {str(exc)}"
        else:
            message = "An unexpected error occurred. Please try again later."

        exception = BaseAPIException(
            message=message, code="internal_server_error", status_code=500
        )

        return GlobalErrorHandler.handle_base_api_exception(request, exception)

    @staticmethod
    def register_handlers(api):
        """Register all error handlers with Django Ninja API"""

        # Custom API exceptions
        @api.exception_handler(BaseAPIException)
        def handle_api_exception(request: HttpRequest, exc: BaseAPIException):
            return GlobalErrorHandler.handle_base_api_exception(request, exc)

        # Authentication exceptions
        @api.exception_handler(jwt.ExpiredSignatureError)
        @api.exception_handler(jwt.InvalidTokenError)
        def handle_jwt_exception(request: HttpRequest, exc: Exception):
            return GlobalErrorHandler.handle_authentication_exception(request, exc)

        # Permission exceptions
        @api.exception_handler(PermissionDenied)
        def handle_permission_exception(request: HttpRequest, exc: PermissionDenied):
            return GlobalErrorHandler.handle_permission_denied(request, exc)

        # Validation exceptions
        @api.exception_handler(ValidationError)
        @api.exception_handler(PydanticValidationError)
        def handle_validation_exception(request: HttpRequest, exc: Exception):
            return GlobalErrorHandler.handle_validation_error(request, exc)

        # Not found exceptions
        @api.exception_handler(ObjectDoesNotExist)
        def handle_not_found_exception(request: HttpRequest, exc: ObjectDoesNotExist):
            return GlobalErrorHandler.handle_object_not_found(request, exc)

        # Database exceptions
        @api.exception_handler(DatabaseError)
        @api.exception_handler(IntegrityError)
        def handle_db_exception(request: HttpRequest, exc: Exception):
            return GlobalErrorHandler.handle_database_error(request, exc)

        # Generic exceptions (catch-all)
        @api.exception_handler(Exception)
        def handle_generic_exception(request: HttpRequest, exc: Exception):
            return GlobalErrorHandler.handle_generic_exception(request, exc)
