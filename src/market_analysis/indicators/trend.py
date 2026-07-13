"""Placeholders for trend and trend-strength indicators."""

from typing import Any


def calculate_sma(data: Any, period: int) -> Any:
    """Calculate a simple moving average.

    Args:
        data: Price data to process.
        period: The rolling-window length.

    Returns:
        A future SMA series.
    """
    pass


def calculate_ema(data: Any, period: int) -> Any:
    """Calculate an exponential moving average.

    Args:
        data: Price data to process.
        period: The rolling-window length.

    Returns:
        A future EMA series.
    """
    pass


def calculate_vwap(data: Any) -> Any:
    """Calculate volume-weighted average price.

    Args:
        data: OHLCV data to process.

    Returns:
        A future VWAP series.
    """
    pass


def calculate_adx(data: Any, period: int) -> Any:
    """Calculate average directional index.

    Args:
        data: OHLC data to process.
        period: The rolling-window length.

    Returns:
        A future ADX series.
    """
    pass


def calculate_supertrend(data: Any, period: int, multiplier: float) -> Any:
    """Calculate the Supertrend indicator.

    Args:
        data: OHLC data to process.
        period: The ATR window length.
        multiplier: The ATR multiplier.

    Returns:
        A future Supertrend series.
    """
    pass
