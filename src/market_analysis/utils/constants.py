"""
Project-wide constants.

This module contains configuration constants shared across the
market_analysis package.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATABASE_DIR = PROJECT_ROOT / "storage"

DATABASE_FILE = DATABASE_DIR / "market.db"

# SQLite database URL understood by SQLAlchemy
DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"