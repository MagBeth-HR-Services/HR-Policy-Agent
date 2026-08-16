from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from agent.mcp_client import load_agent_tools
from agent.model import create_chat_model
from agent.prompts import SYSTEM_PROMPT


def choose_next_step(state: MessagesState):
    """Route the graph based on whether the LLM requested a tool."""
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


async def create_hr_agent():
    """Build and compile the HR agent workflow."""
    tools = await load_agent_tools()
    model = create_chat_model()
    model_with_tools = model.bind_tools(tools)

    async def call_model(state: MessagesState):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        response = await model_with_tools.ainvoke(messages)

        return {"messages": [response]}

    workflow = StateGraph(MessagesState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "agent")

    workflow.add_conditional_edges(
        "agent",
        choose_next_step,
        {
            "tools": "tools",
            END: END,
        },
    )

    workflow.add_edge("tools", "agent")

    return workflow.compile()