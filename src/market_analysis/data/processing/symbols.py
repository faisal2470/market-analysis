"""
Utilities for processing security master datasets.

These functions operate on the canonical symbol schema used throughout
the project. They are provider-independent and should work for any
symbol master returned by a data provider.
"""

from __future__ import annotations

from collections.abc import Iterable
import pandas as pd

from market_analysis.database.models.enums import SecuritySeries, SymbolColumns

# =============================================================================
# Value Normalization
# =============================================================================

def normalize_symbol_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize values in a canonical symbol master.

    Parameters
    ----------
    df
        Symbol master using the canonical column names.

    Returns
    -------
    pd.DataFrame
        Normalized copy of the symbol master.
    """

    df = df.copy()

    # Normalize string columns ------------------------------------------------
    df[SymbolColumns.SYMBOL]        = df[SymbolColumns.SYMBOL       ].str.strip().str.upper()
    df[SymbolColumns.COMPANY_NAME]  = df[SymbolColumns.COMPANY_NAME ].str.strip()
    df[SymbolColumns.SERIES]        = df[SymbolColumns.SERIES       ].str.strip().str.upper()
    df[SymbolColumns.ISIN]          = df[SymbolColumns.ISIN         ].str.strip().str.upper()

    # Finalize ---------------------------------------------------------------
    return df.sort_values(SymbolColumns.SYMBOL).reset_index(drop=True)

# =============================================================================
# Series Filtering
# =============================================================================

def filter_symbol_series(df: pd.DataFrame, series: SecuritySeries | str | Iterable[str] | None) -> pd.DataFrame:
    """
    Filter the symbol master by security series.

    Parameters
    ----------
    df
        Canonical symbol master.

    series
        Security series to retain.

        - ``SecuritySeries.EQ``
        - ``"EQ"``
        - ``["EQ", "BE"]``
        - ``None`` (returns all rows)

    Returns
    -------
    pd.DataFrame
        Filtered symbol master.
    """

    if series is None:
        return df.copy()

    if isinstance(series, (SecuritySeries, str)):
        series = [series]

    allowed = {str(value).strip().upper() for value in series}

    return df[df[SymbolColumns.SERIES].isin(allowed)].reset_index(drop=True)


