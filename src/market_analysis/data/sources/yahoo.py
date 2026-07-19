"""
Yahoo Finance data source.

This module provides helper functions for downloading historical market
data from Yahoo Finance.
"""

from __future__ import annotations
from market_analysis.exceptions import UnsupportedExchangeError, EmptyDataError, DataDownloadError

from datetime import date

import pandas as pd
import yfinance as yf

from market_analysis.database.models.enums import Exchange

_YAHOO_EXCHANGE_SUFFIXES: dict[Exchange, str] = {
    Exchange.NSE: ".NS",
    Exchange.BSE: ".BO",
}

def build_ticker(symbol: str, exchange: Exchange) -> str:
    """
    Build a Yahoo Finance ticker.

    Parameters
    ----------
    symbol
        Exchange trading symbol.
    exchange
        Exchange on which the security trades.

    Returns
    -------
    str
        Yahoo Finance ticker.
    """

    try:
        suffix = _YAHOO_EXCHANGE_SUFFIXES[exchange]
    except KeyError as exc:
        raise UnsupportedExchangeError(
            f"Exchange '{exchange}' is not supported by Yahoo Finance."
        ) from exc

    return f"{symbol.upper()}{suffix}"

def download_daily_history(
    symbol: str,
    exchange: Exchange,
    *,
    start: date | None = None,
    end: date | None = None,
    period: str | None = None,
    auto_adjust: bool = False,
) -> pd.DataFrame:
    """
    Download daily historical OHLCV data.

    Exactly one of ``period`` or ``start`` should normally be supplied.

    Parameters
    ----------
    symbol
        Trading symbol.
    exchange
        Exchange on which the security trades.
    start
        Start date.
    end
        End date.
    period
        Yahoo Finance period string (e.g. "1y", "5y", "max").
    auto_adjust
        Whether Yahoo should automatically adjust OHLC prices.

    Returns
    -------
    pandas.DataFrame
        Historical OHLCV data.
    """

    ticker = build_ticker(symbol, exchange)

    try:
        data = yf.download(
            ticker,
            start=start,
            end=end,
            period=period,
            interval="1d",
            auto_adjust=auto_adjust,
            progress=False,
            actions=False,
        )
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel("Ticker")
    except Exception as exc:
        raise DataDownloadError(
            f"Failed to download '{ticker}' from Yahoo Finance."
        ) from exc

    if data.empty:
        raise EmptyDataError(
            f"No historical data returned for '{ticker}'."
        )

    data.index.name = "Date"

    return data

def download_intraday_history(
    symbol: str,
    exchange: Exchange,
    *,
    interval: str = "5m",
    period: str = "5d",
    auto_adjust: bool = False,
) -> pd.DataFrame:
    """
    Download intraday historical data.

    Parameters
    ----------
    symbol
        Trading symbol.
    exchange
        Exchange on which the security trades.
    interval
        Yahoo Finance interval.
    period
        Yahoo Finance period.
    auto_adjust
        Whether Yahoo should automatically adjust OHLC prices.

    Returns
    -------
    pandas.DataFrame
        Intraday OHLCV data.
    """

    ticker = build_ticker(symbol, exchange)

    try:
        data = yf.download(
            ticker,
            interval=interval,
            period=period,
            auto_adjust=auto_adjust,
            progress=False,
            actions=False,
        )
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel("Ticker")
    except Exception as exc:
        raise DataDownloadError(
            f"Failed to download '{ticker}' from Yahoo Finance."
        ) from exc

    if data.empty:
        raise EmptyDataError(
            f"No intraday data returned for '{ticker}'."
        )

    return data






