from datetime import datetime, timezone

from database.connection import get_connection


def get_employee_summary(employee_id: str) -> dict:
    """Return a limited, non-sensitive employee summary."""
    employee_id = employee_id.strip().upper()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                employee_id,
                first_name,
                employment_type,
                department,
                job_title,
                work_mode,
                primary_city,
                primary_state,
                primary_country,
                status
            FROM employees
            WHERE employee_id = ?
            """,
            (employee_id,),
        ).fetchone()

    if row is None:
        raise ValueError(
            f"Employee {employee_id} was not found."
        )

    return dict(row)


def get_pto_balance(employee_id: str) -> dict:
    """Return an employee's PTO balance."""
    employee_id = employee_id.strip().upper()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                employee_id,
                available_hours,
                approved_future_hours,
                annual_accrual_hours,
                carryover_hours,
                last_updated,
                notes
            FROM pto_balances
            WHERE employee_id = ?
            """,
            (employee_id,),
        ).fetchone()

    if row is None:
        raise ValueError(
            f"No PTO balance was found for {employee_id}."
        )

    return dict(row)


def get_benefits_status(employee_id: str) -> dict:
    """Return an employee's benefits status."""
    employee_id = employee_id.strip().upper()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                employee_id,
                benefits_eligible,
                medical_status,
                dental_status,
                vision_status,
                enrollment_effective_date,
                last_updated
            FROM benefits
            WHERE employee_id = ?
            """,
            (employee_id,),
        ).fetchone()

    if row is None:
        raise ValueError(
            f"No benefits record was found for {employee_id}."
        )

    result = dict(row)
    result["benefits_eligible"] = bool(
        result["benefits_eligible"]
    )

    return result


def create_hr_ticket(
    employee_id: str,
    category: str,
    summary: str,
    confirmed_by_user: bool,
) -> dict:
    """Create an HR ticket only after explicit user confirmation."""
    employee_id = employee_id.strip().upper()
    category = category.strip().lower()
    summary = summary.strip()

    allowed_categories = {
        "pto",
        "remote_work",
        "benefits",
        "conduct",
        "other",
    }

    if not confirmed_by_user:
        raise PermissionError(
            "The user must explicitly confirm ticket creation."
        )

    if category not in allowed_categories:
        raise ValueError(
            f"Unsupported ticket category: {category}."
        )

    if not summary:
        raise ValueError(
            "The ticket summary cannot be empty."
        )

    if len(summary) > 500:
        raise ValueError(
            "The ticket summary cannot exceed 500 characters."
        )

    get_employee_summary(employee_id)

    with get_connection() as connection:
        latest_ticket = connection.execute(
            """
            SELECT ticket_id
            FROM hr_tickets
            ORDER BY ticket_id DESC
            LIMIT 1
            """
        ).fetchone()

        if latest_ticket is None:
            next_number = 1
        else:
            next_number = (
                int(latest_ticket["ticket_id"].split("-")[1])
                + 1
            )

        ticket_id = f"TKT-{next_number:04d}"
        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        connection.execute(
            """
            INSERT INTO hr_tickets (
                ticket_id,
                employee_id,
                category,
                summary,
                status,
                created_at,
                confirmed_by_user
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                employee_id,
                category,
                summary,
                "open",
                created_at,
                1,
            ),
        )

    return {
        "ticket_id": ticket_id,
        "employee_id": employee_id,
        "category": category,
        "summary": summary,
        "status": "open",
        "created_at": created_at,
        "confirmed_by_user": True,
    }