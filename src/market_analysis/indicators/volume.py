"""Placeholders for volume indicators."""

from typing import Any


def calculate_obv(data: Any) -> Any:
    """Calculate on-balance volume.

    Args:
        data: Price and volume data to process.

    Returns:
        A future OBV series.
    """
    pass


def calculate_money_flow_index(data: Any, period: int) -> Any:
    """Calculate money flow index.

    Args:
        data: OHLCV data to process.
        period: The rolling-window length.

    Returns:
        A future MFI series.
    """
    pass
