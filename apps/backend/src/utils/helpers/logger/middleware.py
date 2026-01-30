# core/middleware.py
import time
import uuid
from django.http import HttpRequest, JsonResponse

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware:
    """Log all incoming requests with context and duration"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.request_id = request_id

        start_time = time.time()
        user = request.user if request.user.is_authenticated else None

        # Log incoming request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "ip_address": self.get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT"),
                "user_id": user.id if user else None,
                "user": str(user) if user else "anonymous",
            },
        )

        response = self.get_response(request)

        duration = time.time() - start_time

        # Log completed response
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": f"{duration:.3f}s",
            },
        )

        # Add request ID header
        response["X-Request-ID"] = request_id
        return response

    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
