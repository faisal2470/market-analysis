"""
Market data cleaning utilities.

This module provides deterministic cleaning operations for downloaded
market data. Unlike validation, cleaning modifies the DataFrame to make
it suitable for storage or analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

# ============================================================================
# Models
# ============================================================================

@dataclass(slots=True)
class CleaningAction:
    """
    Represents a single cleaning action.
    """

    action:     str
    message:    str

@dataclass(slots=True)
class CleaningReport:
    """
    Summary of all cleaning operations performed.
    """

    actions: list[CleaningAction] = field(default_factory=list)

    def add_action(self, action: str, message: str) -> None:

        self.actions.append(CleaningAction(
                action=action,
                message=message,
        ))

    def summary(self) -> str:
        """
        Return a formatted cleaning summary.
        """

        lines = [
            "Cleaning Report",
            "=" * 15,
            "",
        ]

        if not self.actions:
            lines.append("No cleaning was required.")
            return "\n".join(lines)

        for action in self.actions:
            lines.append(f"• {action.action}")
            lines.append(f"  {action.message}")

        return "\n".join(lines)

    def print_summary(self) -> None:
        """Print the cleaning summary."""

        print(self.summary())

# ============================================================================
# Cleaning operations
# ============================================================================

def _sort_index(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:

    if df.index.is_monotonic_increasing:
        return df

    report.add_action(
        "sort_index",
        "Sorted DataFrame by index.",
    )

    return df.sort_index()

def _remove_duplicate_index(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:

    duplicated = df.index.duplicated()

    if not duplicated.any():
        return df

    n = duplicated.sum()

    report.add_action(
        "duplicate_index",
        f"Removed {n} duplicated timestamps.",
    )

    return df.loc[~duplicated]

def _remove_duplicate_rows(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:

    duplicated = df.duplicated()

    if not duplicated.any():
        return df

    n = duplicated.sum()

    report.add_action(
        "duplicate_rows",
        f"Removed {n} duplicated rows.",
    )

    return df.loc[~duplicated]

def _drop_missing_values(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:

    n = len(df)

    df = df.dropna()

    removed = n - len(df)

    if removed:

        report.add_action(
            "missing_values",
            f"Removed {removed} rows containing NaN values.",
        )

    return df

def _remove_zero_volume(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:

    if "Volume" not in df.columns:
        return df

    invalid = df["Volume"] == 0

    if not invalid.any():
        return df

    report.add_action(
        "zero_volume",
        f"Removed {invalid.sum()} zero-volume rows.",
    )

    return df.loc[~invalid]

def _convert_dtypes(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
    """
    Convert columns to expected dtypes.
    """

    float_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    if "Adj Close" in df.columns:
        float_columns.append("Adj Close")

    for column in float_columns:
        if column in df.columns:
            df[column] = df[column].astype(float)

    report.add_action(
        "dtypes",
        "Converted numeric columns to float.",
    )

    return df

# ============================================================================
# Public API
# ============================================================================

def clean_daily_data(
    df: pd.DataFrame,
    *,
    sort_index: bool = True,
    remove_duplicate_index: bool = True,
    remove_duplicate_rows: bool = True,
    drop_missing_values: bool = False,
    remove_zero_volume: bool = False,
    convert_dtypes: bool = True,
) -> tuple[pd.DataFrame, CleaningReport]:
    """
    Clean a daily OHLCV DataFrame.

    Parameters
    ----------
    df
        Input DataFrame.

    Returns
    -------
    tuple[pd.DataFrame, CleaningReport]
        Cleaned DataFrame and cleaning report.
    """

    df = df.copy()

    report = CleaningReport()

    if sort_index:
        df = _sort_index(df, report)

    if remove_duplicate_index:
        df = _remove_duplicate_index(df, report)

    if remove_duplicate_rows:
        df = _remove_duplicate_rows(df, report)

    if drop_missing_values:
        df = _drop_missing_values(df, report)

    if remove_zero_volume:
        df = _remove_zero_volume(df, report)

    if convert_dtypes:
        df = _convert_dtypes(df, report)

    return df, report


