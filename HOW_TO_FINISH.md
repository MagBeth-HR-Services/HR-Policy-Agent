# How to Finish the Horizon HR Policy Agent

## Status after the 28 August 2026 implementation pass

Done in the repository (still needs your Render click, a 24-case OpenRouter eval run, and the video):

- `/api/chat` returns `answer`, `citations`, `snippets` (on each citation), and `tool_trace`
- Chat UI shows citations and the tool trace; header shows `/health` MCP status
- Graceful chat message when the agent/MCP stack is not started
- Retrieval tests, MCP registration tests, HR MCP stdio list+call test (runs in GitHub Actions via pytest)
- 24 evaluation cases with gold answers, including multi-document and out-of-scope
- Runner aggregates, latency, and `--ablation no-policy-search`
- Corpus size documented at about 46 pages
- `render.yaml`, `.python-version`, `design-and-evaluation.md`, `ai-tooling.md`, `deployed.md`

Not done (people / live services):

- Create the Render Standard service and paste `OPENROUTER_API_KEY`
- Re-run `python -m evaluation.run_evaluation` and the ablation; paste metrics into `design-and-evaluation.md`
- Confirm both demo prompts on the live URL
- Video, IDs, `quantic-grader`, one submitter

The rest of this file is the original plan mapped to the official brief.

---

This guide maps the official Quantic brief (*AI Engineering Techniques and Architectures*, including the 0–5 rubric) onto the current repository. It replaces the earlier draft that was written before the official text was available.

Score **2+** is passing. The aim here is a **4–5**: a working deployed demo with visible MCP traces, a 20–30 case eval with gold answers and the named metrics, and the three required markdown files.

---

## 1. Where you already stand

The core system matches the **recommended single-service architecture** in the brief:

Web chat + `/api/chat` + agent orchestrator + MCP client + two local MCP servers over `stdio` + Chroma + SQLite mock data + OpenRouter via env vars.

That is exactly what Quantic drew as the free-tier-compatible layout. You do **not** need a second MCP host or a paid database.

Also already in place:

- 11 fictional policies, Markdown + PDF, topics the brief lists
- 12 synthetic employees, PTO, benefits, tickets, managers
- Seven MCP tools (five operational + two health). The brief’s names (`search_policy_documents`, `check_pto_balance`, …) are **examples**; prefixed FastMCP names are fine
- Two demo workflows chosen: PTO guidance (E1001) and international temporary work (E1002)
- LangGraph agent that discovers tools through MCP (not hard-coded function calls)
- Safety: invalid IDs, confirmation before mock tickets, no approvals
- FastAPI chat UI, `/api/chat` (allowed as “or equivalent”), `/health`
- 40 pytest tests, GitHub Actions on push/PR to `main`
- 10 evaluation cases, all passing, with per-case judge fields
- `ARCHITECTURE.md`, `README.md` local setup, `mcp_servers/` (allowed as “mcp/ or equivalent”), `mock_data/`, `evaluation/`

### Weak or false checklist marks

| Item | Honest status |
| --- | --- |
| Retrieval tests | **Missing.** No test calls `search_policy_documents()`. Unchecked. |
| Two workflows “for the deployed demo” | **Selected**, not proven on a live URL. |
| Escalation | Prompt/policy text only. |
| MCP scripts | Exist under `scripts/`. **CI does not run them.** The brief wants a discovery or call check in the pipeline. |

---

## 2. Official brief vs the checklist

The checklist was already close. After reading the official text, these are the **real remaining gaps**. Extra checklist items (E#### format, Python 3.14, pip check) are stricter than the brief and can stay.

### Required by the brief, not done yet

| Brief requirement | Current repo | Rubric impact |
| --- | --- | --- |
| `/chat` (or equivalent) returns **answer, citations, snippets, and a concise tool-call trace** | `/api/chat` returns only `session_id` + `answer`. Citations live in prose. No snippets or trace fields. | Score 5: “clear tool-call traces.” Demo **must** narrate tool names, args, outputs, citations. Without UI/API traces you cannot show that. |
| `/health` includes app status **and, where feasible, MCP connectivity** | App status only. | Easy fix; graders hit this URL. |
| At least one **multi-document** policy question | No eval case requires two policy IDs. EVAL-010 sometimes cites two docs by luck. | Explicit in §3 RAG. |
| Eval set of **20–30** tasks with **gold / expected answers** | 10 cases with criteria, **no `gold_answer` field**. Missing out-of-scope and a dedicated multi-doc case. | §9 and `design-and-evaluation.md` both require expected answers. |
| Report **groundedness, citation accuracy, tool selection, workflow completion, escalation/clarification, action-safety, p50/p95 latency** | Per-case flags only; summary is `pass_rate`. No latency. | Named in learning outcomes and score 5. |
| At least one **ablation** (k, chunk size, prompt, or tool availability) | None. | §9. |
| Graceful **unavailable MCP** behavior | Not implemented or tested. | §4 failures. |
| Ambiguous requests need clarification | Missing-ID case exists; location/date ambiguity is thin. | §4 and §9. |
| Out-of-scope requests in the eval set | None. | §9. |
| CI includes **MCP discovery or a simple MCP tool call** | Scripts only, not in `.github/workflows/ci.yml`. | §8 and score 5. |
| **Deploy only if tests pass** | Render is not wired. GitHub push can deploy even if CI is red unless you gate it. | §8. |
| Shareable deployed URL; document **cold starts** | Not deployed. | §7; score 2 if the demo needs local-only. |
| `design-and-evaluation.md` with architecture **and** eval questions, expected answers, results | Missing. | Required repo file. |
| `ai-tooling.md` | Missing. | Required; AI use is allowed only if described. |
| `deployed.md` with URL, health URL, cold-start notes | Missing. | Required repo file. |
| README **deployment** instructions + deployed URL | Local setup only. | Submission guideline. |
| Corpus **documented** as 30–120 pages | Plan says ~43 pages; not verified in writing. | § corpus. |
| Demo: 7–10 min, all members on camera, **government ID**, two **deployed** tasks with MCP narration | Not recorded. | Hard fail on demo requirements even if code is good. |

### Required by the brief, already satisfied (or equivalent)

- venv, requirements, secrets in env, `.gitignore` for `.env`
- Two source formats, chunking, local embeddings, Chroma, citation metadata
- Top-k retrieval with optional document filter (rerank/query-rewrite are optional)
- Guardrails: out-of-corpus redirect in prompts, facts vs approval
- Agent plans, selects MCP tools, synthesizes
- ≥5 MCP tools; ≥1 RAG; ≥1 mock structured / mock operation
- Agent calls tools through MCP
- Architecture documented in `ARCHITECTURE.md`
- Mock data clearly synthetic
- No paid database
- App start/import test in CI
- Group size ≤3 (confirm with your partner)

### Optional in the brief (do not treat as missing)

- Separate MCP HTTP service
- Query rewriting / reranking
- Exact tool names like `draft_hr_email`
- Exact or partial string match vs gold (optional in addition to groundedness)
- Production-like multi-service deploy

---

## 3. Hosting: official language vs a reliable URL

The brief says deploy to a **free-tier** host, keep the corpus small, and that the project should be possible **without paid hosting**. Score 5 says “free-tier-compatible.” The recommended diagram is **one** web service — which you already have.

What other students hit is not “wrong host.” It is **512 MB RAM**. This app currently loads PyTorch + MiniLM inside the policy MCP process, plus uvicorn and the HR MCP process. That wants about **0.8–1.5 GB**. Render Free and Render Starter are both 512 MB, so they OOM. Then people hop to Railway, then back, and the architecture starts changing.

### Decision (matches your preference: pay a little, do not hop)

1. **Do not change the architecture.** Stay on the brief’s single Render (or Railway) web service: FastAPI + stdio MCP + Chroma + SQLite + OpenRouter.
2. **Do not add** paid Postgres, a second MCP service, or serverless functions.
3. **Deploy on Render Standard (2 GB, about $25/month, billed per second).** Same product family as Free. Paid instances do not spin down. After grading, suspend the service.
4. In `deployed.md` and `design-and-evaluation.md`, say this plainly: the **architecture is the recommended free-tier layout**; the **instance is paid** because local embeddings plus three Python processes exceed 512 MB. Graders need a URL that works. A crashed Free service scores worse (rubric 2: “local execution is required for substantial parts of the demo”).
5. Optional later, only if you want a true $0 URL as well: swap `sentence-transformers`/torch for a smaller ONNX embedder (`fastembed`) so Free *might* boot. That is a dependency change, not a host change. Do it after traces and eval work, not instead of them.

Do **not** switch to Railway mid-project unless Render is down. The brief lists Railway as an equivalent, not a requirement.

New Render services can use **Python 3.14**, which matches this repo. Set `PYTHON_VERSION=3.14.3`.

Cold starts: paid Standard stays up, so cold start is mostly **first request after deploy** (MCP + MiniLM load). Still time it and write the number in `deployed.md`. If you ever use Free, document spin-down (often ~1 minute).

---

## 4. Work order

Do not record the video until the **deployed** UI shows two full workflows, citations, snippets, and a tool trace.

| Phase | Work | Who |
| --- | --- | --- |
| **A** | `/api/chat` returns citations, snippets, tool_trace; UI displays them; `/health` reports MCP | Cursor |
| **B** | Retrieval tests; MCP-down test; MCP discovery in CI; optional CI deploy gate | Cursor |
| **C** | 20–30 cases with `gold_answer`; multi-doc; out-of-scope; aggregates; p50/p95; ablation | Cursor drafts; you spot-check answers |
| **D** | Write the corpus page count (~43 planned) | Cursor can count |
| **E** | `render.yaml` / README deploy; you create Render Standard and paste the OpenRouter key | Shared |
| **F** | `design-and-evaluation.md`, `ai-tooling.md`, `deployed.md`, README URL | Cursor drafts; you write honest tooling notes |
| **G** | Video, IDs, `quantic-grader`, one submitter, group agreement if a group | People only |

---

## 5. Phase A — `/api/chat` contract and demo traces

The brief’s web-app bullet is specific: the endpoint must return the **final answer, citations, snippets, and a concise tool-call trace**. The demo presenter must speak those same fields.

Today `ChatResponse` is `{ session_id, answer }`.

### Implement

1. Reuse `collect_tool_names` / `collect_tool_evidence` from `evaluation/run_evaluation.py`.
2. Parse policy-search JSON into structured citations (`document_id`, `title`, `section`, `page_number`, `source_file`, `snippet`).
3. Return something like:

```json
{
  "session_id": "...",
  "answer": "...",
  "citations": [{ "document_id": "POL-004", "title": "...", "section": "...", "snippet": "..." }],
  "tool_trace": [
    { "tool": "hr_get_employee_summary", "arguments": { "employee_id": "E1002" }, "output_summary": "..." }
  ]
}
```

No hidden chain-of-thought. Short operational rows only.

4. Show answer, citations/snippets, and the trace in `app/templates/index.html`.
5. `/health`: `{ "status": "healthy", "application": "...", "mcp": { "policy": "...", "hr": "..." } }` without crashing if a server is down.
6. Tests for the new JSON shape (fake agent still allowed).

### Local check (the two demo tasks)

1. `I am employee E1001. Can I take three PTO days next week?`  
   Expect: employee/PTO tools + `policy_search_policies`, citations, no approval, ask before a ticket.

2. `I am employee E1002. Can I work from another country for six weeks?`  
   Expect: profile + policy search (POL-004, often POL-003/POL-005), 20-business-day limit, multi-department review, no approval.

Keep `/api/chat` as the path. The brief allows “or equivalent.” Document it as the chat endpoint in README so the grader does not look only for `/chat`.

---

## 6. Phase B — Tests and CI (brief §8)

Add:

- `tests/test_retrieval.py` — a known query hits POL-004; filter and diversify behave.
- MCP unavailable — user sees a safe message, not a traceback.
- One CI step that **discovers tools or calls one tool**. Practical approach: a pytest that imports the FastMCP apps and asserts the seven tool names are registered, plus a short `stdio` smoke if it stays fast. Full `check_agent_tools.py` in CI will download MiniLM and may time out; prefer a lightweight discovery test in Actions and keep the live scripts for local/manual use.
- Deploy gate: either deploy from GitHub Actions only on green `main`, or turn **off** Render auto-deploy on every push and deploy manually after CI is green. The brief: “Deployment must only occur if tests pass.”

---

## 7. Phase C — Evaluation (brief §9)

Need **20–30** questions/tasks covering: straightforward policy Q&A, **multi-document**, tool-requiring, ambiguous, **out-of-scope**, plus the two agentic workflows — each with a **gold / expected answer**.

### Add `gold_answer` to every case

Short paragraph the judge (and the design doc) can compare against. Example for EVAL-002: `Employee E1002 has 120 available PTO hours.`

### New cases to add (on top of the existing 10)

| Type | Example |
| --- | --- |
| Multi-document (required) | Remote work abroad: security + temporary location (POL-003/POL-005 and POL-004) |
| Demo workflow 1 | E1001, three PTO days next week (balance + POL-001) |
| Out of scope | Payroll amount; medical diagnosis; “send an email to my manager”; visa/immigration advice |
| Ambiguous | “Can I work remotely from there?” with no location or ID |
| Confirmation follow-up | After explicit “yes, create the ticket” expect `hr_create_hr_ticket` |
| Broader corpus | One expenses, one equipment, one conduct question |

Target **24–28** cases so you are inside 20–30 with room to drop a flaky one.

### Aggregate metrics in `results.json`

From existing per-case flags, plus a timer:

- Groundedness rate  
- Citation accuracy  
- Tool-selection accuracy  
- Workflow-completion rate  
- Escalation / clarification accuracy  
- Action-safety pass rate  
- Warm latency **p50 and p95** on 10–20 cases  

Cold-start: one timed request to the **deployed** app after deploy (or after spin-down if on Free). Put that number in `deployed.md`.

### Ablation

Run a fixed subset twice, for example:

- Full tools vs **policy search disabled**, or  
- `k=3` vs `k=8`

Report groundedness and citation accuracy for both. A `--ablation` flag is enough; do not fork the app.

OpenRouter usage will rise (agent + judge + ablation). Use the existing key; watch rate limits on free models.

---

## 8. Phase D — Page count

Count PDF pages on POL-003 and POL-005 plus a Markdown page-equivalent (words/300 or print-to-PDF). Write the total in `POLICY_CORPUS_PLAN.md` and `design-and-evaluation.md`. Planned ~43 is already inside 30–120; you mainly need the written verification.

---

## 9. Phase E — Deploy

Build:

```text
pip install -r requirements.txt && python -m ingestion.build_index --recreate && python -m database.seed
```

Start:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Secrets on the host, never in git: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `CHROMA_PATH`, `HR_DATABASE_PATH`, `PYTHON_VERSION=3.14.3`.

Health path: `/health`.

Cursor can add `render.yaml`, `.python-version`, and README steps. You create the Render web service, pick **Standard 2 GB**, paste the key, and confirm `https://<service>.onrender.com/` plus `/health`.

SQLite + Chroma built at deploy = **no paid database** (brief §7).

---

## 10. Phase F — Required repository files

| File | Must contain (from the brief) |
| --- | --- |
| `README.md` | Intro, setup, **local run**, **deployment**, evaluation commands, **deployed URL** |
| `design-and-evaluation.md` | Architecture, RAG, MCP, orchestration, tool schemas, safety, deployment choices, **eval questions, expected answers, results** |
| `ai-tooling.md` | Which AI tools (Cursor, etc.), what worked, what did not |
| `deployed.md` | App URL, health URL, cold-start notes |
| `evaluation/` | Questions, gold answers/rubrics, scripts, reported results (exists; needs expansion) |
| `mock_data/` | Synthetic data (exists) |
| `mcp_servers/` | MCP code (exists; “or equivalent” to `mcp/`) |

---

## 11. Phase G — Demo and submit (people only)

- 7–10 minute screen-share with voiceover  
- Every group member on camera and speaking  
- Every group member shows government ID  
- **Deployed** app, two agentic tasks end-to-end  
- For **each** task: tool names, arguments, outputs, citations, final behavior  
- Short walkthrough: design, deployment, CI/CD, evaluation  
- Share GitHub with `quantic-grader`  
- One member submits both links  
- Group agreement last page if submitting as a group  
- Late submit is allowed; grading may be delayed  
- Questions: msaie+projects@quantic.edu  

Suggested demo order: architecture → CI green → live URL + health → E1001 PTO (trace on screen) → E1002 six weeks (trace on screen) → one failure path (bad ID or out of scope) → metrics from `design-and-evaluation.md`.

---

## 12. What Cursor can implement vs what you do

**I can implement in this repo as soon as you say to start:**

1. **Phase A (highest leverage)** — structured citations, snippets, tool trace in `/api/chat` and the UI; MCP fields on `/health`; tests for the new response shape  
2. Retrieval tests + MCP-unavailable handling  
3. A CI step that checks MCP tool discovery without a full MiniLM download if possible  
4. Expand `evaluation/cases.json` to 20–30 with `gold_answer`, multi-doc, out-of-scope; extend the runner for aggregates, latency, and one ablation flag  
5. Corpus page-count writeup  
6. `render.yaml`, `.python-version`, README deploy section  
7. Drafts of `design-and-evaluation.md`, `ai-tooling.md`, `deployed.md` (URLs filled after you deploy)  
8. Checklist updates as items land  

**I cannot do for you:**

- Create the Render account, pay, or paste production secrets  
- Click the first live deploy and keep the service funded  
- Appear on camera, show ID, or record the 7–10 minute video  
- Invite `quantic-grader` or submit on the dashboard  
- Sign the group agreement  
- Write the subjective “what AI got wrong” stories in `ai-tooling.md` (I can draft a skeleton from this project’s history; you must own it)

**Suggested next step:** Phase A only. That is the difference between a local chat demo and a gradeable deployed demo under the official `/chat` and video rules.
