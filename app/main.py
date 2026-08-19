from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from agent.graph import create_hr_agent
from agent.safety import safe_error_message


PROJECT_ROOT = Path(__file__).resolve().parents[1]

templates = Jinja2Templates(
    directory=str(PROJECT_ROOT / "app" / "templates")
)


class ChatRequest(BaseModel):
    """Data accepted by the chat endpoint."""

    message: str = Field(
        min_length=1,
        max_length=2000,
    )
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Data returned by the chat endpoint."""

    session_id: str
    answer: str


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create the agent once when the web application starts."""
    application.state.agent = await create_hr_agent()
    application.state.conversations = {}

    yield

    application.state.conversations.clear()


app = FastAPI(
    title="Horizon HR Policy Agent",
    description=(
        "Agentic HR policy assistant using RAG, MCP, "
        "LangGraph, and SQLite."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Display the chat webpage."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/health")
async def health_check() -> dict:
    """Return the web application's health status."""
    return {
        "status": "healthy",
        "application": "Horizon HR Policy Agent",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a user message through the HR agent."""
    session_id = request.session_id or str(uuid4())

    conversation = app.state.conversations.setdefault(
        session_id,
        [],
    )

    conversation.append(
        HumanMessage(content=request.message.strip())
    )

    try:
        result = await app.state.agent.ainvoke(
            {"messages": conversation}
        )
    except Exception as error:
        conversation.pop()

        raise HTTPException(
            status_code=500,
            detail=safe_error_message(error),
        ) from error

    updated_conversation = result["messages"]
    app.state.conversations[session_id] = (
        updated_conversation
    )

    answer = str(updated_conversation[-1].content)

    return ChatResponse(
        session_id=session_id,
        answer=answer,
    )