import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Column, Uuid
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TimestampMixin:
    """Provides created_at and updated_at timestamps for all models."""
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
