"""
Utilities for processing security master datasets.

These functions operate on the canonical symbol schema used throughout
the project. They are provider-independent and should work for any
symbol master returned by a data provider.
"""

from __future__ import annotations

from collections.abc import Iterable
import pandas as pd

from market_analysis.database.models.enums import SecuritySeries, SecurityFields

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
    df[SecurityFields.SYMBOL]       = df[SecurityFields.SYMBOL      ].str.strip().str.upper()
    df[SecurityFields.NAME]         = df[SecurityFields.NAME        ].str.strip()
    df[SecurityFields.SERIES]       = df[SecurityFields.SERIES      ].str.strip().str.upper()
    df[SecurityFields.ISIN]         = df[SecurityFields.ISIN        ].str.strip().str.upper()

    # Finalize ---------------------------------------------------------------
    return df.sort_values(SecurityFields.SYMBOL).reset_index(drop=True)

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

    return df[df[SecurityFields.SERIES].isin(allowed)].reset_index(drop=True)


