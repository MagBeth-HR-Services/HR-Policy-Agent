import asyncio

from agent.mcp_client import load_agent_tools


async def main() -> None:
    tools = await load_agent_tools()

    print("Tools available to the agent:")

    for tool in tools:
        print(f"- {tool.name}")


if __name__ == "__main__":
    asyncio.run(main())