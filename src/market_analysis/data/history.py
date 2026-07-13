"""Placeholders for historical OHLCV data management."""

from datetime import date
from typing import Any


def download_historical_data(symbol: str, start: date, end: date) -> Any:
    """Download historical OHLCV data for a symbol.

    Args:
        symbol: The market symbol to retrieve.
        start: The first requested trading date.
        end: The last requested trading date.

    Returns:
        A future historical-data object.
    """
    pass


def load_historical_data(symbol: str) -> Any:
    """Load cached historical data for a symbol.

    Args:
        symbol: The market symbol to load.

    Returns:
        A future historical-data object.
    """
    pass


def update_historical_data(symbol: str) -> None:
    """Update cached historical data for a symbol.

    Args:
        symbol: The market symbol to update.
    """
    pass
