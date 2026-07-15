"""
Reusable SQLAlchemy ORM mixins.

This module defines abstract mixins that provide commonly used columns
and functionality shared across multiple ORM models.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column


class EntityMixin:
    """
    Mixin providing an auto-incrementing integer primary key and an automatic creation and modification timestamps.

    All timestamps are stored in UTC.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

class OHCLVBarMixin:
    """
    Mixin providing common market price columns.

    This mixin is intended for tables storing market price history,
    such as daily and intraday prices.
    """

    open:   Mapped[float] = mapped_column(Float, nullable=False)

    high:   Mapped[float] = mapped_column(Float, nullable=False)

    low:    Mapped[float] = mapped_column(Float, nullable=False)

    close:  Mapped[float] = mapped_column(Float, nullable=False)

    volume: Mapped[float] = mapped_column(Float, nullable=False)


