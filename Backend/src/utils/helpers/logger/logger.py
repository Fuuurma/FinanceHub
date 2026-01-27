import logging
import sys
from utils.helpers.logger.formatter import ORJSONFormatter, SimpleFormatter
from django.conf import settings


def setup_logging() -> None:
    """Initialize logging with orjson in production"""
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        ORJSONFormatter() if getattr(settings, "LOG_JSON", False) else SimpleFormatter()
    )
    root.addHandler(handler)

    # Optional error file
    if log_file := getattr(settings, "LOG_FILE", None):
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(ORJSONFormatter())
        root.addHandler(file_handler)

    # Silence noisy loggers
    for logger_name in [
        "django.server",
        "django.request",
        "django.db.backends",
        "urllib3",
    ]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str = __name__, **context) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logging.getLogger(name), context or {})
