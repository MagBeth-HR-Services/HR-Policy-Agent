from database.connection import (
    get_connection,
    initialize_database,
)
from database.seed import seed_database


def test_initialize_database_creates_tables(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "test_hr_data.db"

    monkeypatch.setenv(
        "HR_DATABASE_PATH",
        str(database_path),
    )

    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

    table_names = {row["name"] for row in rows}

    assert {
        "employees",
        "pto_balances",
        "benefits",
        "hr_tickets",
    }.issubset(table_names)


def test_seed_database_loads_mock_data(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "test_hr_data.db"

    monkeypatch.setenv(
        "HR_DATABASE_PATH",
        str(database_path),
    )

    counts = seed_database()

    assert counts == {
        "employees": 12,
        "pto_balances": 12,
        "benefits": 12,
        "hr_tickets": 3,
    }