"""
Database engine utilities.

This module creates and exposes the SQLAlchemy Engine used throughout
the application.
"""

from __future__ import annotations

from sqlalchemy import Engine
from sqlalchemy import create_engine

from market_analysis.utils.constants import DATABASE_DIR
from market_analysis.utils.constants import DATABASE_URL


def create_database_engine() -> Engine:
    """
    Create the SQLAlchemy engine.

    Returns
    -------
    Engine
        Configured SQLAlchemy engine.
    """

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        DATABASE_URL,
        echo=False,
        future=True,
    )

    return engine


engine = create_database_engine()