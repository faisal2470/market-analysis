"""Placeholders for database CRUD operations."""

from typing import Any


def create_record(record: Any) -> Any:
    """Create a database record.

    Args:
        record: The record to persist.

    Returns:
        A future persisted record.
    """
    pass


def read_record(record_id: int) -> Any:
    """Read a database record by identifier.

    Args:
        record_id: The record identifier.

    Returns:
        A future record, if found.
    """
    pass


def update_record(record_id: int, values: dict[str, Any]) -> Any:
    """Update a database record.

    Args:
        record_id: The record identifier.
        values: Values to update.

    Returns:
        A future updated record.
    """
    pass


def delete_record(record_id: int) -> None:
    """Delete a database record.

    Args:
        record_id: The record identifier.
    """
    pass
