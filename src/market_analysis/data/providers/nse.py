"""
NSE data provider.

This module provides direct access to data published by the National Stock
Exchange of India (NSE).

Currently supported
-------------------
- Equity symbol master

Future support
--------------
- Historical prices
- Intraday prices
- Company information
- Corporate actions
- Trading holidays
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import requests
from collections.abc import Iterable

from market_analysis.database.models.enums import SecurityFields, SecuritySeries, Exchange, SecurityType, Currency
from market_analysis.exceptions.data import NSEAuthenticationError, NSEResponseError, NSEError, NSEConnectionError, NSETimeoutError
from market_analysis.utils.constants import (
    NSE_BASE_URL,
    NSE_EQUITY_MASTER_URL,
    NSE_REQUEST_TIMEOUT,
)
from market_analysis.data.processing import normalize_symbol_values, filter_symbol_series
from market_analysis.data.providers.capabilities import ProviderCapabilities

class NSEClient:
    """
    HTTP client for communicating with the National Stock Exchange.

    The client owns a persistent HTTP session so that cookies,
    headers and TCP connections can be reused across requests.

    Notes
    -----
    This class is responsible only for communication with NSE.
    It performs no validation, cleaning or database operations.
    """
    # ======================================================================
    # Construction
    # ======================================================================

    def __init__(self, *, timeout: int = NSE_REQUEST_TIMEOUT) -> None:
        self.timeout = timeout
        self.session = requests.Session()

        self._initialized = False

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def capabilities(self) -> ProviderCapabilities:
        """
        Return the metadata describing the information supplied by this provider.

        The returned capabilities are immutable and define which canonical
        security fields may be synchronized into the database.
        """

        return self._CAPABILITIES

    # ======================================================================
    # Session Management
    # ======================================================================

    @staticmethod
    def _build_headers() -> dict[str, str]:
        """
        Build the default HTTP headers used for all NSE requests.

        These headers make the request appear similar to one originating
        from a modern web browser.
        """

        return {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/138.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Referer": NSE_BASE_URL,
        }

    def _ensure_session(self) -> None:
        """
        Initialise the HTTP session.

        The first request to the NSE homepage establishes any cookies
        required by subsequent requests.

        Calling this function multiple times is safe.
        """

        if self._initialized:
            return

        self.session.close()
        self.session = requests.Session()
        self.session.headers.update(self._build_headers())

        response = self.session.get(NSE_BASE_URL, timeout=self.timeout)

        response.raise_for_status()

        self._initialized = True

    def _reset_session(self) -> None:
        """
        Reset the current HTTP session.

        The next request will automatically create a new session and
        obtain fresh cookies from NSE.
        """

        self.session.close()
        self.session = requests.Session()
        self._initialized = False

    def _get_session(self, use_session: bool) -> requests.Session:
        """
        Return a configured HTTP session.
        """
        if use_session:
            self._ensure_session()
            return self.session

        session = requests.Session()
        session.headers.update(self._build_headers())

        return session

    def _get(self, url: str, *, use_session: bool = True, **kwargs) -> requests.Response:
        """
        Perform an HTTP GET request.
        """

        session = self._get_session(use_session)

        for attempt in range(2):
            try:
                response = session.get(url, timeout=self.timeout, **kwargs)

                # Only authenticated requests need session refresh.
                if (use_session and response.status_code in (401, 403)):
                    if attempt == 0:
                        self._reset_session()
                        session = self._get_session(True)
                        continue

                    raise NSEAuthenticationError(f"NSE rejected the request ({response.status_code}).")

                response.raise_for_status()

                return response

            except requests.exceptions.Timeout as exc:
                raise NSETimeoutError("The request to NSE timed out.") from exc

            except requests.exceptions.ConnectionError as exc:
                raise NSEConnectionError("Unable to connect to NSE.") from exc

            except requests.exceptions.HTTPError as exc:
                raise NSEResponseError(f"NSE returned HTTP {exc.response.status_code}.") from exc

            except requests.exceptions.RequestException as exc:
                raise NSEError("Unexpected error while communicating with NSE.") from exc

        # Defensive safeguard; execution should never reach here.
        raise NSEError("Unexpected failure while communicating with NSE.")

    # ======================================================================
    # Download Helpers
    # ======================================================================
    
    def _download_csv(self, url: str, **kwargs) -> pd.DataFrame:
        """
        Download a CSV file.

        Parameters
        ----------
        url
            URL of the CSV file.

        **kwargs
            Additional keyword arguments forwarded to ``_get()``.

        Returns
        -------
        DataFrame
            Raw CSV contents.
        """

        response = self._get(url, use_session=False, **kwargs)
        return pd.read_csv(BytesIO(response.content))

    def _download_json(self, url: str, **kwargs) -> dict | list:
        """
        Download a JSON resource.

        Parameters
        ----------
        url
            URL of the JSON endpoint.

        **kwargs
            Additional keyword arguments forwarded to ``_get()``.

        Returns
        -------
        dict | list
            Parsed JSON response.
        """

        response = self._get(url, use_session=False, **kwargs)
        return response.json()

    # =============================================================================
    # Symbol Processing
    # =============================================================================

    def _normalize_symbol_master(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the raw NSE symbol master into the canonical schema.

        Parameters
        ----------
        df
            Raw symbol master downloaded from NSE.

        Returns
        -------
        pd.DataFrame
            Symbol master using the project's canonical column names.
        """
        df = df.copy()

        # Normalize column names -------------------------------------------------
        df.columns = df.columns.str.strip()

        # Rename columns ---------------------------------------------------------
        df = df.rename(
            columns={
                "SYMBOL"            : SecurityFields.SYMBOL,
                "NAME OF COMPANY"   : SecurityFields.NAME,
                "SERIES"            : SecurityFields.SERIES,
                "DATE OF LISTING"   : SecurityFields.LISTING_DATE,
                "PAID UP VALUE"     : SecurityFields.PAID_UP_VALUE,
                "MARKET LOT"        : SecurityFields.MARKET_LOT,
                "ISIN NUMBER"       : SecurityFields.ISIN,
                "FACE VALUE"        : SecurityFields.FACE_VALUE,
            }
        )

        # Parse provider-specific data types -------------------------------------
        df[SecurityFields.LISTING_DATE]     = pd.to_datetime(df[SecurityFields.LISTING_DATE], errors="coerce", format="%d-%b-%Y").dt.date
        df[SecurityFields.EXCHANGE]         = Exchange.NSE
        df[SecurityFields.SECURITY_TYPE]    = SecurityType.STOCK
        df[SecurityFields.CURRENCY]         = Currency.INR
        df[SecurityFields.ACTIVE]           = True

        return df

    # ==========================================================================
    # Provider Capabilities
    # ==========================================================================

    _CAPABILITIES = ProviderCapabilities(
        synchronizable_fields=frozenset({
            SecurityFields.SYMBOL,
            SecurityFields.NAME,
            SecurityFields.EXCHANGE,
            SecurityFields.SECURITY_TYPE,
            SecurityFields.ISIN,
            SecurityFields.SERIES,
            SecurityFields.LISTING_DATE,
            SecurityFields.PAID_UP_VALUE,
            SecurityFields.MARKET_LOT,
            SecurityFields.FACE_VALUE,
        }),
        supports_symbols=True,
    )

    # =============================================================================
    # Public APIs
    # =============================================================================

    def fetch_symbols(self, *, series: SecuritySeries | str | Iterable[str] | None = SecuritySeries.EQ) -> pd.DataFrame:
        """
        Download the NSE symbol master.

        Parameters
        ----------
        series
            Security series to retain.

            Examples
            --------
            SecuritySeries.EQ
            "EQ"
            ["EQ", "BE"]
            None

        Returns
        -------
        pd.DataFrame
            Canonical security metadata.

            All returned columns use the project's canonical
            ``SecurityFields`` names.
        """

        # Download ----------------------------------------------------------------
        df = self._download_csv(NSE_EQUITY_MASTER_URL)

        # Provider normalization --------------------------------------------------
        df = self._normalize_symbol_master(df)

        # General Processing ------------------------------------------------------
        df = normalize_symbol_values(df)
        df = filter_symbol_series(df, series)

        return df


