from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, ToolMessage

from agent.safety import MCP_UNAVAILABLE_MESSAGE
from app.main import app


class FakeAgent:
    """Return a fixed response without calling an LLM."""

    async def ainvoke(self, state):
        return {
            "messages": [
                *state["messages"],
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "policy_search_policies",
                            "args": {
                                "query": "PTO policy"
                            },
                            "id": "call-1",
                            "type": "tool_call",
                        }
                    ],
                ),
                ToolMessage(
                    name="policy_search_policies",
                    tool_call_id="call-1",
                    content=(
                        '[{"document_id": "POL-001", '
                        '"title": "Paid Time Off Policy", '
                        '"section": "1. Purpose", '
                        '"page_number": 0, '
                        '"source_file": "POL-001-paid-time-off-policy.md", '
                        '"snippet": "Full-time employees accrue PTO."}]'
                    ),
                ),
                AIMessage(content="Test agent response."),
            ]
        }


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "healthy"
    assert payload["application"] == "Horizon HR Policy Agent"
    assert payload["mcp"]["policy"] == "not_connected"
    assert payload["mcp"]["hr"] == "not_connected"


def test_home_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "Horizon HR Policy Agent" in response.text
    assert 'id="chat-form"' in response.text
    assert 'id="health-status"' in response.text


def test_chat_endpoint():
    app.state.agent = FakeAgent()
    app.state.conversations = {}

    response = client.post(
        "/api/chat",
        json={
            "message": "What is the PTO policy?",
            "session_id": None,
        },
    )

    result = response.json()

    assert response.status_code == 200
    assert result["answer"] == "Test agent response."
    assert result["session_id"]
    assert result["citations"][0]["document_id"] == "POL-001"
    assert result["citations"][0]["snippet"]
    assert result["tool_trace"][0]["tool"] == "policy_search_policies"


def test_chat_without_agent_returns_safe_message():
    app.state.agent = None
    app.state.conversations = {}

    response = client.post(
        "/api/chat",
        json={
            "message": "What is the PTO policy?",
            "session_id": None,
        },
    )

    result = response.json()

    assert response.status_code == 200
    assert result["answer"] == MCP_UNAVAILABLE_MESSAGE
    assert result["citations"] == []
    assert result["tool_trace"] == []
