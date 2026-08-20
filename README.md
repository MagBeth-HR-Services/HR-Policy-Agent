# Horizon HR Policy Agent

[![Continuous Integration](https://github.com/mcutler1973-hue/HR-Policy-Agent/actions/workflows/ci.yml/badge.svg)](https://github.com/mcutler1973-hue/HR-Policy-Agent/actions/workflows/ci.yml)

An agentic HR assistant for the fictional company Horizon Technologies.

The application combines Retrieval-Augmented Generation (RAG), LangGraph agent orchestration, MCP tools, synthetic HR data, and a FastAPI web interface. It answers policy questions, retrieves employee information, and supports safe mock HR workflows using grounded company evidence.

> This project uses entirely fictional policies and employee data. It is an educational project and is not intended to provide real HR, legal, tax, immigration, medical, or financial advice.

## Project Status

The application currently runs locally and includes:

- A corpus of 11 fictional HR policy documents
- Markdown and PDF policy loading
- Deterministic policy chunking
- Local sentence-transformer embeddings
- A persistent Chroma vector index
- SQLite employee, PTO, benefits, and ticket data
- Two FastMCP servers using `stdio`
- Seven MCP tools available to the agent
- A LangGraph tool-calling agent
- Employee-ID and confirmation safety controls
- A FastAPI chat interface
- Unit and smoke tests
- A hybrid deterministic and LLM-based evaluation runner
- GitHub Actions continuous integration

Deployment and final project documentation are still in progress.

## Main Technologies

- Python 3.14
- FastAPI and Uvicorn
- LangChain and LangGraph
- Model Context Protocol and FastMCP
- OpenRouter
- Chroma
- Sentence Transformers
- SQLite
- Pytest
- GitHub Actions

## Architecture

```text
Browser
   |
FastAPI web application
   |
LangGraph agent
   |
Multi-server MCP client
   |
   +-- Policy MCP server
   |      |
   |      +-- RAG retrieval
   |             |
   |             +-- Chroma vector index
   |                    |
   |                    +-- Fictional policy documents
   |
   +-- HR MCP server
          |
          +-- SQLite database
                 |
                 +-- Synthetic HR data

LangGraph agent ---> OpenRouter LLM
```

Additional architecture details are available in `ARCHITECTURE.md`.

## Project Structure

```text
agent/             LangGraph agent, model configuration, prompts, and safety
app/               FastAPI application and browser interface
database/          SQLite connection, schema, seeding, and HR services
evaluation/        Evaluation cases, runner, and results
ingestion/         Policy loading, chunking, embedding, and indexing
mcp_servers/       Policy and HR FastMCP servers
mock_data/         Synthetic employee, PTO, benefits, and ticket data
policies/          Fictional HR policy documents
rag/               Policy retrieval and command-line search
scripts/           Manual MCP and agent verification scripts
tests/             Automated tests
.github/workflows/ GitHub Actions CI workflow
```

The `data/` directory is generated locally and is not committed to Git.

## Requirements

- Python 3.14
- Git
- An OpenRouter account and API key

## Local Setup

### 1. Clone the repository

```cmd
git clone https://github.com/mcutler1973-hue/HR-Policy-Agent.git
cd HR-Policy-Agent
```

### 2. Create a virtual environment

On Windows Command Prompt:

```cmd
py -m venv .venv
.venv\Scripts\activate
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```cmd
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to a new file named `.env`.

On Windows Command Prompt:

```cmd
copy .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your own OpenRouter API key.

```text
OPENROUTER_API_KEY=your-private-key
OPENROUTER_MODEL=poolside/laguna-xs-2.1:free
CHROMA_PATH=./data/chroma
HR_DATABASE_PATH=./data/hr_data.db
```

Never commit `.env` or share an API key.

Free OpenRouter models can change availability and have request limits. Another tool-capable OpenRouter model may be used by changing `OPENROUTER_MODEL`.

### 5. Build the policy vector index

```cmd
python -m ingestion.build_index --recreate
```

This command:

1. Loads the Markdown and PDF policies.
2. Divides them into deterministic chunks.
3. Generates embeddings.
4. Stores the embedded chunks in Chroma.

The first run downloads the local embedding model and may take longer.

### 6. Create and seed the SQLite database

```cmd
python -m database.seed
```

This creates `data/hr_data.db` and imports the synthetic records from `mock_data/`.

## Run the Web Application

Start the FastAPI server:

```cmd
python -m uvicorn app.main:app --reload
```

Open the chat interface:

```text
http://127.0.0.1:8000
```

Check application health:

```text
http://127.0.0.1:8000/health
```

Interactive FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Stop the server with `Ctrl+C`.

## Example Questions

General policy question:

```text
What is Horizon's general paid time off policy?
```

Employee-data question:

```text
How much PTO does employee E1002 have?
```

Combined policy and employee workflow:

```text
I am employee E1002. Can I work from another country for six weeks?
```

Benefits question:

```text
What is the benefits status for employee E1002?
```

The project uses fictional employee IDs in the format `E####`.

## MCP Tools

The agent discovers tools from two FastMCP servers.

### Policy MCP server

- `policy_health_check`
- `policy_search_policies`

### HR MCP server

- `hr_health_check`
- `hr_get_employee_summary`
- `hr_get_pto_balance`
- `hr_get_benefits_status`
- `hr_create_hr_ticket`

The MCP servers use `stdio` transport and run as child processes of the application.

## Safety Controls

The application includes the following safeguards:

- Employee IDs must use the `E####` format.
- Invalid IDs are rejected before the LLM can reinterpret them.
- Employee-specific tools retrieve only the information needed.
- Missing records must be reported without speculation.
- The agent cannot approve HR requests.
- Mock HR ticket creation requires explicit confirmation.
- Unexpected internal error details are hidden from users.
- Policy answers must use retrieved company evidence.

All employee data and ticket operations are fictional.

## Run Automated Tests

Run the complete test suite:

```cmd
python -m pytest -v
```

The repository currently contains 40 passing automated tests covering:

- Policy loading
- Chunking
- Retrieval
- SQLite services
- MCP-related behavior
- Agent routing
- Safety controls
- FastAPI startup and endpoints

## Run the Evaluation

Run all current evaluation cases:

```cmd
python -m evaluation.run_evaluation
```

Run one selected case:

```cmd
python -m evaluation.run_evaluation --case-id EVAL-001
```

The evaluator combines:

- Deterministic tool-selection checks
- Required policy citation checks
- Explicit forbidden-phrase safety checks
- An LLM judge for factual correctness, grounding, safety, and semantic criteria

The current 10-case baseline passes all cases. The evaluation set will be expanded to the assignment-required 20–30 cases, with latency metrics and an ablation comparison added before submission.

The evaluation uses additional OpenRouter requests because both the agent and the judge call an LLM.

## Manual Diagnostic Commands

Test policy retrieval:

```cmd
python -m rag.search "Can an employee work from another country for six weeks?"
```

Test agent MCP tool discovery:

```cmd
python -m scripts.check_agent_tools
```

Test the policy MCP server:

```cmd
python -m scripts.check_policy_mcp
```

Test the HR MCP server:

```cmd
python -m scripts.check_hr_mcp
```

Run the command-line chat agent:

```cmd
python -m scripts.check_chat_agent
```

## Continuous Integration

GitHub Actions runs automatically on:

- Pushes to `main`
- Pull requests targeting `main`

The workflow:

1. Creates a clean Linux runner.
2. Installs Python and project dependencies.
3. Checks installed dependency compatibility.
4. Verifies that the FastAPI application imports.
5. Runs the automated tests.

A failed workflow is reported in the repository's Actions tab.

## Collaboration

Contributors should create a separate branch:

```cmd
git switch -c feature/short-description
```

After making and testing one logical change:

```cmd
git add .
git commit -m "Describe the change"
git push -u origin feature/short-description
```

Open a pull request on GitHub and wait for the CI workflow to pass before merging.

Each contributor must create their own `.env` and use their own API key.

## Generated and Private Files

The following are intentionally excluded from Git:

- `.env`
- `.venv/`
- `data/chroma/`
- `data/*.db`
- Python and test cache files

Chroma and SQLite are recreated from the committed fictional source data.

## Deployment

Deployment to Render is planned but not yet complete.

The deployed application URL, health endpoint, build instructions, and expected free-tier cold-start behavior will be added after deployment.

## Project Documentation

- `PROJECT_SCOPE.md` — project workflows and boundaries
- `ARCHITECTURE.md` — system architecture
- `PROJECT_CHECKLIST.md` — assignment requirements
- `evaluation/` — evaluation cases, runner, and results
- `mock_data/DATA_SCHEMA.md` — synthetic data schema

The following final submission documents are still being prepared:

- `design-and-evaluation.md`
- `ai-tooling.md`
- `deployed.md`

## License and Data Notice

The policy corpus and HR records were created as fictional training data for this educational project. They do not describe real people or a real company.