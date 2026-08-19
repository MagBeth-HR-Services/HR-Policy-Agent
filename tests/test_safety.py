import pytest

from agent.safety import (
    contains_invalid_employee_reference,
    is_explicit_confirmation,
    safe_error_message,
    validate_employee_id,
)


@pytest.mark.parametrize(
    ("provided_id", "expected_id"),
    [
        ("E1002", "E1002"),
        ("e1002", "E1002"),
        ("  E1002  ", "E1002"),
    ],
)
def test_valid_employee_ids_are_normalized(
    provided_id,
    expected_id,
):
    assert validate_employee_id(provided_id) == expected_id


@pytest.mark.parametrize(
    "provided_id",
    [
        "1002",
        "EMP1002",
        "E102",
        "E10022",
        "",
    ],
)
def test_invalid_employee_ids_are_rejected(provided_id):
    with pytest.raises(
        ValueError,
        match="format E followed by four digits",
    ):
        validate_employee_id(provided_id)


def test_employee_reference_without_e_prefix_is_detected():
    message = "Show the PTO balance for employee 1002."

    assert contains_invalid_employee_reference(message) is True


def test_valid_employee_reference_is_not_rejected():
    message = "Show the PTO balance for employee E1002."

    assert contains_invalid_employee_reference(message) is False


@pytest.mark.parametrize(
    "message",
    [
        "yes",
        "YES",
        "I confirm",
        "yes, create the ticket",
        "  confirmed  ",
    ],
)
def test_clear_confirmations_are_accepted(message):
    assert is_explicit_confirmation(message) is True


@pytest.mark.parametrize(
    "message",
    [
        "maybe",
        "I need help",
        "tell me more",
        "not yet",
        "",
    ],
)
def test_unclear_responses_are_not_confirmation(message):
    assert is_explicit_confirmation(message) is False


def test_expected_errors_are_safe_to_display():
    error = ValueError("Employee E9999 was not found.")

    assert safe_error_message(error) == (
        "Employee E9999 was not found."
    )


def test_unexpected_errors_are_hidden():
    error = RuntimeError(
        "Internal database connection details"
    )

    result = safe_error_message(error)

    assert "Internal database" not in result
    assert "contact HR" in result