import uuid
import pytest
from sqlalchemy.orm import Session
from app.services.ledger_service import LedgerService, GENESIS_PREV_HASH
from app.models.ledger import OwnershipLedger, LedgerTransactionType
from app.models.user import User, UserRole

def test_cryptographic_ledger_chain_and_tamper_detection(db_session: Session):
    project_id = uuid.uuid4()
    
    # 1. Create two users
    farmer = User(
        email="farmer.kisan@example.com",
        phone_number="+919876500001",
        hashed_password="hash",
        full_name="Kisan Farmer",
        primary_role=UserRole.FARMER.value
    )
    investor = User(
        email="investor.arun@example.com",
        phone_number="+919876500002",
        hashed_password="hash",
        full_name="Arun Investor",
        primary_role=UserRole.INVESTOR.value
    )
    db_session.add_all([farmer, investor])
    db_session.commit()

    # 2. Block 1: Genesis Issuance (Farmer 30 shares)
    b1 = LedgerService.append_entry(
        db=db_session,
        project_id=project_id,
        transaction_type=LedgerTransactionType.GENESIS_ISSUANCE.value,
        to_user_id=farmer.id,
        shares_count=30,
        price_per_share=1000.0,
        total_amount=30000.0,
        from_user_id=None
    )
    assert b1.prev_hash == GENESIS_PREV_HASH
    assert len(b1.entry_hash) == 64

    # 3. Block 2: Share Purchase (Investor 10 shares)
    b2 = LedgerService.append_entry(
        db=db_session,
        project_id=project_id,
        transaction_type=LedgerTransactionType.SHARE_PURCHASE.value,
        to_user_id=investor.id,
        shares_count=10,
        price_per_share=1000.0,
        total_amount=10000.0,
        from_user_id=farmer.id
    )
    # Block 2 must point to Block 1's entry hash
    assert b2.prev_hash == b1.entry_hash

    # 4. Verify chain integrity: Should be pristine!
    is_valid, errors = LedgerService.verify_project_chain_integrity(db_session, project_id)
    assert is_valid is True
    assert len(errors) == 0

    # 5. Simulate malicious tampering: silently mutate b1's share count directly in database
    b1.shares_count = 999  # Attacker tries to falsely inflate their shares
    db_session.commit()

    # 6. Re-verify integrity: Tamper detection must catch it immediately!
    is_valid_after_tamper, errors_after_tamper = LedgerService.verify_project_chain_integrity(db_session, project_id)
    assert is_valid_after_tamper is False
    assert len(errors_after_tamper) > 0
    assert any("Data tampering detected" in err for err in errors_after_tamper)
