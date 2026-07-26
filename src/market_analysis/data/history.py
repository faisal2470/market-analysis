"""
Historical market data management.

This module orchestrates downloading, validating, cleaning, storing,
and loading historical market data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import pandas as pd

from sqlalchemy.orm import Session

from market_analysis.data.processing import CleaningReport, ValidationReport, validate_daily_data, clean_daily_data
from market_analysis.data.providers import yahoo
from market_analysis.database.models.enums import DataProvider, Exchange
from market_analysis.database import ensure_security, store_daily_bars, delete_daily_bars, load_daily_bars, get_security, get_session

# ============================================================================
# Result Models
# ============================================================================


@dataclass(slots=True)
class HistoryUpdateResult:
    """
    Summary of a history update operation.
    """

    symbol:             str
    exchange:           Exchange
    provider:           DataProvider

    dataframe:          pd.DataFrame

    validation_report:  ValidationReport
    cleaning_report:    CleaningReport

    rows_downloaded:    int
    rows_after_cleaning:int
    rows_stored:        int


# ============================================================================
# Provider Registry
# ============================================================================


_PROVIDER_DOWNLOADERS = {
    DataProvider.YAHOO: yahoo.download_daily_history,
}

def _get_downloader(provider: DataProvider):
    """
    Return the download function for the selected provider.
    """
    try:
        return _PROVIDER_DOWNLOADERS[provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported data provider: {provider}") from exc


# ============================================================================
# Private Helpers
# ============================================================================


def _download_daily(symbol: str, exchange: Exchange, provider: DataProvider, *,
    start: date | None = None, end: date | None = None, period: str | None = None, interval: str = "1d") -> pd.DataFrame:
    """
    Download historical market data from the selected provider.
    """

    downloader = _get_downloader(provider)

    return downloader(
        symbol=symbol, exchange=exchange,
        start=start, end=end, period=period, interval=interval,
    )

def _validate(df: pd.DataFrame) -> ValidationReport:
    """
    Validate downloaded historical data.
    """

    return validate_daily_data(df)

def _clean(df: pd.DataFrame, *,
    sort_index: bool = True, remove_duplicate_index: bool = True, remove_duplicate_rows: bool = True,
    drop_missing_values: bool = False, remove_zero_volume: bool = False, convert_dtypes: bool = True,
) -> tuple[pd.DataFrame, CleaningReport]:
    """
    Clean downloaded historical data.
    """

    return clean_daily_data(
        df,
        sort_index=sort_index,
        remove_duplicate_index=remove_duplicate_index,
        remove_duplicate_rows=remove_duplicate_rows,
        drop_missing_values=drop_missing_values,
        remove_zero_volume=remove_zero_volume,
        convert_dtypes=convert_dtypes,
    )

def _store(session: Session, symbol: str, exchange: Exchange, dataframe: pd.DataFrame, *, overwrite: bool = False) -> int:
    """
    Store historical market data in the database.

    Parameters
    ----------
    session
        Active database session.
    symbol
        Security symbol.
    exchange
        Security exchange.
    dataframe
        Historical OHLCV data.
    overwrite
        Whether to delete existing history before storing.

    Returns
    -------
    int
        Number of rows written to the database.
    """

    security = ensure_security(session=session, symbol=symbol, exchange=exchange)

    if overwrite:
        delete_daily_bars(session=session, security_id=security.id)

    rows_written = store_daily_bars(session=session, security_id=security.id, dataframe=dataframe)

    return rows_written

def _load(session: Session, symbol: str, exchange: Exchange, *,
    start: date | None = None, end: date | None = None) -> pd.DataFrame:
    """
    Load historical market data from the database.

    Parameters
    ----------
    session
        Active database session.
    symbol
        Security symbol.
    exchange
        Security exchange.
    start
        Optional start date.
    end
        Optional end date.

    Returns
    -------
    DataFrame
        Historical OHLCV data.
    """

    security = get_security(session=session, symbol=symbol, exchange=exchange)

    if security is None:
        return pd.DataFrame()

    return load_daily_bars(session=session, security_id=security.id, start=start, end=end)


# ============================================================================
# Public APIs
# ============================================================================

def download_daily_history(symbol: str, exchange: Exchange, provider: DataProvider = DataProvider.YAHOO, *,
    start: date | None = None, end: date | None = None, period: str | None = None, interval: str = "1d") -> pd.DataFrame:
    """
    Download historical market data from a provider.

    This function does not validate, clean or store the data.
    """

    return _download_daily(
        symbol=symbol, exchange=exchange, provider=provider,
        start=start, end=end, period=period, interval=interval,
    )

def store_daily_history(symbol: str, exchange: Exchange, dataframe: pd.DataFrame, *, overwrite: bool = False) -> int:
    """
    Store historical market data in the database.

    Returns
    -------
    int
        Number of rows written.
    """

    with get_session() as session:
        try:
            rows_written = _store(session=session, symbol=symbol, exchange=exchange, dataframe=dataframe, overwrite=overwrite)

            session.commit()

            return rows_written

        except Exception:
            session.rollback()
            raise

def load_daily_history(symbol: str, exchange: Exchange, *, start: date | None = None, end: date | None = None) -> pd.DataFrame:
    """
    Load historical market data from the database.
    """

    with get_session() as session:

        return _load(session=session, symbol=symbol, exchange=exchange, start=start, end=end)

def update_daily_history(symbol: str, exchange: Exchange, provider: DataProvider = DataProvider.YAHOO, *,
    start: date | None = None, end: date | None = None, period: str | None = None, interval: str = "1d",
    overwrite: bool = False, convert_dtypes: bool = True,
    sort_index: bool = True, remove_duplicate_index: bool = True,
    remove_duplicate_rows: bool = True,
    drop_missing_values: bool = False,
    remove_zero_volume: bool = False,
) -> HistoryUpdateResult:
    """
    Download, validate, clean and store historical market data.
    """

    # -------------------------------------------------------------
    # Download
    # -------------------------------------------------------------

    dataframe = download_daily_history(
        symbol=symbol,
        exchange=exchange,
        provider=provider,
        start=start,
        end=end,
        period=period,
        interval=interval,
    )

    rows_downloaded = len(dataframe)

    # -------------------------------------------------------------
    # Validate
    # -------------------------------------------------------------

    validation_report = _validate(dataframe)

    # -------------------------------------------------------------
    # Clean
    # -------------------------------------------------------------

    dataframe, cleaning_report = _clean(
        dataframe,
        sort_index=sort_index,
        remove_duplicate_index=remove_duplicate_index,
        remove_duplicate_rows=remove_duplicate_rows,
        drop_missing_values=drop_missing_values,
        remove_zero_volume=remove_zero_volume,
        convert_dtypes=convert_dtypes,
    )

    rows_after_cleaning = len(dataframe)

    # -------------------------------------------------------------
    # Store
    # -------------------------------------------------------------

    rows_stored = store_daily_history(
        symbol=symbol,
        exchange=exchange,
        dataframe=dataframe,
        overwrite=overwrite,
    )

    # -------------------------------------------------------------
    # Result
    # -------------------------------------------------------------

    return HistoryUpdateResult(
        symbol=symbol,
        exchange=exchange,
        provider=provider,
        dataframe=dataframe,
        validation_report=validation_report,
        cleaning_report=cleaning_report,
        rows_downloaded=rows_downloaded,
        rows_after_cleaning=rows_after_cleaning,
        rows_stored=rows_stored,
    )

def refresh_daily_history(symbol: str, exchange: Exchange, provider: DataProvider = DataProvider.YAHOO, *, 
        remove_zero_volume: bool = False) -> HistoryUpdateResult:
    """
    Download and append only missing daily history.

    If the security is not yet present in the database,
    the complete available history is downloaded.
    """
    existing = load_daily_history(symbol=symbol, exchange=exchange)

    if existing.empty:

        return update_daily_history(
            symbol=symbol,
            exchange=exchange,
            provider=provider,
            period="max",
            overwrite=False,
            remove_zero_volume=remove_zero_volume,
        )

    latest_date = existing.index.max()

    return update_daily_history(
        symbol=symbol,
        exchange=exchange,
        provider=provider,
        start=latest_date + timedelta(days=1),
        overwrite=False,
        remove_zero_volume=remove_zero_volume,
    )




