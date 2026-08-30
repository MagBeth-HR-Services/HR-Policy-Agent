import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from database.seed import seed_database
from mcp_servers.hr_server import mcp as hr_mcp
from mcp_servers.policy_server import mcp as policy_mcp


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_policy_mcp_registers_required_tools():
    tools = asyncio.run(policy_mcp.list_tools())
    names = {tool.name for tool in tools}

    assert names == {"health_check", "search_policies"}


def test_hr_mcp_registers_required_tools():
    tools = asyncio.run(hr_mcp.list_tools())
    names = {tool.name for tool in tools}

    assert names == {
        "health_check",
        "get_employee_summary",
        "get_pto_balance",
        "get_benefits_status",
        "create_hr_ticket",
    }


def test_hr_mcp_stdio_discovers_and_calls_a_tool(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "test_hr_data.db"
    monkeypatch.setenv("HR_DATABASE_PATH", str(database_path))
    seed_database()

    async def run_mcp_check():
        environment = os.environ.copy()
        environment["HR_DATABASE_PATH"] = str(database_path)

        server_parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_servers.hr_server"],
            env=environment,
            cwd=str(PROJECT_ROOT),
        )

        async with stdio_client(server_parameters) as (
            read_stream,
            write_stream,
        ):
            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:
                await session.initialize()

                available_tools = await session.list_tools()
                names = {
                    tool.name
                    for tool in available_tools.tools
                }

                result = await session.call_tool(
                    "get_pto_balance",
                    {"employee_id": "E1002"},
                )

                return names, result

    names, result = asyncio.run(run_mcp_check())

    assert "get_pto_balance" in names
    assert "health_check" in names

    texts = [
        item.text
        for item in result.content
        if hasattr(item, "text")
    ]

    combined = " ".join(texts)

    assert "120" in combined
    assert "E1002" in combined
