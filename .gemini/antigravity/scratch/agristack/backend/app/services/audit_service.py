import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import Request
from ..models.audit import AuditLog, SecurityAlert

class AuditService:
    """Service for recording tamper-evident audit trails and security alerts."""

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        resource_type: str,
        resource_id: str,
        actor_role: str = "SYSTEM",
        actor_id: Optional[uuid.UUID] = None,
        ip_address: str = "127.0.0.1",
        user_agent: str = "AgriStack-Client",
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Records an immutable audit event."""
        log_entry = AuditLog(
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            ip_address=ip_address,
            user_agent=user_agent[:250],
            details=details or {}
        )
        db.add(log_entry)
        db.commit()
        return log_entry

    @staticmethod
    def record_security_alert(
        db: Session,
        alert_type: str,
        severity: str,
        details: Dict[str, Any]
    ) -> SecurityAlert:
        """Records a security alert (e.g. tampering or duplicate survey number)."""
        alert = SecurityAlert(
            alert_type=alert_type,
            severity=severity,
            details=details
        )
        db.add(alert)
        db.commit()
        return alert
