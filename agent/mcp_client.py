import sys
from pathlib import Path

from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def create_mcp_client() -> MultiServerMCPClient:
    """Configure connections to both local MCP servers."""
    return MultiServerMCPClient(
        {
            "policy": {
                "command": sys.executable,
                "args": [
                    "-m",
                    "mcp_servers.policy_server",
                ],
                "transport": "stdio",
                "cwd": str(PROJECT_ROOT),
            },
            "hr": {
                "command": sys.executable,
                "args": [
                    "-m",
                    "mcp_servers.hr_server",
                ],
                "transport": "stdio",
                "cwd": str(PROJECT_ROOT),
            },
        },
        tool_name_prefix=True,
        handle_tool_errors=True,
    )


async def load_agent_tools():
    """Load LangChain-compatible tools from both MCP servers."""
    client = create_mcp_client()
    return await client.get_tools()