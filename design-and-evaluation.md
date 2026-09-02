# Design and evaluation

Horizon HR Policy Agent — architecture, RAG, MCP, safety, demo workflows, and evaluation design for the Quantic *AI Engineering Techniques and Architectures* project.

## 1. Problem and approach

The system answers fictional Horizon Technologies HR questions. It retrieves policy evidence (RAG), looks up synthetic employee records through MCP tools, and refuses to approve real HR actions.

Orchestration is a LangGraph tool-calling loop, not a hand-written multi-agent graph. That matches the assignment: interpret intent, select tools, call MCP servers, synthesize a grounded answer.

## 2. Architecture

```text
User browser
     |
     v
FastAPI  GET /   POST /api/chat   GET /health
     |
     v
LangGraph agent --------------------------> OpenRouter LLM
     |
     v
MultiServerMCPClient (stdio)
     |
     +---- Policy FastMCP server --> Chroma (MiniLM embeddings)
     |
     +---- HR FastMCP server -------> SQLite (synthetic HR data)
```

Single-service deployment is the layout recommended in the brief. Components stay in one Render web service so MCP `stdio` child processes work without a second host or a paid database.

## 3. Policy corpus and RAG

- 11 original fictional policies (9 Markdown, 2 PDF)
- Verified size about **46 pages** (18 PDF pages + ~28 Markdown page-equivalents at 300 words/page), inside 30–120
- Heading-aware Markdown split plus recursive character split (size 1000, overlap 150)
- Embeddings: local `sentence-transformers/all-MiniLM-L6-v2` on CPU
- Store: persistent Chroma collection `horizon_policies`
- Retrieval: default `k=5`, optional `document_id` filter, optional diversify (max two chunks per document)
- Citations include document ID, title, section, page number, source file, and snippet

## 4. MCP servers and tools

Transport: **stdio**. Two FastMCP processes. The LangChain `MultiServerMCPClient` prefixes tool names with the server name.

| Prefixed tool | Server | Role |
| --- | --- | --- |
| `policy_health_check` | Policy | Connectivity |
| `policy_search_policies` | Policy | RAG over Chroma |
| `hr_health_check` | HR | Connectivity |
| `hr_get_employee_summary` | HR | Mock employee profile |
| `hr_get_pto_balance` | HR | Mock PTO |
| `hr_get_benefits_status` | HR | Mock benefits |
| `hr_create_hr_ticket` | HR | Mock ticket after confirmation |

The brief’s names (`search_policy_documents`, `check_pto_balance`, …) are examples. The agent discovers these tools through MCP; it does not import the HR functions directly.

## 5. Agent orchestration and traces

`agent/graph.py` is a `StateGraph`: model node, `ToolNode`, loop until there are no tool calls. Invalid employee IDs (`1002` instead of `E1002`) are rejected **before** the LLM.

`POST /api/chat` returns:

- `answer`
- `citations` (from `policy_search_policies` results)
- `tool_trace` (tool name, arguments, short output)

The UI shows those fields. That is the operational trace required by the brief. Hidden chain-of-thought is not shown.

If the agent was not created, chat returns a safe MCP-unavailable message instead of a stack trace.

`GET /health` includes `mcp.policy` and `mcp.hr` (`connected`, `not_connected`, or `unavailable`).

## 6. Safety

- Synthetic data only
- Employee IDs must match `E####`
- MCP HR tools validate IDs again
- Missing records: report not found, do not invent
- No approval of PTO, travel, expenses, or similar
- `hr_create_hr_ticket` requires `confirmed_by_user`
- Unexpected errors become a generic user message

## 7. Demo workflows and expected MCP sequences

### Task 1 — PTO guidance

Prompt: `I am employee E1001. Can I take three PTO days next week?`

Expected tools (order may vary):

1. `hr_get_employee_summary` and/or `hr_get_pto_balance` (56 available hours)
2. `policy_search_policies` → POL-001
3. Explain notice/manager approval; do not approve
4. `hr_create_hr_ticket` only after explicit confirmation

### Task 2 — International temporary work

Prompt: `I am employee E1002. Can I work from another country for six weeks?`

Expected tools:

1. `hr_get_employee_summary` (remote, Austin, TX)
2. `policy_search_policies` → POL-004; often POL-003 / POL-005 as well
3. Explain the 20-business-day limit and multi-department review; do not approve
4. Mock ticket only after confirmation

## 8. Web application

- Framework: FastAPI + Jinja chat page
- Chat: `POST /api/chat` (equivalent to `/chat` in the brief)
- Health: `GET /health`
- Sessions: in-memory `session_id`

## 9. Deployment choices

- Target: Render Standard 2 GB, one web service
- Why not Free/Starter: PyTorch + MiniLM + three Python processes exceed 512 MB
- No paid database: Chroma and SQLite are built in the Render build command
- Auto-deploy is off in `render.yaml` so a deploy follows a green GitHub Actions run
- Secrets: environment variables only

See `deployed.md` for the live URL once it exists.

## 10. Evaluation

Dataset: `evaluation/cases.json` — **24** cases with gold answers.

| Category | What it covers |
| --- | --- |
| `policy_rag` | Straightforward policy Q&A |
| `multi_document` | POL-004 + POL-005 in one question |
| `employee_data` | PTO and benefits tools |
| `combined_workflow` | Demo-style policy + employee tools |
| `missing_information` | Clarification |
| `invalid_employee` / `unknown_employee` | Safety |
| `confirmation_safety` | Ticket gate, including a follow-up confirmation |
| `out_of_scope` | Payroll, medical advice, sending email |

Runner: `python -m evaluation.run_evaluation`

Checks:

- Deterministic tool selection and policy-ID citation
- Forbidden-phrase safety
- LLM judge: factual, grounded, safe, criteria met (compared with gold answers)
- Warm latency per case; summary p50/p95
- Aggregates: groundedness, citation accuracy, tool-selection accuracy, workflow completion, clarification/escalation accuracy, action-safety pass rate

Ablation:

```text
python -m evaluation.run_evaluation --ablation no-policy-search
```

This disables `policy_search_policies`. Groundedness and citation accuracy should drop versus the full agent. Results go to `evaluation/results_ablation_no_policy_search.json`.

### Results

The final local evaluation was run on September 1, 2026, using `google/gemini-3-flash-preview`.

| Metric | Full agent | No policy search |
| --- | ---: | ---: |
| Cases passed | 24/24 | 18/24 |
| Pass rate | 100% | 75% |
| Groundedness | 100% | 83.33% |
| Citation accuracy | 100% | 83.33% |
| Tool-selection accuracy | 100% | 100% |
| Workflow-completion rate | 100% | 80% |
| Escalation or clarification accuracy | 100% | 100% |
| Action-safety pass rate | 100% | 100% |
| Warm latency p50 | 18.55 seconds | 9.57 seconds |
| Warm latency p95 | 34.92 seconds | 35.05 seconds |
| Mean warm latency | 17.56 seconds | 13.95 seconds |

The no-policy-search ablation reduced the pass rate by 25 percentage points. Groundedness and citation accuracy each fell by 16.67 percentage points, demonstrating that RAG materially improves policy-specific answers. Safety remained at 100%, showing that the deterministic and prompt-based safeguards continued to operate without policy retrieval.

The detailed full-agent results are stored in `evaluation/results.json`. The ablation results are stored in `evaluation/results_ablation_no_policy_search.json`.

Cold-start latency will be measured on the deployed URL and is not included in these local results.

## 11. CI

GitHub Actions on push/PR to `main`: install, `pip check`, import `app.main`, pytest. Pytest includes MCP tool registration and an HR MCP stdio list+call test.
