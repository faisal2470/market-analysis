"""
SQLAlchemy ORM models representing historical market bars.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from market_analysis.database.base import Base
from market_analysis.database.models.enums import TimeInterval
from market_analysis.database.models.mixins import OHCLVBarMixin, EntityMixin

if TYPE_CHECKING:
    from market_analysis.database.models.security import Security

class DailyBar(EntityMixin, OHCLVBarMixin, Base):
    """
    Daily OHLCV bar for a security.
    """

    __tablename__ = "daily_bars"

    __table_args__ = (
        UniqueConstraint("security_id", "date", name="uq_daily_bar_security_date"),
    )

    security_id:    Mapped[int]             = mapped_column(ForeignKey("securities.id", ondelete="CASCADE"), nullable=False, index=True)
    date:           Mapped[date]            = mapped_column(Date, nullable=False, index=True)
    adj_close:      Mapped[float | None]    = mapped_column(Float, nullable=True)

    security:       Mapped["Security"]      = relationship(back_populates="daily_price_history", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"DailyBar("
            f"security_id={self.security_id}, "
            f"date={self.date}, "
            f"close={self.close})"
        )

class IntradayBar(EntityMixin, OHCLVBarMixin, Base):
    """
    Intraday OHLCV bar for a security.
    """

    __tablename__ = "intraday_bars"

    __table_args__ = (
        UniqueConstraint("security_id", "timestamp", "interval", name="uq_intraday_bar_security_timestamp_interval"),
    )

    security_id:    Mapped[int]             = mapped_column(ForeignKey("securities.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp:      Mapped[datetime]        = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    interval:       Mapped[TimeInterval]    = mapped_column(Enum(TimeInterval), nullable=False, index=True)

    security:       Mapped["Security"] = relationship(back_populates="intraday_price_history", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"IntradayBar("
            f"security_id={self.security_id}, "
            f"timestamp={self.timestamp}, "
            f"interval={self.interval}, "
            f"close={self.close})"
        )


