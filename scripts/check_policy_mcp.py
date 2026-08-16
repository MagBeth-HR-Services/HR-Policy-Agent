import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_servers.policy_server"],
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

            result = await session.call_tool(
                "search_policies",
                {
                    "query": (
                        "Can an employee work from "
                        "another country for six weeks?"
                    ),
                    "number_of_results": 3,
                },
            )

            print("\nTool result:")

            for content_item in result.content:
                if hasattr(content_item, "text"):
                    print(content_item.text)


if __name__ == "__main__":
    asyncio.run(main())