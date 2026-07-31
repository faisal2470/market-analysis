"""
Database CRUD utilities.

This module contains helper functions for interacting with the database.
Higher-level modules (e.g. history.py) should use these functions instead
of writing SQLAlchemy queries directly.
"""

from __future__ import annotations

from datetime import date
import pandas as pd

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from market_analysis.database.models.bars import DailyBar
from market_analysis.database.models.enums import Currency, Exchange, SecurityType
from market_analysis.database.models.security import Security

# ============================================================================
# Security
# ============================================================================

def get_security(session: Session, symbol: str, exchange: Exchange) -> Security | None:
    """
    Return a security if it exists.
    """

    statement = (
        select(Security)
        .where(Security.symbol == symbol)
        .where(Security.exchange == exchange)
    )

    return session.scalar(statement)

def create_security(session: Session, symbol: str, exchange: Exchange, *,
        name: str | None = None, isin: str | None = None,
        security_type: SecurityType = SecurityType.STOCK, currency: Currency = Currency.INR
    ) -> Security:
    """
    Create a new security.
    """

    security = Security(
        symbol=symbol, exchange=exchange, name=name or symbol,
        isin=isin, security_type=security_type, currency=currency
    )

    session.add(security)
    session.flush()

    return security

def ensure_security(session: Session, symbol: str, exchange: Exchange, **kwargs) -> Security:
    """
    Return an existing security or create it.
    """

    security = get_security(session=session, symbol=symbol, exchange=exchange)
    if security is not None:
        return security

    return create_security(session=session, symbol=symbol, exchange=exchange, **kwargs)


# ============================================================================
# Daily Bars
# ============================================================================

def delete_daily_bars(session: Session, security_id: int) -> None:
    """
    Delete all daily bars for a security.
    """

    session.execute(
        delete(DailyBar).where(
            DailyBar.security_id == security_id
        )
    )

def store_daily_bars(session: Session, security_id: int, dataframe: pd.DataFrame) -> int:
    """
    Insert daily bars.

    Returns
    -------
    int
        Number of inserted rows.
    """

    rows = []

    for timestamp, row in dataframe.iterrows():

        rows.append(
            DailyBar(
                security_id=security_id,
                date=timestamp.date(),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                adj_close=float(
                    row.get("Adj Close", row["Close"])
                ),
                volume=float(row["Volume"]),
            )
        )

    session.add_all(rows)

    return len(rows)

def load_daily_bars(session: Session, security_id: int, *, start: date | None = None, end: date | None = None) -> pd.DataFrame:
    """
    Load daily bars into a DataFrame.
    """

    statement = (
        select(DailyBar)
        .where(DailyBar.security_id == security_id)
        .order_by(DailyBar.date)
    )

    if start is not None:
        statement = statement.where(DailyBar.date >= start)

    if end is not None:
        statement = statement.where(DailyBar.date <= end)

    bars = session.scalars(statement).all()

    if not bars:
        return pd.DataFrame()

    df = pd.DataFrame(
        {
            "Date":         [bar.date for bar in bars],
            "Open":         [bar.open for bar in bars],
            "High":         [bar.high for bar in bars],
            "Low":          [bar.low for bar in bars],
            "Close":        [bar.close for bar in bars],
            "Adj Close":    [bar.adj_close for bar in bars],
            "Volume":       [bar.volume for bar in bars],
        }
    )

    return df.set_index("Date")

def get_daily_bar_dates(session: Session, security_id: int) -> pd.DatetimeIndex:
    """
    Return all stored daily bar dates for a security.

    Parameters
    ----------
    session
        Database session.
    security_id
        Security primary key.

    Returns
    -------
    DatetimeIndex
        Sorted index of stored trading dates.
    """
    stmt = (
        select(DailyBar.date)
        .where(DailyBar.security_id == security_id)
        .order_by(DailyBar.date)
    )

    dates = session.scalars(stmt).all()

    return pd.DatetimeIndex(dates)
