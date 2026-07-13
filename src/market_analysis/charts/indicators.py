"""Placeholders for indicator and volume chart overlays."""

from typing import Any


def plot_indicator_overlay(chart: Any, indicator: Any, label: str) -> Any:
    """Add an indicator overlay to a chart.

    Args:
        chart: The chart to extend.
        indicator: Indicator data to overlay.
        label: The indicator label.

    Returns:
        A future updated chart object.
    """
    pass


def plot_volume_chart(data: Any, title: str) -> Any:
    """Create a volume chart.

    Args:
        data: Volume data to plot.
        title: The chart title.

    Returns:
        A future chart object.
    """
    pass
