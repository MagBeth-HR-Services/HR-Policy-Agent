# Horizon HR Policy Agent — Architecture

## 1. Architecture Purpose

The Horizon HR Policy Agent combines:

- A browser chat interface
- A FastAPI web application
- A LangGraph agent
- An OpenRouter-hosted language model
- A multi-server MCP client
- Two FastMCP servers
- Policy retrieval through Chroma
- Synthetic HR data stored in SQLite

The architecture currently runs locally and through GitHub Actions. Single-service deployment to Render remains planned.

## 2. Current Technology Stack

| Component | Technology | Current status |
| --- | --- | --- |
| Programming language | Python 3.14 | Implemented |
| Web application | FastAPI | Implemented |
| Web server | Uvicorn | Implemented |
| Browser interface | HTML, CSS, and JavaScript | Implemented |
| Agent orchestration | LangGraph `StateGraph` | Implemented |
| LLM interface | LangChain `ChatOpenAI` | Implemented |
| LLM provider | OpenRouter | Implemented and configurable |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | Implemented locally on CPU |
| Vector database | Chroma | Implemented |
| Structured HR storage | SQLite | Implemented |
| MCP implementation | FastMCP | Implemented |
| MCP client | LangChain `MultiServerMCPClient` | Implemented |
| MCP transport | `stdio` | Implemented |
| Testing | Pytest | Implemented |
| Continuous integration | GitHub Actions | Implemented |
| Deployment target | Render | Planned |

Exact package versions are pinned in `requirements.txt`.

## 3. Current Component Diagram

```text
User browser
     |
     v
FastAPI web application
  GET  /
  POST /api/chat
  GET  /health
     |
     v
LangGraph agent --------------------------> OpenRouter LLM
     |
     v
MultiServerMCPClient
     |
     +---- stdio ----> Policy FastMCP server
     |                    |
     |                    v
     |              RAG retrieval layer
     |                    |
     |                    v
     |              Chroma vector index
     |                    |
     |                    v
     |              Fictional policies
     |
     +---- stdio ----> HR FastMCP server
                          |
                          v
                    HR service layer
                          |
                          v
                    SQLite database
                          |
                          v
                    Synthetic HR data
```

The policy ingestion process runs separately before application startup:

```text
Markdown and PDF policies
          |
          v
Document loaders
          |
          v
Heading-aware and recursive chunking
          |
          v
Local embedding model
          |
          v
Persistent Chroma collection
```

## 4. FastAPI Application

The FastAPI application is defined in `app/main.py`.

### Current endpoints

#### `GET /`

Returns the browser chat interface.

#### `POST /api/chat`

Accepts:

```json
{
  "message": "User message",
  "session_id": "optional-session-id"
}
```

Returns:

```json
{
  "session_id": "conversation-session-id",
  "answer": "Agent response",
  "citations": [
    {
      "document_id": "POL-004",
      "title": "Temporary Work Location Policy",
      "section": "4. Policy Requirements",
      "page_number": 0,
      "source_file": "POL-004-temporary-work-location-policy.md",
      "snippet": "International work is normally limited to twenty business days."
    }
  ],
  "tool_trace": [
    {
      "tool": "policy_search_policies",
      "arguments": {"query": "six weeks abroad"},
      "output_summary": "..."
    }
  ]
}
```

The application stores conversation state in process memory using the session ID.

#### `GET /health`

Returns application status and MCP connectivity:

```json
{
  "status": "healthy",
  "application": "Horizon HR Policy Agent",
  "mcp": {
    "policy": "connected",
    "hr": "connected"
  }
}
```

Values for each MCP server are `connected`, `not_connected`, or `unavailable`.

### Application lifespan

When FastAPI starts, it:

1. Creates the LangGraph agent.
2. Discovers MCP tools through the multi-server client.
3. Stores the agent in application state.
4. Creates an in-memory conversation dictionary.

Conversation state is cleared when the application stops.

### Pending API improvements

Live Render verification of both demo workflows is still required. Structured citations, snippets, tool traces, and MCP health status are implemented.

## 5. Browser Interface

The browser interface is stored in `app/templates/index.html`.

It currently:

- Accepts user messages
- Sends them to `POST /api/chat`
- Preserves the returned session ID
- Displays the final agent answer
- Displays structured citations and snippets
- Displays a concise MCP tool-call trace
- Shows application and MCP health status

## 6. LangGraph Agent

The agent is defined in `agent/graph.py`.

It uses two primary nodes:

```text
START
  |
  v
agent
  |
  +-- no tool call --> END
  |
  +-- tool call ----> tools
                         |
                         v
                       agent
```

### Agent node

The agent node:

1. Checks the original user message for invalid employee-ID references.
2. Adds the system prompt to the conversation.
3. Sends the conversation and bound MCP tools to the configured LLM.
4. Returns the model response.

### Tool node

LangGraph’s `ToolNode` executes MCP tools selected by the LLM and returns their results to the agent node.

The loop continues until the LLM produces a response without another tool call.

### Model configuration

`agent/model.py` creates a `ChatOpenAI` client configured for OpenRouter.

Configuration is read from environment variables:

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`

The model uses:

- Temperature `0`
- A 60-second timeout
- Up to two retries

The model name is configurable rather than hard-coded in Python.

## 7. MCP Client

The MCP client is defined in `agent/mcp_client.py`.

It creates one `MultiServerMCPClient` connected to two local servers:

- `policy`
- `hr`

Both servers:

- Run as Python child processes
- Use the same Python interpreter as the main application
- Run from the project root
- Communicate through `stdio`

Tool-name prefixes are enabled, producing names such as:

- `policy_search_policies`
- `hr_get_pto_balance`

Tool errors are returned in a form the agent can handle.

## 8. Policy MCP Server

The policy server is defined in `mcp_servers/policy_server.py`.

It exposes:

### `policy_health_check`

Confirms that the policy server is responding.

### `policy_search_policies`

Accepts:

- Search query
- Number of results
- Optional policy document ID
- Optional result diversification

It returns ranked citation-ready evidence containing:

- Rank
- Relevance score
- Document ID
- Policy title
- Section
- Page number
- Chunk ID
- Source filename
- Snippet
- Full chunk content

The Chroma store is loaded before the MCP server begins accepting requests. This avoids loading the embedding model during the first tool request.

## 9. HR MCP Server

The HR server is defined in `mcp_servers/hr_server.py`.

It exposes:

### `hr_health_check`

Confirms that the HR server is responding.

### `hr_get_employee_summary`

Returns a limited synthetic employee profile.

### `hr_get_pto_balance`

Returns synthetic PTO balance information.

### `hr_get_benefits_status`

Returns synthetic benefits information.

### `hr_create_hr_ticket`

Creates a clearly labeled mock HR ticket after explicit user confirmation.

Employee IDs are validated before the HR service queries SQLite.

## 10. Policy Ingestion and Chunking

Policy ingestion is implemented under `ingestion/`.

### Supported source formats

- Markdown
- PDF

### Markdown chunking

Markdown documents are first divided using level-two and level-three headings.

### Size-based chunking

Heading sections and PDF pages are processed with a recursive character splitter configured with:

- Chunk size: 1,000 characters
- Chunk overlap: 150 characters

This approach preserves policy structure when possible while limiting chunk size.

### Deterministic metadata

Each chunk receives stable citation metadata:

- Document ID
- Title
- Section
- Page number
- Chunk index
- Stable chunk ID
- Source filename
- Source format
- Source snippet

The current corpus produces 177 chunks.

## 11. Embeddings and Chroma

The vector-store implementation is in `ingestion/vector_store.py`.

### Embedding model

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model:

- Runs locally
- Uses CPU
- Normalizes embeddings
- Does not require an embedding API key

### Chroma collection

The collection is named:

```text
horizon_policies
```

The default local path is:

```text
data/chroma
```

The Chroma index is generated and excluded from Git because it can be reproduced from the committed policy documents.

## 12. Policy Retrieval

Retrieval is implemented in `rag/retrieval.py`.

It supports:

- Semantic similarity search
- Configurable `k` between 1 and 10
- Optional filtering by policy document ID
- Optional diversification across policy documents
- Relevance scores
- Citation-ready structured results

The default policy MCP search returns five results.

The vector store is cached within the policy-server process after it is opened.

## 13. SQLite Data Layer

SQLite access is implemented under `database/`.

The default database path is:

```text
data/hr_data.db
```

The database contains:

- Employee profiles
- Manager relationships
- PTO balances
- Benefits records
- Mock HR tickets

The database is built from committed JSON files under `mock_data/`.

The generated database is excluded from Git because it can be recreated with:

```cmd
python -m database.seed
```

Foreign-key enforcement is enabled for every SQLite connection.

## 14. Safety Architecture

Safety controls exist at several layers.

### Before the LLM

The LangGraph agent checks the original user message for an employee reference that omits the required `E` prefix.

This prevents the LLM from changing an invalid ID such as `1002` into a valid employee ID and exposing data.

### MCP tool boundary

The HR MCP server validates every employee ID using the `E####` format.

### HR service boundary

Ticket creation requires a `confirmed_by_user` value and rejects unconfirmed requests.

### System prompt

The system prompt requires the agent to:

- Use policy tools for company-policy answers
- Avoid unsupported general HR knowledge
- Use minimal employee information
- Avoid approving HR requests
- Require explicit ticket confirmation
- Avoid speculation when records are missing
- Escalate missing, unclear, or conflicting evidence

### Error handling

Expected validation errors are converted into readable messages.

Unexpected internal errors are replaced with a generic safe response.

## 15. Testing and Evaluation

The automated test suite covers:

- Policy loading
- Citation metadata
- Chunking
- Retrieval (top-k, filter, diversify)
- Database creation and services
- Employee-ID validation
- Confirmation logic
- Agent behavior
- FastAPI import and endpoints, including citations and tool traces
- MCP tool registration and an HR MCP stdio tool call

GitHub Actions successfully runs the project on a clean Linux runner.

The current evaluation system combines:

- Deterministic tool-selection checks
- Deterministic citation checks
- Explicit forbidden-phrase checks
- An LLM judge for correctness, grounding, safety, and semantic criteria

The evaluation dataset contains 24 cases with gold answers. Aggregate metrics and a no-policy-search ablation are implemented in the runner. A full OpenRouter run of the expanded set is still required, along with deployed cold-start measurement.

Still required:

- Record live evaluation metrics for all 24 cases
- Measure deployed cold-start latency
- Complete Render Standard deployment

## 16. Current Local Runtime

Before starting the application locally:

1. Build the Chroma index.
2. Seed the SQLite database.
3. Start FastAPI with Uvicorn.

```cmd
python -m ingestion.build_index --recreate
python -m database.seed
python -m uvicorn app.main:app --reload
```

FastAPI starts both MCP servers as local child processes when it creates the agent.

## 17. Planned Deployment Architecture

The planned Render deployment will use one web service containing:

- FastAPI
- LangGraph
- The MCP client
- Both MCP server subprocesses
- Chroma
- SQLite
- Policy documents
- Synthetic source data

The deployment build process is expected to:

1. Install dependencies.
2. Build the Chroma policy index.
3. Seed the SQLite database.
4. Start the FastAPI application with Uvicorn.

Render environment variables will supply the API key, model name, and data paths.

Because Render’s free filesystem is temporary, Chroma and SQLite will be recreated during deployment. Mock ticket changes will not be durable across restarts on the free service.

The final build command, start command, health URL, cold-start behavior, and persistence limitations will be documented after deployment testing.

## 18. Known Limitations and Pending Enhancements

The current architecture has these known limitations:

- Conversation state exists only in application memory.
- Conversation history is lost when the application restarts.
- SQLite ticket changes are local and non-durable across deploys.
- Chroma and the embedding model increase build and startup resource use.
- The expanded evaluation suite has not yet been re-run end-to-end against OpenRouter.
- Deployment has not yet been completed.