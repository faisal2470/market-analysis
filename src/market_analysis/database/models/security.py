"""
SQLAlchemy ORM model representing a tradable financial security.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from datetime import date

from sqlalchemy import Boolean, Enum, String, UniqueConstraint, Date, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from market_analysis.database.base import Base
from market_analysis.database.models.enums import Currency, Exchange, SecurityType, SecuritySeries, SecurityFields
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

    symbol:         Mapped[str]             = mapped_column(String(32),             nullable=False, index=True)
    name:           Mapped[str]             = mapped_column(String(256),            nullable=False)
    exchange:       Mapped[Exchange]        = mapped_column(Enum(Exchange),         nullable=False, index=True)
    security_type:  Mapped[SecurityType]    = mapped_column(Enum(SecurityType),     nullable=False, index=True)
    isin:           Mapped[str | None]      = mapped_column(String(32),             nullable=True,  unique=True)

    currency:       Mapped[Currency]        = mapped_column(Enum(Currency),         nullable=False, default=Currency.INR)
    active:         Mapped[bool]            = mapped_column(Boolean,                nullable=False, default=True, index=True)

    series:         Mapped[SecuritySeries]  = mapped_column(Enum(SecuritySeries),   nullable=True,  index=True)
    listing_date:   Mapped[date  | None]    = mapped_column(Date,                   nullable=True)
    face_value:     Mapped[float | None]    = mapped_column(Float,                  nullable=True)
    paid_up_value:  Mapped[float | None]    = mapped_column(Float,                  nullable=True)
    market_lot:     Mapped[int   | None]    = mapped_column(Integer,                nullable=True)

    synchronizable_fields: ClassVar[frozenset[SecurityFields]] = frozenset({
        SecurityFields.SYMBOL,
        SecurityFields.NAME,
        SecurityFields.EXCHANGE,
        SecurityFields.SECURITY_TYPE,
        SecurityFields.ISIN,
        SecurityFields.SERIES,
        SecurityFields.LISTING_DATE,
        SecurityFields.FACE_VALUE,
        SecurityFields.PAID_UP_VALUE,
        SecurityFields.MARKET_LOT,
        SecurityFields.CURRENCY,
        SecurityFields.ACTIVE,
    })

    @classmethod
    def is_synchronizable(cls, field: SecurityFields) -> bool:
        return field in cls.synchronizable_fields

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
            f"type='{self.security_type}', "
            f"isin='{self.isin}')"
        )

