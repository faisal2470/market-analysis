"""
Database CRUD utilities.

This module contains helper functions for interacting with the database.
Higher-level modules (e.g. history.py) should use these functions instead
of writing SQLAlchemy queries directly.
"""

from __future__ import annotations

from datetime import date
import pandas as pd
from dataclasses import dataclass, field
from collections.abc import Set

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from market_analysis.database.models.bars import DailyBar
from market_analysis.database.models.enums import Currency, Exchange, SecurityType, SecuritySeries, SecurityFields
from market_analysis.database.models.security import Security

# ============================================================================
# Classes
# ============================================================================

@dataclass(slots=True)
class SecurityUpsertSummary:
    """
    Summary of a security synchronization operation.
    """
    processed: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: int = 0

    errors: list[SecuritySyncError] = field(default_factory=list)

    @property
    def successful(self) -> int:
        """
        Return the number of successfully processed securities.
        """

        return self.inserted + self.updated + self.unchanged

    @property
    def success_rate(self) -> float:
        """
        Return the synchronization success rate.
        """

        if self.processed == 0:
            return 0.0

        return 100.0 * self.successful / self.processed

    def __str__(self) -> str:
        """
        Return a formatted synchronization summary.
        """

        lines = [
            "Security Synchronization Summary",
            "--------------------------------",
            f"Processed : {self.processed}",
            f"Inserted  : {self.inserted}",
            f"Updated   : {self.updated}",
            f"Unchanged : {self.unchanged}",
            f"Failed    : {self.failed}",
            f"Success   : {self.success_rate:.1f}%",
        ]

        if self.errors:
            lines.append("")
            lines.append("Errors:")

            for error in self.errors:
                lines.append(f"  - {error}")

        return "\n".join(lines)

@dataclass(slots=True)
class SecuritySyncError:
    symbol: str
    reason: str
    exception: Exception | None = None


# ============================================================================
# Private Helpers
# ============================================================================

def _should_update_field(current_value: object, incoming_value: object) -> bool:
    """
    Determine whether a security field should be updated.

    A field is updated only when the provider supplies a non-missing value
    that differs from the value currently stored in the database.

    Parameters
    ----------
    current_value
        Value currently stored in the database.

    incoming_value
        Value supplied by the provider.

    Returns
    -------
    bool
        True if the field should be updated.
    """

    if pd.isna(incoming_value):
        return False

    return current_value != incoming_value

def _update_security(security: Security, row: pd.Series, allowed_fields: Set[SecurityFields]) -> int:
    """
    Update an existing security from a canonical metadata row.

    Only fields listed in ``allowed_fields`` are considered. A field is
    updated only when the incoming value is non-missing and differs from the
    value currently stored in the database.

    Parameters
    ----------
    security
        Existing security stored in the database.

    row
        Canonical security metadata.

    allowed_fields
        Canonical fields permitted to be synchronized for this operation.

    Returns
    -------
    int
        Number of fields updated.
    """
    updated_fields = 0

    for field in allowed_fields:

        new_value = row[field]
        current_value = getattr(security, field.value)

        old = getattr(security, field.value)
        new = row[field]

        if old != new:
            print(field)
            print(type(old), repr(old))
            print(type(new), repr(new))
            print()

        if not _should_update_field(current_value, new_value):
            continue

        setattr(security, field.value, new_value)

        updated_fields += 1

    return updated_fields

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

def insert_security(session: Session, symbol: str, exchange: Exchange, *,
    name: str | None = None, isin: str | None = None, security_type: SecurityType = SecurityType.STOCK,
    currency: Currency = Currency.INR) -> Security:
    """
    Insert a new security with the minimum required metadata.

    This function is primarily intended for workflows where only the symbol
    and exchange are known (for example, downloading historical price data).
    Additional metadata may be synchronized later by the symbol
    synchronization pipeline.

    Parameters
    ----------
    session
        Active SQLAlchemy session.

    symbol
        Trading symbol.

    exchange
        Exchange on which the security trades.

    name
        Display name of the security. Defaults to the symbol.

    isin
        International Securities Identification Number.

    security_type
        Type of financial instrument.

    currency
        Trading currency.

    Returns
    -------
    Security
        Newly inserted security.
    """

    security = Security(symbol=symbol, name=name or symbol, exchange=exchange,
        security_type=security_type, isin=isin, currency=currency)

    session.add(security)
    session.flush()

    return security

def insert_security_from_row(session: Session, row: pd.Series) -> Security:
    """
    Insert a new security from a canonical security metadata row.

    Parameters
    ----------
    session
        Active SQLAlchemy session.

    row
        Canonical security metadata.

    Returns
    -------
    Security
        Newly inserted security.
    """

    security = Security(
        symbol          = row[SecurityFields.SYMBOL],
        name            = row[SecurityFields.NAME],
        exchange        = row[SecurityFields.EXCHANGE],
        security_type   = row[SecurityFields.SECURITY_TYPE],
        isin            = row[SecurityFields.ISIN],
        currency        = row[SecurityFields.CURRENCY],
        active          = row[SecurityFields.ACTIVE],
        series          = row[SecurityFields.SERIES],
        listing_date    = row[SecurityFields.LISTING_DATE],
        face_value      = row[SecurityFields.FACE_VALUE],
        paid_up_value   = row[SecurityFields.PAID_UP_VALUE],
        market_lot      = row[SecurityFields.MARKET_LOT],
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

    return insert_security(session=session, symbol=symbol, exchange=exchange, **kwargs)

def upsert_securities(session: Session, securities: pd.DataFrame, allowed_fields: Set[SecurityFields]) -> SecurityUpsertSummary:
    """
    Synchronize security metadata into the database.

    Parameters
    ----------
    session
        Active SQLAlchemy session.

    securities
        Canonical security metadata.

    allowed_fields
        Canonical fields permitted to be synchronized.

    Returns
    -------
    SecurityUpsertSummary
        Summary of the synchronization.
    """
    summary = SecurityUpsertSummary()

    for _, row in securities.iterrows():
        summary.processed += 1

        symbol      = row[SecurityFields.SYMBOL]
        exchange    = row[SecurityFields.EXCHANGE]

        try:
            security = get_security(session, symbol, exchange)
            if security is None:
                insert_security_from_row(session, row)
                summary.inserted += 1

            else:
                updated_fields = _update_security(security, row, allowed_fields)
                if updated_fields:
                    summary.updated += 1
                else:
                    summary.unchanged += 1

        except Exception as exc:
            session.rollback()
            summary.failed += 1

            summary.errors.append(SecuritySyncError(
                symbol=symbol,
                reason=str(exc),
                exception=exc
            ))

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise

    return summary


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
