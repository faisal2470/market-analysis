"""
Database session utilities.

This module provides a SQLAlchemy session factory for interacting
with the database.
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from market_analysis.database.engine import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_session() -> Session:
    """
    Create a new database session.

    Returns
    -------
    Session
        SQLAlchemy database session.
    """

    return SessionLocal()