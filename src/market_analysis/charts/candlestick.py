"""Placeholders for price-chart rendering."""

from typing import Any


def plot_candlestick_chart(data: Any, title: str) -> Any:
    """Create a candlestick chart.

    Args:
        data: OHLC data to plot.
        title: The chart title.

    Returns:
        A future chart object.
    """
    pass


def plot_ohlc_chart(data: Any, title: str) -> Any:
    """Create an OHLC chart.

    Args:
        data: OHLC data to plot.
        title: The chart title.

    Returns:
        A future chart object.
    """
    pass
