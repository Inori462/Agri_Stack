import uuid
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
from ..models.ledger import OwnershipLedger, LedgerTransactionType
from ..core.config import settings
from ..core.exceptions import LedgerIntegrityError

GENESIS_PREV_HASH = "0" * 64

class LedgerService:
    """
    Append-only Cryptographic Hash-Chain Ledger Service for Digital Share Ownership.
    Guarantees strict tamper-evidence: every block cryptographically anchors the entire prior history.
    """

    @staticmethod
    def _generate_signature(entry_hash: str) -> str:
        """Generates server HMAC-SHA256 signature for the entry hash to guarantee provenance."""
        return hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            entry_hash.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def append_entry(
        db: Session,
        project_id: uuid.UUID,
        transaction_type: Optional[str] = None,
        to_user_id: Optional[uuid.UUID] = None,
        shares_count: Optional[int] = None,
        price_per_share: float = 0.0,
        total_amount: float = 0.0,
        from_user_id: Optional[uuid.UUID] = None,
        entry_type: Optional[str] = None,
        actor_id: Optional[uuid.UUID] = None,
        num_shares: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OwnershipLedger:
        """
        Appends a new immutable entry to the project ownership ledger.
        Retrieves the latest entry to link the hash chain.
        """
        transaction_type = transaction_type or entry_type or "LEDGER_ENTRY"
        to_user_id = to_user_id or actor_id
        shares_count = shares_count if shares_count is not None else (num_shares or 0)
        # Fetch latest entry for the project
        latest_entry = (
            db.query(OwnershipLedger)
            .filter(OwnershipLedger.project_id == project_id)
            .order_by(OwnershipLedger.sequence_id.desc())
            .first()
        )

        prev_hash = latest_entry.entry_hash if latest_entry else GENESIS_PREV_HASH
        entry_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        timestamp_iso = now.isoformat()

        # Compute deterministic cryptographic SHA-256 hash
        entry_hash = OwnershipLedger.compute_hash(
            prev_hash=prev_hash,
            entry_id=str(entry_id),
            project_id=str(project_id),
            from_user_id=str(from_user_id) if from_user_id else None,
            to_user_id=str(to_user_id),
            shares=shares_count,
            amount=total_amount,
            timestamp=now
        )

        signature = LedgerService._generate_signature(entry_hash)

        ledger_entry = OwnershipLedger(
            entry_id=entry_id,
            project_id=project_id,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
            transaction_type=transaction_type,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            shares_count=shares_count,
            price_per_share_inr=price_per_share,
            total_amount_inr=total_amount,
            signature=signature,
            timestamp=now
        )

        db.add(ledger_entry)
        db.commit()
        db.refresh(ledger_entry)
        return ledger_entry

    @staticmethod
    def verify_project_chain_integrity(db: Session, project_id: uuid.UUID) -> Tuple[bool, List[str]]:
        """
        Verifies the cryptographic integrity of the entire ownership chain for a project.
        Traverses sequentially from genesis to tip, verifying:
        1. prev_hash matches the previous record's entry_hash
        2. recalculated hash matches the stored entry_hash
        3. digital signature is valid
        Returns (is_valid, error_logs)
        """
        entries = (
            db.query(OwnershipLedger)
            .filter(OwnershipLedger.project_id == project_id)
            .order_by(OwnershipLedger.sequence_id.asc())
            .all()
        )

        if not entries:
            return True, ["No ledger entries found (genesis not initiated)"]

        errors: List[str] = []
        expected_prev_hash = GENESIS_PREV_HASH

        for idx, entry in enumerate(entries):
            # Check 1: Chain linkage
            if entry.prev_hash != expected_prev_hash:
                errors.append(
                    f"Chain broken at sequence #{entry.sequence_id}: "
                    f"expected prev_hash '{expected_prev_hash[:12]}...', got '{entry.prev_hash[:12]}...'"
                )

            # Check 2: Hash recalculation
            recomputed = OwnershipLedger.compute_hash(
                prev_hash=entry.prev_hash,
                entry_id=str(entry.entry_id),
                project_id=str(entry.project_id),
                from_user_id=str(entry.from_user_id) if entry.from_user_id else None,
                to_user_id=str(entry.to_user_id),
                shares=entry.shares_count,
                amount=float(entry.total_amount_inr),
                timestamp=entry.timestamp
            )

            if recomputed != entry.entry_hash:
                errors.append(
                    f"Data tampering detected at sequence #{entry.sequence_id} (entry_id {entry.entry_id}): "
                    f"stored hash '{entry.entry_hash[:12]}...' != recomputed '{recomputed[:12]}...'"
                )

            # Check 3: Signature verification
            expected_sig = LedgerService._generate_signature(entry.entry_hash)
            if entry.signature != expected_sig:
                errors.append(f"Invalid signature detected at sequence #{entry.sequence_id}")

            expected_prev_hash = entry.entry_hash

        is_valid = len(errors) == 0
        return is_valid, errors
