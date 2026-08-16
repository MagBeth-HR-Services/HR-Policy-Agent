import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


def resolve_database_path() -> Path:
    """Return the configured SQLite database path."""
    load_dotenv(PROJECT_ROOT / ".env")

    configured_path = Path(
        os.getenv("HR_DATABASE_PATH", "./data/hr_data.db")
    )

    if configured_path.is_absolute():
        return configured_path

    return (PROJECT_ROOT / configured_path).resolve()


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database."""
    database_path = resolve_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database() -> Path:
    """Create the database and its tables."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.executescript(schema)

    return resolve_database_path()