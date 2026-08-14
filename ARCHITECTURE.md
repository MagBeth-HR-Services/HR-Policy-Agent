# HR Policy Agent - Architecture

## 1. Architecture Goal

The application will use a simple, modular architecture that can run locally and as one modest free-tier web service. It will combine a browser chat interface, an API, a LangGraph agent, genuine MCP tool calls, policy retrieval through Chroma, synthetic HR data in SQLite, and an OpenRouter-hosted language model.

The design intentionally reuses technologies practiced in the course while meeting the project's API, MCP, RAG, safety, traceability, testing, and deployment requirements.

## 2. Technology Stack

| Component | Selected technology | Reason |
| --- | --- | --- |
| Programming language | Python | Used throughout the course examples and supported by all selected libraries |
| Web application and API | FastAPI | Provides the browser UI, `/chat`, and `/health` from one web process |
| Browser interface | Small HTML, CSS, and JavaScript chat page | Keeps the UI lightweight while consuming the structured FastAPI response |
| Agent orchestration | LangGraph | Supports the familiar model-to-tools-to-model workflow and explicit agent state |
| LLM integration | LangChain `ChatOpenAI` interface | Compatible with LangGraph tool calling and OpenRouter's OpenAI-compatible API |
| LLM provider | OpenRouter | Provides configurable model access and has already been used in the course work |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | Free, local, lightweight, and familiar from the course RAG exercise |
| Vector database | Chroma | Persistent local vector storage already practiced in the course |
| Document processing | LangChain document loaders and text splitters | Supports multiple formats, metadata, and configurable chunking |
| MCP server implementation | FastMCP | Familiar tool-definition approach from the course agent project |
| MCP client | `MultiServerMCPClient` from LangChain MCP Adapters | Discovers MCP tools and converts them into tools usable by LangGraph |
| MCP transport | `stdio` | Simple local subprocess transport suitable for a single deployed service |
| Structured HR storage | SQLite | Lightweight, file-based, free, and familiar from the course agent project |
| Automated testing | pytest | Standard Python unit, integration, and smoke testing framework |
| CI/CD | GitHub Actions | Meets the assignment requirement for automated checks on pushes or pull requests |
| Initial deployment target | Render | Candidate for running the complete system as one web service |

Package versions and the final hosted model will be selected and pinned only after compatibility and deployment-resource testing.

## 3. Component Diagram

```text
User's browser
      |
      v
FastAPI application
  - GET  /         browser chat interface
  - POST /chat     structured agent response
  - GET  /health   application and MCP status
      |
      v
LangGraph HR agent -----------------------> OpenRouter LLM
      |
      v
MultiServerMCPClient
      |
      +---- stdio ----> Policy MCP server
      |                    |
      |                    +--> Chroma RAG index
      |                    +--> Policy documents
      |
      +---- stdio ----> HR Operations MCP server
                           |
                           +--> SQLite employee records
                           +--> SQLite PTO balances
                           +--> SQLite mock HR tickets

Policy ingestion and indexing
      |
      +--> LangChain loaders and splitters
      +--> Local Hugging Face embedding model
      +--> Persistent Chroma index
```

## 4. Component Responsibilities

### FastAPI application

- Serve the browser chat page.
- Accept user messages through `POST /chat`.
- Validate incoming request data.
- Invoke the LangGraph agent.
- Return the final answer, citations, supporting snippets, operational trace, confirmation state, and errors in structured JSON.
- Report application and MCP connectivity status through `GET /health`.
- Avoid placing policy, database, or tool logic directly in route handlers.

### Browser chat interface

- Send user messages to `POST /chat`.
- Display the assistant's final answer.
- Display citations and supporting snippets separately from the answer.
- Display a concise operational trace suitable for development and demonstration.
- Clearly show when clarification or confirmation is required.

### LangGraph HR agent

- Interpret the user's intent.
- Decide whether the request requires policy retrieval, structured HR data, or both.
- Select and call tools discovered through MCP.
- Continue the model-tools-model loop until it can answer, clarify, escalate, or request confirmation.
- Combine tool outputs into a grounded response.
- Preserve only operational trace information, not hidden chain-of-thought.

### Policy MCP server

- Expose policy retrieval tools through MCP.
- Search the Chroma index for relevant policy chunks.
- Retrieve a specific document section using stable identifiers.
- Return structured evidence containing document ID, title, section, page or location where applicable, snippet, and relevance information.
- Support preliminary policy-compliance checks using explicit policy rules and retrieved evidence.

### HR Operations MCP server

- Look up synthetic employee profiles.
- Look up synthetic PTO balances.
- Create clearly labeled mock HR tickets only when the application has received explicit confirmation.
- Return structured results and useful not-found errors.
- Never connect to a real HR system or use real employee data.

### Policy ingestion and indexing process

- Load at least two supported source formats where feasible.
- Clean and split documents using a justified, deterministic strategy.
- Preserve citation metadata throughout ingestion and chunking.
- Create embeddings locally with `all-MiniLM-L6-v2`.
- Build or refresh the persistent Chroma index reproducibly.

### OpenRouter LLM

- Interpret requests and select bound tools.
- Synthesize responses from tool results and policy evidence.
- Use a model name supplied by configuration rather than one fixed in source code.
- Receive credentials only through environment variables.

## 5. MCP Server Separation

The project will use two MCP servers.

### Policy server

Planned tool responsibilities:

- `search_policy_documents`
- `get_policy_section`
- `check_policy_compliance`

### HR Operations server

Planned tool responsibilities:

- `lookup_employee_profile`
- `check_pto_balance`
- `create_mock_hr_ticket`

This separation keeps policy evidence and employee operations conceptually distinct, resembles the two-server course example, and provides a clear architecture to explain in the demonstration.

The final tool schemas and exact return objects will be designed before implementation.

## 6. Request Data Flow

For a typical multi-step request:

1. The browser sends the user's message to `POST /chat`.
2. FastAPI validates the request and invokes the LangGraph agent.
3. LangGraph sends the conversation state to the configured OpenRouter model with the discovered MCP tools bound.
4. The model requests one or more appropriate tool calls.
5. `MultiServerMCPClient` sends each call to the correct MCP server over `stdio`.
6. The MCP server reads the policy index or synthetic SQLite data and returns a structured result.
7. LangGraph records a concise operational trace and supplies tool results back to the model.
8. The loop continues until the agent can answer, request clarification, recommend escalation, or ask for confirmation.
9. FastAPI returns structured JSON containing the result and supporting information.
10. The browser displays the response, evidence, and trace in distinct sections.

## 7. Planned API Shape

### `GET /`

Return the lightweight browser chat interface.

### `POST /chat`

Accept a user message and conversation context. The response will be designed to include:

- Final answer
- Policy citations
- Supporting snippets
- Concise MCP tool-call trace
- Clarification or escalation information
- Confirmation requirement and pending mock action, when applicable
- Safe, readable error information

The exact request and response schemas will be defined when the API is implemented.

### `GET /health`

Return JSON describing:

- Overall application status
- Agent initialization status
- MCP tool discovery or connectivity status where feasible
- Non-sensitive version or configuration information useful for grading

The health response will never expose API keys or other secrets.

## 8. Persistence and Deployment Model

The initial deployment will use one web service containing:

- The FastAPI web process
- The LangGraph agent and MCP client
- Both local MCP server subprocesses
- The policy files
- The persistent Chroma index, or a reproducible index built during deployment
- The synthetic SQLite data files

This avoids paid databases and separate paid services. The final index build strategy will be chosen after deployment-resource and startup-time testing.

Render is the initial deployment candidate. Current plan capabilities, resource limits, startup behavior, and deployment commands will be verified before deployment. If Render is unsuitable at that time, an equivalent free-tier or zero-cost platform may be selected and documented.

## 9. Configuration and Secrets

- `OPENROUTER_API_KEY` will be read from an environment variable.
- The OpenRouter model name will be configurable through an environment variable or application setting.
- File locations and deployment-specific settings will use centralized configuration.
- A safe `.env.example` will document required variables without real values.
- `.env`, local virtual environments, and secret-bearing files will be excluded from Git.
- No API key will be assigned directly in Python source code.

## 10. Safety and Traceability

- All policy and employee information will be fictional or synthetic.
- The agent will use evidence returned through MCP tools rather than asserting unsupported policy facts.
- Missing evidence will result in a limitation statement, clarification, or escalation.
- Consequential-looking actions will be mock actions.
- Explicit user confirmation will be required before creating a mock HR ticket or similar record.
- Operational traces will contain tool names, arguments, summarized results, retrieved sources, and the response basis.
- Hidden chain-of-thought will not be recorded or displayed.
- Tool and application failures will be translated into safe, useful responses.

## 11. Testing Boundaries

The architecture must allow automated verification of:

- Application import and startup
- API health response
- MCP tool discovery
- At least one genuine MCP tool call
- Policy retrieval and citation metadata
- Synthetic employee and PTO lookup
- Agent tool selection for representative tasks
- Confirmation before mock actions
- Missing data, missing evidence, and unavailable-tool behavior

## 12. Architecture Decisions Deferred Until Testing

The following choices remain deliberately open:

- Exact pinned package versions
- Exact OpenRouter chat model
- Retrieval `k`
- Chunk size and overlap
- Whether to commit the completed Chroma index or rebuild it during deployment
- Detailed API request and response schemas
- Detailed MCP tool input and output schemas
- Final Render start command and persistence behavior
- Whether an optional `draft_hr_email` MCP tool adds enough value to include

These decisions will be made one at a time using implementation evidence and evaluation results.
