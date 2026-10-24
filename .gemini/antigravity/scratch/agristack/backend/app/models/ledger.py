import uuid
import hashlib
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Numeric, Integer, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base

class LedgerTransactionType(str, Enum):
    GENESIS_ISSUANCE = "GENESIS_ISSUANCE"
    SHARE_PURCHASE = "SHARE_PURCHASE"
    SECONDARY_TRANSFER = "SECONDARY_TRANSFER"
    ESCROW_PAYOUT = "ESCROW_PAYOUT"
    SETTLEMENT_DISTRIBUTION = "SETTLEMENT_DISTRIBUTION"

class OwnershipLedger(Base):
    __tablename__ = "ownership_ledger"

    sequence_id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    
    # Cryptographic Hash Chain Linkage
    prev_hash = Column(String(64), nullable=False)  # 64 hex characters (SHA-256)
    entry_hash = Column(String(64), unique=True, nullable=False, index=True)
    
    transaction_type = Column(String(50), nullable=False)
    from_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    shares_count = Column(Integer, nullable=False)
    price_per_share_inr = Column(Numeric(10, 2), nullable=False)
    total_amount_inr = Column(Numeric(12, 2), nullable=False)
    
    # Nonce / digital signature / HMAC
    signature = Column(String(512), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="ownership_ledger_entries")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])

    @staticmethod
    def format_timestamp(ts) -> str:
        """Converts datetime to consistent ISO string ignoring microsecond/driver variations."""
        if isinstance(ts, str):
            return ts
        if hasattr(ts, "strftime"):
            return ts.strftime("%Y-%m-%d %H:%M:%S")
        return str(ts)

    @staticmethod
    def compute_hash(prev_hash: str, entry_id: str, project_id: str, from_user_id: str,
                     to_user_id: str, shares: int, amount: float, timestamp) -> str:
        """Computes deterministic SHA-256 hash for ledger entry."""
        ts_str = OwnershipLedger.format_timestamp(timestamp)
        payload = f"{prev_hash}|{entry_id}|{project_id}|{from_user_id or 'NULL'}|{to_user_id}|{shares}|{amount:.2f}|{ts_str}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
