from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from agent.mcp_client import load_agent_tools
from agent.model import create_chat_model
from agent.prompts import SYSTEM_PROMPT
from agent.safety import contains_invalid_employee_reference


def choose_next_step(state: MessagesState):
    """Route the graph based on whether the LLM requested a tool."""
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


def build_hr_agent(tools):
    """Build and compile the HR agent workflow from MCP tools."""
    model = create_chat_model()
    model_with_tools = model.bind_tools(tools)

    async def call_model(state: MessagesState):
        latest_user_message = next(
            (
                message
                for message in reversed(state["messages"])
                if isinstance(message, HumanMessage)
            ),
            None,
        )

        if (
            latest_user_message
            and isinstance(latest_user_message.content, str)
            and contains_invalid_employee_reference(
                latest_user_message.content
            )
        ):
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "Employee ID must use the format E followed by "
                            "four digits, such as E1002."
                        )
                    )
                ]
            }

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        response = await model_with_tools.ainvoke(messages)

        return {"messages": [response]}

    workflow = StateGraph(MessagesState)

    workflow.add_node("agent", call_model)
    workflow.add_node(
        "tools",
        ToolNode(tools, handle_tool_errors=True),
    )

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


async def create_hr_agent():
    """Load MCP tools and compile the HR agent workflow."""
    tools = await load_agent_tools()
    return build_hr_agent(tools)