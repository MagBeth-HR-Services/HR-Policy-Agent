import json
from pathlib import Path

from database.connection import (
    get_connection,
    initialize_database,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MOCK_DATA_PATH = PROJECT_ROOT / "mock_data"


def load_json(filename: str) -> list[dict]:
    """Load records from one mock JSON file."""
    path = MOCK_DATA_PATH / filename

    with path.open(encoding="utf-8") as file:
        return json.load(file)


def insert_records(
    connection,
    table_name: str,
    records: list[dict],
) -> None:
    """Insert records without replacing existing rows."""
    if not records:
        return

    columns = list(records[0].keys())
    column_names = ", ".join(columns)
    placeholders = ", ".join("?" for _ in columns)

    sql = (
        f"INSERT OR IGNORE INTO {table_name} "
        f"({column_names}) VALUES ({placeholders})"
    )

    values = [
        tuple(record[column] for column in columns)
        for record in records
    ]

    connection.executemany(sql, values)


def seed_database() -> dict[str, int]:
    """Create the database and seed it with mock HR data."""
    initialize_database()

    employees = load_json("employees.json")
    pto_balances = load_json("pto_balances.json")
    benefits = load_json("benefits.json")
    hr_tickets = load_json("hr_tickets.json")

    with get_connection() as connection:
        # Insert employees first without managers because some managers
        # appear later in the JSON file.
        employees_without_managers = [
            {**employee, "manager_id": None}
            for employee in employees
        ]

        insert_records(
            connection,
            "employees",
            employees_without_managers,
        )

        connection.executemany(
            """
            UPDATE employees
            SET manager_id = ?
            WHERE employee_id = ?
            """,
            [
                (
                    employee["manager_id"],
                    employee["employee_id"],
                )
                for employee in employees
            ],
        )

        insert_records(
            connection,
            "pto_balances",
            pto_balances,
        )
        insert_records(
            connection,
            "benefits",
            benefits,
        )
        insert_records(
            connection,
            "hr_tickets",
            hr_tickets,
        )

        counts = {}

        for table_name in (
            "employees",
            "pto_balances",
            "benefits",
            "hr_tickets",
        ):
            result = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()

            counts[table_name] = result[0]

    return counts


def main() -> None:
    counts = seed_database()

    print("Database seeded successfully.")

    for table_name, count in counts.items():
        print(f"{table_name}: {count}")


if __name__ == "__main__":
    main()