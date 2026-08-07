"""
Abstract base class for all market data providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from datetime import date
import pandas as pd

from market_analysis.data.providers.capabilities import ProviderCapabilities
from market_analysis.data.processing import normalize_symbol_values
from market_analysis.database.models import Security

class ProviderClient(ABC):
    """
    Abstract base class for all market data providers.

    A provider is responsible only for communicating with an external
    data source and returning canonical data structures.

    Providers never perform validation, cleaning, storage, or any other
    database-related operations.
    """

    # ========================================================================
    # Capabilities
    # ========================================================================

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """
        Return the capabilities supported by this provider.
        """
        pass

    # ========================================================================
    # Symbols
    # ========================================================================

    def _download_symbols(self) -> pd.DataFrame:
        """
        Download raw security metadata from the provider.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support symbols metadata."
        )

    def _canonicalise_symbols(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert provider-specific symbol data into the project's canonical schema.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support symbols metadata."
        )

    def fetch_symbols(self) -> pd.DataFrame:
        """
        Download and canonicalize security metadata.
        """

        data = self._download_symbols()
        data = self._canonicalise_symbols(data)
        data = normalize_symbol_values(data)

        return data

    # ========================================================================
    # Daily History
    # ========================================================================

    def _download_daily_history(self, *args, **kwargs) -> pd.DataFrame:
        """
        Download raw daily historical data.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support daily history."
        )

    def _canonicalize_daily_history(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert provider-specific daily history into the project's canonical schema.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support daily history."
        )

    def fetch_daily_history(self, security: Security, *,
        start: date | None = None, end: date | None = None, period: str | None = None,
        auto_adjust: bool = False) -> pd.DataFrame:
            """
            Download and canonicalize daily historical price data.
            """
            data = self._download_daily_history(
                security    = security,
                start       = start,
                end         = end,
                period      = period,
                auto_adjust = auto_adjust,
            )
            data = self._canonicalize_daily_history(data)
    
            return data

    # ========================================================================
    # Intraday History
    # ========================================================================

    def _download_intraday_history(self, *args, **kwargs) -> pd.DataFrame:
        """
        Download raw intraday historical data.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} does not support intraday history."
        )

    def _canonicalize_intraday_history(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert provider-specific intraday history into the project's canonical schema.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} does not support intraday history."
        )

    def fetch_intraday_history(self, security: Security, *,
        interval: str | None = "5m", start: date | None = None, end: date | None = None, period: str | None = "5d",
        auto_adjust: bool = False) -> pd.DataFrame:
        """
        Download and canonicalize intraday historical price data.
        """

        data = self._download_intraday_history(
            security    = security,
            interval    = interval,
            start       = start,
            end         = end,
            period      = period,
            auto_adjust = auto_adjust,
        )
        data = self._canonicalize_intraday_history(data)

        return data




