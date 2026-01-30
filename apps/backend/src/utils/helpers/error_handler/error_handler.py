from typing import Optional
import sys
import jwt
from django.http import HttpRequest, JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.db import DatabaseError, IntegrityError
from pydantic import ValidationError as PydanticValidationError
from ninja.errors import ValidationError as NinjaValidationError
from django.conf import settings
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class GlobalErrorHandler:
    @staticmethod
    def _log_error(request: HttpRequest, exc: Exception, extra: Optional[dict] = None):
        logger.error(
            f"{exc.__class__.__name__}: {str(exc)}",
            extra={
                "request_id": getattr(request, "request_id", None),
                "path": request.path,
                "method": request.method,
                "user_id": (
                    getattr(request.user, "id", None)
                    if request.user.is_authenticated
                    else None
                ),
                **(extra or {}),
            },
            exc_info=True,
        )

    @staticmethod
    def handle_validation_error(request: HttpRequest, exc: Exception) -> JsonResponse:
        details = {}

        if isinstance(exc, (ValidationError, NinjaValidationError)):
            details = {
                "validation_errors": [
                    str(e)
                    for e in exc.errors()
                    if isinstance(exc, NinjaValidationError)
                ]
                or exc.messages()
            }
        elif isinstance(exc, PydanticValidationError):
            details = {
                "validation_errors": [
                    {
                        "field": ".".join(map(str, e["loc"])),
                        "message": e["msg"],
                        "type": e["type"],
                    }
                    for e in exc.errors()
                ]
            }

        response_data = {
            "error": {
                "code": "validation_error",
                "message": "Validation failed",
                "status": 422,
                "details": details,
            }
        }
        return JsonResponse(response_data, status=422)

    @staticmethod
    def handle_auth_error(request: HttpRequest, exc: Exception) -> JsonResponse:
        if isinstance(exc, jwt.ExpiredSignatureError):
            code, message = "token_expired", "Token has expired"
        elif isinstance(exc, jwt.InvalidTokenError):
            code, message = "invalid_token", "Invalid token"
        else:
            code, message = "authentication_failed", "Authentication failed"

        GlobalErrorHandler._log_error(request, exc)
        return JsonResponse(
            {"error": {"code": code, "message": message, "status": 401}}, status=401
        )

    @staticmethod
    def handle_permission_denied(
        request: HttpRequest, exc: PermissionDenied
    ) -> JsonResponse:
        GlobalErrorHandler._log_error(request, exc)
        return JsonResponse(
            {
                "error": {
                    "code": "permission_denied",
                    "message": "Permission denied",
                    "status": 403,
                }
            },
            status=403,
        )

    @staticmethod
    def handle_not_found(request: HttpRequest, exc: ObjectDoesNotExist) -> JsonResponse:
        return JsonResponse(
            {
                "error": {
                    "code": "resource_not_found",
                    "message": "Resource not found",
                    "status": 404,
                }
            },
            status=404,
        )

    @staticmethod
    def handle_database_error(request: HttpRequest, exc: Exception) -> JsonResponse:
        GlobalErrorHandler._log_error(request, exc, {"db_error": str(exc)})
        return JsonResponse(
            {
                "error": {
                    "code": "database_error",
                    "message": "Database error",
                    "status": 500,
                }
            },
            status=500,
        )

    @staticmethod
    def handle_unexpected(request: HttpRequest, exc: Exception) -> JsonResponse:
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        GlobalErrorHandler._log_error(request, exc, {"traceback": tb})

        message = "Internal server error" if not settings.DEBUG else str(exc)
        return JsonResponse(
            {"error": {"code": "internal_error", "message": message, "status": 500}},
            status=500,
        )

    @staticmethod
    def register_handlers(api):
        from ninja import NinjaAPI

        @api.exception_handler(PydanticValidationError)
        @api.exception_handler(NinjaValidationError)
        @api.exception_handler(ValidationError)
        def validation(request, exc):
            return GlobalErrorHandler.handle_validation_error(request, exc)

        @api.exception_handler(jwt.ExpiredSignatureError)
        @api.exception_handler(jwt.InvalidTokenError)
        def auth_errors(request, exc):
            return GlobalErrorHandler.handle_auth_error(request, exc)

        @api.exception_handler(PermissionDenied)
        def permission(request, exc):
            return GlobalErrorHandler.handle_permission_denied(request, exc)

        @api.exception_handler(ObjectDoesNotExist)
        def not_found(request, exc):
            return GlobalErrorHandler.handle_not_found(request, exc)

        @api.exception_handler(DatabaseError)
        def db_error(request, exc):
            return GlobalErrorHandler.handle_database_error(request, exc)

        @api.exception_handler(Exception)
        def unexpected(request, exc):
            return GlobalErrorHandler.handle_unexpected(request, exc)
