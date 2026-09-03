# AI tooling

AI coding tools are allowed for this assignment. This file describes how they were used on the Horizon HR Policy Agent.

## Tools used

- **Cursor** (Agent) for local setup, requirement mapping against the Quantic brief, implementation of traces/citations/health, tests, evaluation-case expansion, and draft documentation.
- **OpenRouter-hosted models** at runtime for the LangGraph agent and the evaluation judge (configured through `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`).
- **Local `sentence-transformers/all-MiniLM-L6-v2`** for embeddings. This is not a code-generation tool; it is the retrieval embedder.

## What worked well

- Cursor mapped the official brief onto the existing checklist and caught gaps the checklist had marked done too early (no retrieval tests, `/api/chat` missing citations and traces, eval set of 10 without gold answers).
- Generating FastAPI response models, pytest cases, and evaluation JSON from the existing code style was faster than writing those files by hand.
- Reusing `evaluation/run_evaluation.py` patterns (`collect_tool_names`, MCP tool evidence) for the web API avoided a second, incompatible trace format.

## What did not work well, or needed human checks

- Opening a different project folder started a new Cursor chat, so setup context had to be reconstructed.
- PowerShell treats `.\.venv\Scripts\activate python -m uvicorn ...` as one command; `-m` was parsed as an Activate.ps1 parameter. That was a human environment issue, not a model issue.
- Local `sentence-transformers` + PyTorch is too large for Render Free (512 MB). The architecture stayed single-service; instance size is the change, not the design.
- The assistant cannot record the 7–10 minute video, show government ID, or invite `quantic-grader`.

## What we still verified by hand

- Local app start and `/health`
- Chat UI in the browser
- Render Standard deploy, live `/health`, and both demonstration workflows
- That `.env` is gitignored
- That employee IDs in mock data are fictional

## Responsibility

Group members remain responsible for correctness, secrets, academic integrity, and the demo. AI-generated code was reviewed in this repository before it was relied on for grading.
