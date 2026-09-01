from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import END

from agent.graph import (
    add_missing_policy_citations,
    choose_next_step,
    has_meaningful_content,
)
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


def test_detects_blank_and_meaningful_content():
    assert not has_meaningful_content("")
    assert not has_meaningful_content("   ")
    assert has_meaningful_content("Grounded answer")
    assert has_meaningful_content(
        [{"type": "text", "text": "Grounded answer"}]
    )


def test_adds_policy_id_from_policy_tool_evidence():
    tool_message = ToolMessage(
        content='{"rank": 1,"document_id": "POL-004"}',
        tool_call_id="call-1",
        name="policy_search_policies",
    )
    response = AIMessage(
        content="International work requires formal review."
    )

    updated = add_missing_policy_citations(
        response,
        [tool_message],
    )

    assert "Sources: POL-004" in updated.content


def test_does_not_add_policy_id_from_hr_tool():
    tool_message = ToolMessage(
        content='{"notes": "Not eligible under POL-001."}',
        tool_call_id="call-2",
        name="hr_get_pto_balance",
    )
    response = AIMessage(content="No PTO is available.")

    updated = add_missing_policy_citations(
        response,
        [tool_message],
    )

    assert updated.content == response.content


def test_does_not_duplicate_existing_policy_id():
    tool_message = ToolMessage(
        content='{"rank": 1, "document_id": "POL-005"}',
        tool_call_id="call-3",
        name="policy_search_policies",
    )
    response = AIMessage(
        content="POL-005 requires approved devices."
    )

    updated = add_missing_policy_citations(
        response,
        [tool_message],
    )

    assert updated.content == response.content


def test_system_prompt_contains_safety_rules():
    prompt = SYSTEM_PROMPT.lower()

    assert "call policy_search_policies" in prompt
    assert "explicit confirmation" in prompt
    assert "do not call hr_create_hr_ticket" in prompt
    assert "do not invent" in prompt
    assert "mcp tool is unavailable" in prompt
    assert "every policy used is cited" in prompt
    assert "response is not empty" in prompt