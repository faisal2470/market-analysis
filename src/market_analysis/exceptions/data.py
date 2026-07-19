"""
Custom exceptions related to market data.
"""

from __future__ import annotations


class MarketDataError(Exception):
    """
    Base class for all market data exceptions.
    """


class UnsupportedExchangeError(MarketDataError):
    """
    Raised when a data source does not support the requested exchange.
    """


class InvalidTickerError(MarketDataError):
    """
    Raised when an invalid ticker symbol is supplied.
    """


class DataDownloadError(MarketDataError):
    """
    Raised when historical or live market data cannot be downloaded.
    """


class EmptyDataError(MarketDataError):
    """
    Raised when a data source returns no data.
    """