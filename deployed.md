# Deployed application

The Horizon HR Policy Agent is deployed on Render.

Intended deployment (do not change the architecture):

- Host: Render web service
- Compute: Standard (`1c-2g`, 2 GB RAM), not Free or Starter
- Layout: one service running FastAPI, the LangGraph agent, two FastMCP `stdio` processes, Chroma, and SQLite
- Python: 3.14 via `.python-version` / `PYTHON_VERSION=3.14.3`

## URLs

| Item | Value |
| --- | --- |
| Application | https://horizon-hr-policy-agent.onrender.com/ |
| Health | https://horizon-hr-policy-agent.onrender.com/health |
| Chat API | `POST /api/chat` |

## Build and start

Build:

```text
pip install -r requirements.txt && python -m ingestion.build_index --recreate && python -m database.seed
```

Start:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

`render.yaml` in the repository root encodes these commands. Auto-deploy is off so a deploy happens only after GitHub Actions is green.

## Environment variables

Set in the Render dashboard. Do not commit secrets.

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `CHROMA_PATH=./data/chroma`
- `HR_DATABASE_PATH=./data/hr_data.db`
- `PYTHON_VERSION=3.14.3`

## Cold start

Paid Standard instances do not spin down the way Render Free does.

Measured first-chat latency after the live deploy: **17.65 seconds** (`What is PTO?`). Most of that wait is MiniLM loading inside the policy MCP process on the first request after a deploy.

If the service is ever moved to Free, document spin-down (often about one minute) here.

## Notes

SQLite and Chroma are rebuilt on each deploy. Mock tickets created in the live app do not survive a rebuild.
