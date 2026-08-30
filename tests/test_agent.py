from langchain_core.messages import AIMessage
from langgraph.graph import END

from agent.graph import choose_next_step
from agent.prompts import SYSTEM_PROMPT


def test_routes_tool_calls_to_tools_node():
    message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "policy_search_policies",
                "args": {
                    "query": "What is the remote-work policy?"
                },
                "id": "call-1",
                "type": "tool_call",
            }
        ],
    )

    state = {"messages": [message]}

    assert choose_next_step(state) == "tools"


def test_ends_when_no_tool_is_requested():
    message = AIMessage(
        content="Here is the final response."
    )

    state = {"messages": [message]}

    assert choose_next_step(state) == END


def test_system_prompt_contains_safety_rules():
    prompt = SYSTEM_PROMPT.lower()

    assert "call policy_search_policies" in prompt
    assert "explicit confirmation" in prompt
    assert "do not call hr_create_hr_ticket" in prompt
    assert "do not invent" in prompt
    assert "mcp tool is unavailable" in prompt