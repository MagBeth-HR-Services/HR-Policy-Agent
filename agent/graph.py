import re

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from agent.mcp_client import load_agent_tools
from agent.model import create_chat_model
from agent.prompts import SYSTEM_PROMPT
from agent.safety import contains_invalid_employee_reference
from agent.traces import messages_for_latest_turn


RANK_ONE_POLICY_PATTERN = re.compile(
    r'"rank"\s*:\s*1.*?"document_id"\s*:\s*"(POL-\d{3})"',
    re.IGNORECASE | re.DOTALL,
)


def choose_next_step(state: MessagesState):
    """Route the graph based on whether the LLM requested a tool."""
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


def content_as_text(content) -> str:
    """Convert message content into plain text."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, dict):
                text = block.get("text", "")
                if isinstance(text, str):
                    text_parts.append(text)
            else:
                text_parts.append(str(block))

        return "\n".join(text_parts)

    if content is None:
        return ""

    return str(content)


def has_meaningful_content(content) -> bool:
    """Return True when a model response contains usable text."""
    return bool(content_as_text(content).strip())


def get_primary_policy_ids(messages) -> list[str]:
    """Collect only rank-one policy IDs from policy-search evidence."""
    policy_ids = set()

    for message in messages:
        if not isinstance(message, ToolMessage):
            continue

        tool_name = message.name or ""

        if "search_policies" not in tool_name:
            continue

        content = content_as_text(message.content)

        for policy_id in RANK_ONE_POLICY_PATTERN.findall(content):
            policy_ids.add(policy_id.upper())

    return sorted(policy_ids)


def add_missing_policy_citations(response, messages):
    """Append rank-one policy IDs supported by retrieved evidence."""
    if response.tool_calls:
        return response

    answer = content_as_text(response.content).strip()

    if not answer:
        return response

    retrieved_policy_ids = get_primary_policy_ids(messages)

    missing_policy_ids = [
        policy_id
        for policy_id in retrieved_policy_ids
        if policy_id.lower() not in answer.lower()
    ]

    if not missing_policy_ids:
        return response

    citations = ", ".join(missing_policy_ids)
    updated_answer = f"{answer}\n\nSources: {citations}"

    return response.model_copy(
        update={"content": updated_answer}
    )


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

        if (
            not response.tool_calls
            and not has_meaningful_content(response.content)
        ):
            retry_messages = [
                *messages,
                SystemMessage(
                    content=(
                        "Your previous response was empty. Process the "
                        "user's request now. Call every required tool and "
                        "then provide a clear, grounded answer."
                    )
                ),
            ]
            response = await model_with_tools.ainvoke(retry_messages)

        if (
            not response.tool_calls
            and not has_meaningful_content(response.content)
        ):
            response = AIMessage(
                content=(
                    "I could not complete this request because the model "
                    "returned an empty response. Please try again or "
                    "contact HR."
                )
            )

        response = add_missing_policy_citations(
            response,
            messages_for_latest_turn(state["messages"]),
        )

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