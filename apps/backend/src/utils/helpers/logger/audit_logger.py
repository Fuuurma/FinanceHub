from utils.helpers.logger.logger import get_logger
from typing import Any, Dict, Optional


class AuditLogger:
    """High-performance audit trail logger"""

    def __init__(self):
        self.logger = get_logger("audit")

    def user_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        self.logger.info(
            "User action",
            extra={
                "audit_type": "user_action",
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details or {},
                "ip_address": ip_address,
                "user_agent": user_agent,
            },
        )

    def security_event(
        self,
        event_type: str,
        severity: str = "warning",
        description: str = "",
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        log_method = getattr(self.logger, severity.lower(), self.logger.warning)
        log_method(
            "Security event",
            extra={
                "audit_type": "security",
                "event_type": event_type,
                "description": description,
                "user_id": user_id,
                "ip_address": ip_address,
                "details": details or {},
            },
        )

    def data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str = "read",
        ip_address: Optional[str] = None,
    ):
        self.logger.info(
            "Data access",
            extra={
                "audit_type": "data_access",
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
                "ip_address": ip_address,
            },
        )


# Global instance
audit_log = AuditLogger()
