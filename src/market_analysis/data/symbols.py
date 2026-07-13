"""Placeholders for market-symbol and exchange conversions."""


def lookup_symbol(query: str) -> list[str]:
    """Find symbols matching a query.

    Args:
        query: Text used to search symbols.

    Returns:
        A future list of matching symbols.
    """
    pass


def is_valid_ticker(ticker: str) -> bool:
    """Validate a ticker symbol.

    Args:
        ticker: The ticker to validate.

    Returns:
        Whether the ticker is valid.
    """
    pass


def convert_ticker(ticker: str, target_format: str) -> str:
    """Convert a ticker to a target format.

    Args:
        ticker: The source ticker.
        target_format: The requested ticker format.

    Returns:
        A future converted ticker.
    """
    pass


def convert_exchange(exchange: str, target_format: str) -> str:
    """Convert an exchange identifier to a target format.

    Args:
        exchange: The source exchange identifier.
        target_format: The requested exchange format.

    Returns:
        A future converted exchange identifier.
    """
    pass
