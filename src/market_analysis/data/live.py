"""Placeholders for live market-data access."""

from typing import Any


def get_live_quote(symbol: str) -> dict[str, Any]:
    """Retrieve a live quote for a symbol.

    Args:
        symbol: The market symbol to retrieve.

    Returns:
        A future live quote record.
    """
    pass


def get_market_snapshot() -> dict[str, Any]:
    """Retrieve a snapshot of the current market.

    Returns:
        A future market snapshot record.
    """
    pass
