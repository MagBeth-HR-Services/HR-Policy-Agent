import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def print_result(label: str, result) -> None:
    print(f"\n{label}:")

    for content_item in result.content:
        if hasattr(content_item, "text"):
            print(content_item.text)


async def main() -> None:
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_servers.hr_server"],
    )

    async with stdio_client(
        server_parameters
    ) as (read_stream, write_stream):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:
            await session.initialize()

            available_tools = await session.list_tools()

            print("Available MCP tools:")

            for tool in available_tools.tools:
                print(f"- {tool.name}")

            employee_result = await session.call_tool(
                "get_employee_summary",
                {"employee_id": "E1002"},
            )

            await print_result(
                "Employee result",
                employee_result,
            )

            pto_result = await session.call_tool(
                "get_pto_balance",
                {"employee_id": "E1002"},
            )

            await print_result(
                "PTO result",
                pto_result,
            )

            benefits_result = await session.call_tool(
                "get_benefits_status",
                {"employee_id": "E1002"},
            )

            await print_result(
                "Benefits result",
                benefits_result,
            )


if __name__ == "__main__":
    asyncio.run(main())