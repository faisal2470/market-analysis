"""
SQLAlchemy ORM models representing user watchlists.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from market_analysis.database.base import Base
from market_analysis.database.models.mixins import EntityMixin

if TYPE_CHECKING:
    from market_analysis.database.models.security import Security


class Watchlist(EntityMixin, Base):
    """
    A named collection of securities.
    """
    __tablename__ = "watchlists"

    name:           Mapped[str]                     = mapped_column(String(128), nullable=False, unique=True, index=True)
    description:    Mapped[str | None]              = mapped_column(Text, nullable=True)
    active:         Mapped[bool]                    = mapped_column(Boolean, nullable=False, default=True)

    items:          Mapped[list["WatchlistItem"]]   = relationship(back_populates="watchlist", cascade="all, delete-orphan", lazy="selectin")

    @property
    def size(self) -> int:
        return len(self.items)

    def __repr__(self) -> str:
        return (
            f"Watchlist("
            f"id={self.id}, "
            f"name='{self.name}')"
        )
    
class WatchlistItem(EntityMixin, Base):
    """
    Association between a watchlist and a security.
    """
    __tablename__ = "watchlist_items"

    __table_args__ = (
        UniqueConstraint("watchlist_id", "security_id", name="uq_watchlist_item"),
    )

    watchlist_id:   Mapped[int]         = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True)
    security_id:    Mapped[int]         = mapped_column(ForeignKey("securities.id", ondelete="CASCADE"), nullable=False, index=True)

    watchlist:      Mapped["Watchlist"] = relationship(back_populates="items", lazy="selectin")
    security:       Mapped["Security"]  = relationship(back_populates="watchlist_items", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"WatchlistItem("
            f"watchlist_id={self.watchlist_id}, "
            f"security_id={self.security_id})"
        )
