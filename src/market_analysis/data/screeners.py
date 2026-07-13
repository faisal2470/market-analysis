"""Placeholders for market-screening operations."""

from typing import Any


def get_top_gainers() -> list[dict[str, Any]]:
    """Return the leading market gainers.

    Returns:
        A future collection of gainer records.
    """
    pass


def get_top_losers() -> list[dict[str, Any]]:
    """Return the leading market losers.

    Returns:
        A future collection of loser records.
    """
    pass


def get_trending_symbols() -> list[str]:
    """Return currently trending symbols.

    Returns:
        A future list of ticker symbols.
    """
    pass


def get_most_active_symbols() -> list[str]:
    """Return the most actively traded symbols.

    Returns:
        A future list of ticker symbols.
    """
    pass


def get_new_highs() -> list[str]:
    """Return symbols reaching new highs.

    Returns:
        A future list of ticker symbols.
    """
    pass


def get_new_lows() -> list[str]:
    """Return symbols reaching new lows.

    Returns:
        A future list of ticker symbols.
    """
    pass
