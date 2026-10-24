from typing import List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...models.ledger import OwnershipLedger
from ...schemas.share import LedgerEntryResponse, LedgerIntegrityResponse
from ...services.ledger_service import LedgerService
from ...services.audit_service import AuditService

router = APIRouter(prefix="/ledger", tags=["Cryptographic Ownership Ledger"])

@router.get("/project/{project_id}", response_model=List[LedgerEntryResponse])
def get_project_ledger_history(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the immutable, chronological chain of ownership transactions for a given farm project.
    """
    entries = (
        db.query(OwnershipLedger)
        .filter(OwnershipLedger.project_id == project_id)
        .order_by(OwnershipLedger.sequence_id.asc())
        .all()
    )
    return entries

@router.get("/verify-integrity/{project_id}", response_model=LedgerIntegrityResponse)
def verify_ledger_cryptographic_integrity(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validates SHA-256 hash chaining and signatures for the entire project ledger.
    Traverses from genesis block to the tip of the chain to detect any tampering or retroactive modifications.
    """
    is_valid, errors = LedgerService.verify_project_chain_integrity(db, project_id)
    
    entries_count = (
        db.query(OwnershipLedger)
        .filter(OwnershipLedger.project_id == project_id)
        .count()
    )

    if not is_valid:
        AuditService.record_security_alert(
            db=db,
            alert_type="LEDGER_TAMPER_DETECTED",
            severity="CRITICAL",
            details={
                "project_id": str(project_id),
                "errors": errors,
                "audited_by": str(current_user.id)
            }
        )

    return LedgerIntegrityResponse(
        project_id=project_id,
        is_valid=is_valid,
        entries_audited=entries_count,
        error_count=len(errors) if not is_valid else 0,
        errors=errors if not is_valid else [],
        audit_timestamp=datetime.now(timezone.utc)
    )
