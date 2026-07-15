"""
Enumerations used throughout the market_analysis package.

This module defines strongly-typed enumerations shared across the
database models, data providers, analysis modules, and visualization
utilities.
"""

from __future__ import annotations

from enum import StrEnum


class Exchange(StrEnum):
    """
    Supported stock exchanges.
    """

    NSE = "NSE"
    BSE = "BSE"


class SecurityType(StrEnum):
    """
    Supported security types.
    """

    STOCK = "STOCK"
    ETF = "ETF"
    INDEX = "INDEX"
    MUTUAL_FUND = "MUTUAL_FUND"
    BOND = "BOND"


class TimeInterval(StrEnum):
    """
    Supported historical and intraday time intervals.
    """

    ONE_MINUTE = "1m"
    TWO_MINUTE = "2m"
    FIVE_MINUTE = "5m"
    FIFTEEN_MINUTE = "15m"
    THIRTY_MINUTE = "30m"

    ONE_HOUR = "1h"
    TWO_HOUR = "2h"
    FOUR_HOUR = "4h"

    ONE_DAY = "1d"
    FIVE_DAY = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTH = "3mo"


class Currency(StrEnum):
    """
    Supported trading currencies.
    """

    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"


class PriceField(StrEnum):
    """
    Standard price field names used throughout the project.
    """

    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    ADJ_CLOSE = "adj_close"
    VOLUME = "volume"