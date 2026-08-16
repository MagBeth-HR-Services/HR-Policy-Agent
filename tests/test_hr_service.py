import pytest

from database.connection import get_connection
from database.hr_service import (
    create_hr_ticket,
    get_benefits_status,
    get_employee_summary,
    get_pto_balance,
)
from database.seed import seed_database


@pytest.fixture
def seeded_database(tmp_path, monkeypatch):
    database_path = tmp_path / "test_hr_data.db"

    monkeypatch.setenv(
        "HR_DATABASE_PATH",
        str(database_path),
    )

    seed_database()

    return database_path


def test_reads_employee_hr_data(seeded_database):
    employee = get_employee_summary("e1002")
    pto = get_pto_balance("E1002")
    benefits = get_benefits_status("E1002")

    assert employee["employee_id"] == "E1002"
    assert employee["work_mode"] == "remote"
    assert pto["available_hours"] == 120.0
    assert benefits["benefits_eligible"] is True


def test_unknown_employee_raises_error(seeded_database):
    with pytest.raises(
        ValueError,
        match="Employee E9999 was not found",
    ):
        get_employee_summary("E9999")


def test_ticket_requires_confirmation(seeded_database):
    with get_connection() as connection:
        before_count = connection.execute(
            "SELECT COUNT(*) FROM hr_tickets"
        ).fetchone()[0]

    with pytest.raises(
        PermissionError,
        match="explicitly confirm",
    ):
        create_hr_ticket(
            employee_id="E1002",
            category="remote_work",
            summary="Request HR review.",
            confirmed_by_user=False,
        )

    with get_connection() as connection:
        after_count = connection.execute(
            "SELECT COUNT(*) FROM hr_tickets"
        ).fetchone()[0]

    assert after_count == before_count


def test_confirmed_ticket_is_created(seeded_database):
    ticket = create_hr_ticket(
        employee_id="E1002",
        category="remote_work",
        summary="Request HR review.",
        confirmed_by_user=True,
    )

    assert ticket["ticket_id"] == "TKT-0004"
    assert ticket["status"] == "open"
    assert ticket["confirmed_by_user"] is True

    with get_connection() as connection:
        saved_ticket = connection.execute(
            """
            SELECT *
            FROM hr_tickets
            WHERE ticket_id = ?
            """,
            (ticket["ticket_id"],),
        ).fetchone()

    assert saved_ticket is not None
    assert saved_ticket["employee_id"] == "E1002"