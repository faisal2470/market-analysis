"""
SQLAlchemy ORM model representing a tradable financial security.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from market_analysis.database.base import Base
from market_analysis.database.models.enums import Currency, Exchange, SecurityType
from market_analysis.database.models.mixins import EntityMixin

if TYPE_CHECKING:
    from market_analysis.database.models.bars import DailyBar
    from market_analysis.database.models.bars import IntradayBar
    from market_analysis.database.models.watchlist import WatchlistItem

class Security(EntityMixin, Base):
    """
    ORM model representing a tradable financial security.

    This table acts as the master reference for all securities stored in
    the database. Historical prices, watchlists, and future datasets
    reference this table through foreign keys.
    """

    __tablename__ = "securities"

    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="uq_security_symbol_exchange"),
    )

    symbol:         Mapped[str]             = mapped_column(String(32), nullable=False, index=True)
    name:           Mapped[str]             = mapped_column(String(256), nullable=False)
    exchange:       Mapped[Exchange]        = mapped_column(Enum(Exchange), nullable=False, index=True)
    security_type:  Mapped[SecurityType]    = mapped_column(Enum(SecurityType), nullable=False, index=True)
    isin:           Mapped[str | None]      = mapped_column(String(32), nullable=True, unique=True)

    sector:         Mapped[str | None]      = mapped_column(String(128), nullable=True)
    industry:       Mapped[str | None]      = mapped_column(String(128), nullable=True)
    currency:       Mapped[Currency]        = mapped_column(Enum(Currency), nullable=False, default=Currency.INR)
    active:         Mapped[bool]            = mapped_column(Boolean, nullable=False, default=True, index=True)

    daily_price_history:    Mapped[list["DailyBar"]]        = relationship(back_populates="security", cascade="all, delete-orphan", lazy="selectin")
    intraday_price_history: Mapped[list["IntradayBar"]]     = relationship(back_populates="security", cascade="all, delete-orphan", lazy="selectin")
    watchlist_items:        Mapped[list["WatchlistItem"]]   = relationship(back_populates="security", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self) -> str:
        """
        Return a concise string representation of the security.
        """

        return (
            f"Security("
            f"id={self.id}, "
            f"symbol='{self.symbol}', "
            f"exchange='{self.exchange}', "
            f"type='{self.security_type}')"
        )

