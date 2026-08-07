"""
Immutable description of the data supported by a market data provider.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from market_analysis.database.models.enums import SecurityFields

@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    """
    Immutable description of the information a provider can supply.

    The synchronization layer uses this metadata to determine which
    fields may be updated in the database.
    """
    synchronizable_fields:      frozenset[SecurityFields] = field(default_factory=frozenset)

    supports_symbols:           bool = False
    supports_daily_history:     bool = False
    supports_intraday_history:  bool = False

    def supports(self, field: SecurityFields) -> bool:
        """
        Return whether the provider supplies the given field.
        """

        return field in self.supported_fields

    