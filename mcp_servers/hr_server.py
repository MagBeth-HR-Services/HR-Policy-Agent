from mcp.server.fastmcp import FastMCP

from agent.safety import validate_employee_id
from database.hr_service import (
    create_hr_ticket as create_ticket_record,
    get_benefits_status as retrieve_benefits_status,
    get_employee_summary as retrieve_employee_summary,
    get_pto_balance as retrieve_pto_balance,
)


mcp = FastMCP("Horizon HR Operations Server")


@mcp.tool()
def health_check() -> str:
    """Confirm that the HR Operations MCP server is responding."""
    return "HR Operations MCP server is healthy."


@mcp.tool()
def get_employee_summary(employee_id: str) -> dict:
    """Retrieve a limited employee profile using an employee ID."""
    validated_id = validate_employee_id(employee_id)

    return retrieve_employee_summary(validated_id)


@mcp.tool()
def get_pto_balance(employee_id: str) -> dict:
    """Retrieve an employee's current PTO balance."""
    validated_id = validate_employee_id(employee_id)

    return retrieve_pto_balance(validated_id)


@mcp.tool()
def get_benefits_status(employee_id: str) -> dict:
    """Retrieve an employee's current benefits status."""
    validated_id = validate_employee_id(employee_id)

    return retrieve_benefits_status(validated_id)


@mcp.tool()
def create_hr_ticket(
    employee_id: str,
    category: str,
    summary: str,
    confirmed_by_user: bool,
) -> dict:
    """
    Create an HR ticket.

    confirmed_by_user must be true only when the user has explicitly
    approved creating the ticket.
    """
    validated_id = validate_employee_id(employee_id)

    return create_ticket_record(
        employee_id=validated_id,
        category=category,
        summary=summary,
        confirmed_by_user=confirmed_by_user,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")