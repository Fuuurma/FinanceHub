import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import orjson
from django.conf import settings


class ORJSONFormatter(logging.Formatter):
    """Ultra-fast JSON formatter using orjson"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "environment": getattr(settings, "ENVIRONMENT", "development"),
        }

        # Request context from middleware
        for attr in [
            "request_id",
            "user_id",
            "path",
            "method",
            "ip_address",
            "user_agent",
        ]:
            if value := getattr(record, attr, None):
                log_data[attr] = value

        # Add any extra context
        if extra := getattr(record, "extra", None):
            log_data.update(extra)

        # Handle exceptions gracefully
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        try:
            return orjson.dumps(
                log_data,
                option=(
                    orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2
                    if settings.DEBUG
                    else 0
                ),
            ).decode()
        except Exception:
            # Fallback
            log_data = {k: str(v) for k, v in log_data.items()}
            return orjson.dumps(log_data).decode()


class SimpleFormatter(logging.Formatter):
    """Human-readable for local development"""

    def format(self, record: logging.LogRecord) -> str:
        return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {record.levelname} [{record.name}:{record.lineno}] {record.getMessage()}"
