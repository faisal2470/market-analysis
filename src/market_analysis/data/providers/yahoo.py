"""
Yahoo Finance data source.

This module provides helper functions for downloading historical market
data from Yahoo Finance.
"""

from __future__ import annotations


from datetime import date
from typing import ClassVar
import pandas as pd
import yfinance as yf

from market_analysis.exceptions import DataDownloadError, EmptyDataError, UnsupportedExchangeError
from market_analysis.database.models.enums import Exchange
from market_analysis.database.models import Security
from market_analysis.data.providers.capabilities import ProviderCapabilities
from market_analysis.data.providers.base import ProviderClient

class YahooClient(ProviderClient):
    """
    Client for downloading market data from Yahoo Finance.

    This client is responsible only for communicating with Yahoo Finance
    and returning canonical data structures. It performs no validation,
    cleaning, filtering, or database operations.
    """
    # ======================================================================
    # Construction
    # ======================================================================

    def __init__(self) -> None:
        """
        Initialize the Yahoo Finance client.
        """

        super().__init__()

    # ======================================================================
    # Class Variables
    # ======================================================================

    _EXCHANGE_SUFFIXES: ClassVar[dict[Exchange, str]]   = {Exchange.NSE: ".NS", Exchange.BSE: ".BO"}
    _CAPABILITIES:      ClassVar[ProviderCapabilities]  = ProviderCapabilities(supports_daily_history=True, supports_intraday_history=True)

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._CAPABILITIES

    # ========================================================================
    # Helpers
    # ========================================================================

    def _build_ticker(self, security: Security) -> str:
        """
        Build a Yahoo Finance ticker.
        """
        try:
            suffix = self._EXCHANGE_SUFFIXES[security.exchange]
        except KeyError as exc:
            raise UnsupportedExchangeError(
                f"Exchange '{security.exchange}' is not supported by Yahoo Finance."
            ) from exc

        return f"{security.symbol.upper()}{suffix}"

    # ========================================================================
    # Daily History
    # ========================================================================

    def _download_daily_history(self, security: Security, *,
        start: date | None = None, end: date | None = None, period: str | None = None,
        auto_adjust: bool = False) -> pd.DataFrame:
        """
        Download raw daily historical OHLCV data.
        """

        ticker = self._build_ticker(security)

        try:
            data = yf.download(ticker,
                start       = start,
                end         = end,
                period      = period,
                interval    = "1d",
                auto_adjust = auto_adjust,
                progress    = False,
                actions     = False,
            )
        except Exception as exc:
            raise DataDownloadError(f"Failed to download '{ticker}' from Yahoo Finance.") from exc

        if data.empty:
            raise EmptyDataError(f"No historical data returned for '{ticker}'.")

        return data

    def _canonicalize_daily_history(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Yahoo Finance daily history into the project's canonical format.
        """
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel("Ticker")

        data.index.name = "Date"

        return data.copy()

    # ========================================================================
    # Intraday History
    # ========================================================================

    def _download_intraday_history(self, security: Security, *,
        interval: str = "5m", period: str = "5d",
        auto_adjust: bool = False) -> pd.DataFrame:
        """
        Download raw intraday OHLCV data.
        """
        ticker = self._build_ticker(security)

        try:
            data = yf.download(ticker,
                interval    = interval,
                period      = period,
                auto_adjust = auto_adjust,
                progress    = False,
                actions     = False,
            )
        except Exception as exc:
            raise DataDownloadError(f"Failed to download '{ticker}' from Yahoo Finance.") from exc

        if data.empty:
            raise EmptyDataError(f"No intraday data returned for '{ticker}'.")

        return data

    def _canonicalize_intraday_history(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Yahoo Finance intraday history into the project's canonical format.
        """
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel("Ticker")

        data.index.name = "Date"

        return data.copy()
