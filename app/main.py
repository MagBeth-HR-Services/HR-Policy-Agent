from contextlib import asynccontextmanager
from logging import getLogger
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from agent.graph import build_hr_agent
from agent.mcp_client import load_agent_tools
from agent.safety import (
    MCP_UNAVAILABLE_MESSAGE,
    safe_error_message,
)
from agent.traces import collect_citations, collect_tool_trace


PROJECT_ROOT = Path(__file__).resolve().parents[1]
logger = getLogger("horizon.hr_agent")

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


class Citation(BaseModel):
    """A policy snippet returned to the client."""

    document_id: str
    title: str = ""
    section: str = ""
    page_number: int = 0
    source_file: str = ""
    snippet: str = ""


class ToolTraceItem(BaseModel):
    """One MCP tool call shown in the operational trace."""

    tool: str
    arguments: dict = Field(default_factory=dict)
    output_summary: str = ""


class ChatResponse(BaseModel):
    """Data returned by the chat endpoint."""

    session_id: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    tool_trace: list[ToolTraceItem] = Field(
        default_factory=list
    )


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create the agent once when the web application starts."""
    tools = await load_agent_tools()
    application.state.agent = build_hr_agent(tools)
    application.state.mcp_tools = {
        tool.name: tool
        for tool in tools
    }
    application.state.conversations = {}

    yield

    application.state.conversations.clear()
    application.state.mcp_tools = {}
    application.state.agent = None


app = FastAPI(
    title="Horizon HR Policy Agent",
    description=(
        "Agentic HR policy assistant using RAG, MCP, "
        "LangGraph, and SQLite."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.state.agent = None
app.state.conversations = {}
app.state.mcp_tools = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Display the chat webpage."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


async def mcp_connectivity_status() -> dict[str, str]:
    """Call MCP health tools when they were discovered at startup."""
    status = {
        "policy": "not_connected",
        "hr": "not_connected",
    }
    mcp_tools = getattr(app.state, "mcp_tools", {}) or {}
    health_tools = {
        "policy": "policy_health_check",
        "hr": "hr_health_check",
    }

    for key, tool_name in health_tools.items():
        tool = mcp_tools.get(tool_name)

        if tool is None:
            continue

        try:
            await tool.ainvoke({})
            status[key] = "connected"
        except Exception:
            status[key] = "unavailable"

    return status


@app.get("/health")
async def health_check() -> dict:
    """Return application and MCP connectivity status."""
    mcp = await mcp_connectivity_status()
    agent_ready = getattr(app.state, "agent", None) is not None
    mcp_connected = all(
        value == "connected"
        for value in mcp.values()
    )

    if agent_ready and not mcp_connected:
        status = "degraded"
    else:
        status = "healthy"

    return {
        "status": status,
        "application": "Horizon HR Policy Agent",
        "mcp": mcp,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a user message through the HR agent."""
    session_id = request.session_id or str(uuid4())
    agent = getattr(app.state, "agent", None)

    if agent is None:
        return ChatResponse(
            session_id=session_id,
            answer=MCP_UNAVAILABLE_MESSAGE,
            citations=[],
            tool_trace=[],
        )

    conversation = app.state.conversations.setdefault(
        session_id,
        [],
    )

    conversation.append(
        HumanMessage(content=request.message.strip())
    )

    try:
        result = await agent.ainvoke(
            {"messages": conversation}
        )
    except Exception as error:
        conversation.pop()
        logger.exception("Chat agent invocation failed.")

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
        citations=collect_citations(updated_conversation),
        tool_trace=collect_tool_trace(updated_conversation),
    )
