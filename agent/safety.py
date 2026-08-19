import re


EMPLOYEE_ID_PATTERN = re.compile(r"^E\d{4}$")

EXPLICIT_CONFIRMATIONS = {
    "yes",
    "yes, create it",
    "yes, create the ticket",
    "confirm",
    "confirmed",
    "i confirm",
    "proceed",
}


def validate_employee_id(employee_id: str) -> str:
    """Validate and normalize a Horizon employee ID."""
    normalized_id = employee_id.strip().upper()

    if not EMPLOYEE_ID_PATTERN.fullmatch(normalized_id):
        raise ValueError(
            "Employee ID must use the format E followed by "
            "four digits, such as E1002."
        )

    return normalized_id


def is_explicit_confirmation(message: str) -> bool:
    """Return true only for a clear confirmation response."""
    normalized_message = " ".join(
        message.strip().lower().split()
    )

    return normalized_message in EXPLICIT_CONFIRMATIONS


def safe_error_message(error: Exception) -> str:
    """Convert an expected application error into a safe message."""
    if isinstance(
        error,
        (ValueError, PermissionError),
    ):
        return str(error)

    return (
        "The requested operation could not be completed. "
        "Please try again or contact HR."
    )