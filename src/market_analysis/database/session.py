"""
Database session utilities.

This module provides a SQLAlchemy session factory for interacting
with the database.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from market_analysis.database.engine import engine

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Create a managed database session.

    Yields
    ------
    Session
        SQLAlchemy database session.

    Examples
    --------
    >>> with get_session() as session:
    ...     ...
    """

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


