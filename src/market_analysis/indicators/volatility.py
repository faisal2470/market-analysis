"""Placeholders for volatility indicators."""

from typing import Any


def calculate_atr(data: Any, period: int) -> Any:
    """Calculate average true range.

    Args:
        data: OHLC data to process.
        period: The rolling-window length.

    Returns:
        A future ATR series.
    """
    pass


def calculate_bollinger_bands(
    data: Any,
    period: int,
    standard_deviations: float,
) -> Any:
    """Calculate Bollinger Bands.

    Args:
        data: Price data to process.
        period: The rolling-window length.
        standard_deviations: The band-width multiplier.

    Returns:
        A future bands result.
    """
    pass


def calculate_donchian_channels(data: Any, period: int) -> Any:
    """Calculate Donchian Channels.

    Args:
        data: OHLC data to process.
        period: The lookback length.

    Returns:
        A future channels result.
    """
    pass
