from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import settings
from ..models.base import Base

# Determine connect args (SQLite needs check_same_thread=False)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Creates all database tables based on declarative models."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
