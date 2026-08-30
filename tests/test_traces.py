import json

from langchain_core.messages import AIMessage, ToolMessage

from agent.traces import (
    collect_citations,
    collect_tool_names,
    collect_tool_trace,
    unwrap_mcp_content,
)


POLICY_RESULT = {
    "rank": 1,
    "score": 0.41,
    "document_id": "POL-004",
    "title": "Temporary Work Location Policy",
    "section": "4. Policy Requirements",
    "page_number": 0,
    "chunk_id": "POL-004-C0008",
    "source_file": "POL-004-temporary-work-location-policy.md",
    "snippet": "International work is normally limited to twenty business days.",
    "content": "International work is normally limited to twenty business days.",
}


def test_unwraps_mcp_text_wrappers():
    wrapped = [
        {
            "type": "text",
            "text": json.dumps(POLICY_RESULT),
        }
    ]

    parsed = unwrap_mcp_content(json.dumps(wrapped))

    assert parsed["document_id"] == "POL-004"


def test_collects_tool_trace_and_citations():
    messages = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "policy_search_policies",
                    "args": {"query": "six weeks abroad"},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        ),
        ToolMessage(
            name="policy_search_policies",
            tool_call_id="call-1",
            content=json.dumps([POLICY_RESULT]),
        ),
        AIMessage(content="See POL-004. The request is not approved."),
    ]

    assert collect_tool_names(messages) == [
        "policy_search_policies"
    ]

    trace = collect_tool_trace(messages)

    assert len(trace) == 1
    assert trace[0]["tool"] == "policy_search_policies"
    assert trace[0]["arguments"]["query"] == "six weeks abroad"
    assert "POL-004" in trace[0]["output_summary"]

    citations = collect_citations(messages)

    assert len(citations) == 1
    assert citations[0]["document_id"] == "POL-004"
    assert citations[0]["snippet"].startswith("International work")
