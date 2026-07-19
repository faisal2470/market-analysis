"""
Custom project exceptions.
"""

from .data import DataDownloadError
from .data import MarketDataError
from .data import EmptyDataError
from .data import InvalidTickerError
from .data import UnsupportedExchangeError

__all__ = [
    "DataError",
    "UnsupportedExchangeError",
    "InvalidTickerError",
    "DataDownloadError",
    "EmptyDataError",
]