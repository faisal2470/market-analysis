"""Placeholders for momentum indicators."""

from typing import Any


def calculate_rsi(data: Any, period: int) -> Any:
    """Calculate relative strength index.

    Args:
        data: Price data to process.
        period: The rolling-window length.

    Returns:
        A future RSI series.
    """
    pass


def calculate_macd(
    data: Any,
    fast_period: int,
    slow_period: int,
    signal_period: int,
) -> Any:
    """Calculate moving average convergence divergence.

    Args:
        data: Price data to process.
        fast_period: The fast EMA length.
        slow_period: The slow EMA length.
        signal_period: The signal EMA length.

    Returns:
        A future MACD result.
    """
    pass


def calculate_roc(data: Any, period: int) -> Any:
    """Calculate rate of change.

    Args:
        data: Price data to process.
        period: The lookback length.

    Returns:
        A future ROC series.
    """
    pass
