"""Placeholders for user watchlist management."""

WATCHLIST = ["RELIANCE", "TCS", "INFY"]


def get_watchlist() -> list[str]:
    """Return the configured watchlist.

    Returns:
        A future copy of the user's watchlist.
    """
    pass


def add_to_watchlist(symbol: str) -> None:
    """Add a symbol to the watchlist.

    Args:
        symbol: The ticker symbol to add.
    """
    pass


def remove_from_watchlist(symbol: str) -> None:
    """Remove a symbol from the watchlist.

    Args:
        symbol: The ticker symbol to remove.
    """
    pass
