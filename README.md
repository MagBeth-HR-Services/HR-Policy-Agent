# HR Policy Agent

An agentic HR assistant for the fictional company Horizon Technologies.

The application will combine:

- Retrieval-Augmented Generation (RAG) over company policy documents
- LangGraph agent orchestration
- MCP-exposed tools
- Synthetic employee and HR data
- Grounded answers with citations and operational tool traces

## Current Status

Initial project setup is in progress. The application is not yet runnable.

## Requirements

- Python 3.14.4
- Git
- An OpenRouter API key

## Local Setup

Create a virtual environment:

```cmd
py -m venv .venv
```

Activate it in Command Prompt:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```cmd
python -m pip install -r requirements.txt
```

Create `.env` in the project root using `.env.example` as the template.

Replace the placeholder API key with your private OpenRouter API key. Never commit `.env` or any API key to Git.

## Documentation

- `PROJECT_CHECKLIST.md` - Assignment requirements
- `PROJECT_SCOPE.md` - Selected workflows and project boundaries
- `ARCHITECTURE.md` - Planned system architecture