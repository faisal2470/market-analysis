
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Set

import pandas as pd

from market_analysis.database.models.enums import DataProvider, SecurityFields
from market_analysis.database.models import Security
from market_analysis.database import SessionLocal, SecurityUpsertSummary, upsert_securities
from market_analysis.data.providers import ProviderCapabilities, NSEClient

# ===========================================================================
# Dataclasses
# ===========================================================================

@dataclass(slots=True)
class SymbolDataset:
    """
    Canonical security metadata downloaded from a data provider.
    """
    provider:       DataProvider
    capabilities:   ProviderCapabilities
    data:           pd.DataFrame

# ===========================================================================
# Private Helpers
# ===========================================================================

def _create_provider(provider: DataProvider):
    """
    Create a data provider client.

    Parameters
    ----------
    provider
        Data provider to instantiate.

    Returns
    -------
    object
        Initialised provider client.

    Raises
    ------
    ValueError
        If the provider is not supported.
    """

    match provider:
        case DataProvider.NSE:
            return NSEClient()
        case _:
            raise ValueError(f"Unsupported data provider: {provider}")

def _compute_allowed_fields(dataset: SymbolDataset) -> frozenset[SecurityFields]:
    """
    Compute the set of security fields that may be synchronized.

    Parameters
    ----------
    dataset
        Downloaded symbol dataset.

    Returns
    -------
    Set[SecurityFields]
        Fields that are supported by both the provider and the
        Security model.
    """

    return (
        dataset.capabilities.synchronizable_fields
        &
        Security.synchronizable_fields
    )

# ===========================================================================
# Public APIs
# ===========================================================================

def fetch_symbols(provider: DataProvider) -> SymbolDataset:
    """
    Download and normalize security metadata from a data provider.

    Parameters
    ----------
    provider
        Data provider to fetch symbols from.

    Returns
    -------
    SymbolDataset
        Canonical security metadata together with provider metadata.
    """

    client = _create_provider(provider)

    return SymbolDataset(provider=provider, capabilities=client.capabilities, data=client.fetch_symbols(series=None))

def refresh_symbols(provider: DataProvider) -> SecurityUpsertSummary:
    """
    Synchronize security metadata into the database.

    Parameters
    ----------
    provider
        Data provider used to synchronize security metadata.

    Returns
    -------
    SecurityUpsertSummary
        Summary of the synchronization.
    """

    dataset = fetch_symbols(provider)

    allowed_fields = _compute_allowed_fields(dataset)

    with SessionLocal() as session:

        summary = upsert_securities(
            session=session,
            securities=dataset.data,
            allowed_fields=allowed_fields,
        )

    return summary

