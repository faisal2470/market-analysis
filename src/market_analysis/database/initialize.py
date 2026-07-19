"""
Database initialization utilities.

This module provides helper functions for creating, dropping, and
resetting the database schema.
"""

from __future__ import annotations

# Import all ORM models so they are registered with SQLAlchemy.
import market_analysis.database.models

from market_analysis.database.base import Base
from market_analysis.database.engine import engine

def create_database() -> None:
    """
    Create all database tables.

    Existing tables are left unchanged.
    """

    Base.metadata.create_all(bind=engine)

def drop_database() -> None:
    """
    Drop all database tables.

    This operation permanently deletes all stored data.
    """

    Base.metadata.drop_all(bind=engine)

def reset_database() -> None:
    """
    Reset the database schema.

    This operation drops all existing tables and recreates them.
    """

    drop_database()
    create_database()

