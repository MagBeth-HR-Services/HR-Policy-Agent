import asyncio

from langchain_core.messages import HumanMessage

from agent.graph import create_hr_agent


async def main() -> None:
    print("Starting Horizon HR Policy Agent...")

    agent = await create_hr_agent()
    conversation = []

    print("Agent ready. Type 'quit' to exit.")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        if not user_input:
            continue

        conversation.append(
            HumanMessage(content=user_input)
        )

        result = await agent.ainvoke(
            {"messages": conversation}
        )

        conversation = result["messages"]
        final_message = conversation[-1]

        print(f"\nAgent: {final_message.content}")


if __name__ == "__main__":
    asyncio.run(main())