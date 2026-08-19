from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from app.main import app


class FakeAgent:
    """Return a fixed response without calling an LLM."""

    async def ainvoke(self, state):
        return {
            "messages": [
                *state["messages"],
                AIMessage(content="Test agent response."),
            ]
        }


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_home_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "Horizon HR Policy Agent" in response.text
    assert 'id="chat-form"' in response.text


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