"""
SQLAlchemy declarative base.

All ORM models should inherit from the Base class defined here.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """

    pass