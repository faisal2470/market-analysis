"""
Market data validation utilities.

This module validates downloaded market data before it is stored in the
database. Validation reports data quality issues but never modifies the
input DataFrame.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

import pandas as pd

# ============================================================================
# Models
# ============================================================================


class ValidationSeverity(StrEnum):
    """Severity level of a validation issue."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

@dataclass(slots=True)
class ValidationIssue:

    severity:   ValidationSeverity
    check:      str
    message:    str
    rows:       list[pd.Timestamp] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"[{self.severity}] "
            f"{self.check}: {self.message}"
        )

@dataclass(slots=True)
class ValidationReport:

    issues:     list[ValidationIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)
    
    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]
    
    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR]
    
    def add_issue(self, severity: ValidationSeverity, check: str, message: str, rows: list[pd.Timestamp] | None = None):

        self.issues.append(ValidationIssue(
            severity=severity,
            check=check, 
            message=message,
            rows= rows or [],
        ))

    def summary(self) -> str:
        """
        Return a formatted validation summary.
        """

        lines = [
            "Validation Report",
            "=" * 17,
            "",
            f"Status : {'PASSED' if self.passed else 'FAILED'}",
            f"Issues : {len(self.issues)}",
            "",
        ]

        if self.warnings:
            lines.extend([
                "Warnings",
                "-" * 8,
            ])

            for issue in self.warnings:
                lines.append(f"• {issue.check}")
                lines.append(f"  {issue.message}")

            lines.append("")

        if self.errors:
            lines.extend([
                "Errors",
                "-" * 6,
            ])

            for issue in self.errors:
                lines.append(f"• {issue.check}")
                lines.append(f"  {issue.message}")

        if not self.issues:
            lines.append("No issues detected.")

        return "\n".join(lines)

    def print_summary(self) -> None:
        """
        Print the validation summary.
        """

        print(self.summary())

    def __bool__(self) -> bool:
        return self.passed

# ============================================================================
# Constants
# ============================================================================


REQUIRED_COLUMNS = (
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
)

# ============================================================================
# Individual validation checks
# ============================================================================

def _check_required_columns(df: pd.DataFrame, report: ValidationReport) -> None:

    missing = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing:
        report.add_issue(
            ValidationSeverity.ERROR,
            "required_columns",
            f"Missing columns: {sorted(missing)}",
        )

def _check_duplicate_columns(df: pd.DataFrame, report: ValidationReport) -> None:

    if df.columns.has_duplicates:

        report.add_issue(
            ValidationSeverity.ERROR,
            "duplicate_columns",
            "Duplicate columns detected.",
        )

def _check_duplicate_index(df: pd.DataFrame, report: ValidationReport) -> None:

    if df.index.has_duplicates:

        report.add_issue(
            ValidationSeverity.ERROR,
            "duplicate_index",
            "Duplicate timestamps detected.",
            rows=df.index[df.index.duplicated()].tolist(),
        )

def _check_sorted_index(df: pd.DataFrame, report: ValidationReport) -> None:

    if not df.index.is_monotonic_increasing:

        report.add_issue(
            ValidationSeverity.WARNING,
            "sorted_index",
            "Index is not sorted."
        )

def _check_missing_values(df: pd.DataFrame, report: ValidationReport) -> None:

    if not df.isna().any().any():
        return

    report.add_issue(
        ValidationSeverity.ERROR,
        "missing_values",
        "Missing values detected.",
        rows=df[df.isna().any(axis=1)].index.tolist(),
    )

def _check_negative_prices(df: pd.DataFrame, report: ValidationReport) -> None:

    for column in ("Open", "High", "Low", "Close"):

        invalid = df[df[column] <= 0]

        if invalid.empty:
            continue

        report.add_issue(
            ValidationSeverity.ERROR,
            "negative_prices",
            f"{column} contains non-positive values.",
            rows=invalid.index.tolist(),
        )

def _check_negative_volume(df: pd.DataFrame, report: ValidationReport) -> None:

    invalid = df[df["Volume"] < 0]

    if invalid.empty:
        return

    report.add_issue(
        ValidationSeverity.ERROR,
        "negative_volume",
        "Negative volume detected.",
        rows=invalid.index.tolist(),
    )

def _check_zero_volume(df: pd.DataFrame, report: ValidationReport) -> None:

    invalid = df[df["Volume"] == 0]

    if invalid.empty:
        return

    report.add_issue(
        ValidationSeverity.WARNING,
        "zero_volume",
        f"{len(invalid)} zero-volume rows detected.",
        rows=invalid.index.tolist(),
    )

def _check_ohlc_consistency(df: pd.DataFrame, report: ValidationReport) -> None:

    invalid = df[
        (df["High"] < df["Open"])
        | (df["High"] < df["Close"])
        | (df["High"] < df["Low"])
        | (df["Low"] > df["Open"])
        | (df["Low"] > df["Close"])
    ]

    if invalid.empty:
        return

    report.add_issue(
        ValidationSeverity.ERROR,
        "ohlc_consistency",
        "Invalid OHLC relationships detected.",
        rows=invalid.index.tolist(),
    )


VALIDATORS = (
    _check_required_columns,
    _check_duplicate_index,
    _check_duplicate_columns,
    _check_sorted_index,
    _check_missing_values,
    _check_negative_prices,
    _check_negative_volume,
    _check_zero_volume,
    _check_ohlc_consistency
)

# ============================================================================
# Public API
# ============================================================================


def validate_daily_data(df: pd.DataFrame) -> ValidationReport:
    """
    Validate a daily OHLCV DataFrame.
    """

    report = ValidationReport()

    for validator in VALIDATORS:
        validator(df, report)

    return report


