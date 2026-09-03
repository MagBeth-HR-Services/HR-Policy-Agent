# Horizon HR Policy Agent — Project Requirements Checklist

This checklist translates the project brief into verifiable requirements.

- `[x]` means implemented and verified.
- `[ ]` means incomplete, unverified, or still pending.
- Items should be checked only when supported by code, tests, documentation, evaluation results, or deployed behavior.

## 1. Project Scope

- [x] Build an agentic AI system for HR policy and operations tasks.
- [x] Combine policy RAG with agent workflows over synthetic structured data.
- [x] Select two multi-step agentic workflows for the deployed demonstration.
- [x] Ensure the complete system runs locally for development.
- [ ] Verify the complete deployed architecture works within modest free-tier resources.

## 2. Environment and Reproducibility

- [x] Create and document a Python virtual environment.
- [x] List all dependencies in `requirements.txt`.
- [x] Provide setup and local-run instructions in `README.md`.
- [x] Use deterministic chunking where applicable.
- [x] Read API keys and other secrets from environment variables.
- [x] Provide a safe `.env.example` without real secret values.
- [x] Exclude real secrets and local environment files from Git.

## 3. Policy Corpus

- [x] Create 5–20 coherent company policy and procedure documents.
- [x] Verify and document that the corpus totals approximately 30–120 pages.
- [x] Cover PTO, holidays, remote work, expenses, security, benefits, onboarding, equipment, leave, and conduct.
- [x] Support at least two source formats.
- [x] Ensure the repository contains no private, paid, or improperly licensed material.

## 4. Mock Structured HR Data

- [x] Create clearly synthetic employee and HR records.
- [x] Include employee profiles and manager relationships.
- [x] Include PTO balances, benefits information, work locations, employment types, and ticket records.
- [x] Store the synthetic source data under `mock_data/`.
- [x] Document the synthetic data schema.

## 5. Policy Ingestion and Indexing

- [x] Parse and clean Markdown policy documents.
- [x] Parse and clean PDF policy documents.
- [x] Implement a heading-aware and recursive chunking strategy.
- [x] Use deterministic chunk identifiers and metadata.
- [x] Generate embeddings using a free local embedding model.
- [x] Store embedded chunks in Chroma.
- [x] Persist citation metadata including document ID, title, section, page number, filename, and snippet.
- [x] Make the index reproducible locally.
- [ ] Verify that the index rebuild works within the deployed environment.

## 6. Retrieval-Augmented Generation

- [x] Implement configurable top-k policy retrieval.
- [x] Add optional document filtering and result diversification.
- [x] Supply retrieved text and metadata to the agent through the MCP tool result.
- [x] Generate policy answers containing identifiable policy citations.
- [x] Return citation-ready snippets through policy retrieval.
- [x] Instruct the agent to redirect unsupported or incomplete policy questions.
- [x] Separate policy facts from approvals and recommendations.
- [x] Limit unsupported claims through grounding rules and evaluation.
- [ ] Verify and evaluate at least one answer requiring evidence from multiple policy documents.

## 7. Agent Orchestration

- [x] Interpret user intent through the LangGraph agent.
- [x] Select and call MCP-exposed tools.
- [x] Combine structured tool results and policy evidence into grounded responses.
- [x] Continue the model-tools-model loop until a final response is available.
- [x] Avoid exposing hidden chain-of-thought.
- [x] Verify both selected multi-step demonstration workflows end-to-end.
- [x] Produce a concise user-visible operational trace containing selected tools, arguments, outputs, sources, response basis, and escalation decisions.

## 8. MCP Servers and Tools

- [x] Implement genuine MCP servers.
- [x] Use the MCP-compatible `stdio` transport.
- [x] Implement a multi-server MCP client.
- [x] Expose at least five operational MCP tools.
- [x] Expose policy and HR server health-check tools.
- [x] Include an MCP tool that retrieves from the RAG index.
- [x] Include MCP tools that read synthetic structured data.
- [x] Include a mock HR-ticket operation.
- [x] Ensure the agent discovers and calls tools through MCP.
- [x] Document the MCP architecture, transport, tools, discovery, and invocation.
- [x] Store the MCP server code under `mcp_servers/`.

## 9. Safety and Failure Handling

- [x] Handle missing employee IDs gracefully.
- [x] Handle invalid employee IDs before the LLM can reinterpret them.
- [x] Validate employee IDs again at the MCP boundary.
- [x] Handle unknown employee records safely.
- [x] Prevent unsupported speculation when records are missing.
- [x] Ask for required information when a request is incomplete.
- [x] Make ticket creation a mock operation.
- [x] Require explicit confirmation before mock ticket creation.
- [x] Prevent the agent from claiming to approve HR requests.
- [x] Include escalation behavior for sensitive or unsupported cases.
- [x] Hide unexpected internal error details.
- [x] Add and verify graceful behavior when an MCP server is unavailable.
- [x] Expand testing for materially ambiguous requests.

## 10. Web Application

- [x] Provide a browser-based HR chat interface.
- [x] Provide a documented `POST /api/chat` endpoint.
- [x] Provide a `GET /health` endpoint.
- [x] Maintain conversation state using session IDs.
- [x] Display the final agent response.
- [x] Display citations when included in the agent’s answer.
- [x] Return structured citations and snippets separately from the answer.
- [x] Return and display a concise MCP tool-call trace.
- [x] Include MCP connectivity status in the health response where feasible.
- [x] Verify both demonstration workflows through the final deployed interface.

## 11. Automated Testing

- [x] Add unit, smoke, and application tests appropriate to the system.
- [x] Add an automated test confirming the application can start or import.
- [x] Add scripts confirming MCP tool discovery and MCP tool calls.
- [x] Test policy loading and citation metadata.
- [x] Test deterministic chunking.
- [x] Test core retrieval behavior.
- [x] Test database creation and HR services.
- [x] Test employee-ID and confirmation safety behavior.
- [x] Test FastAPI endpoints.
- [x] Maintain a passing automated test suite.

## 12. CI/CD

- [x] Create a GitHub Actions CI workflow.
- [x] Run the workflow on pushes to `main`.
- [x] Run the workflow on pull requests targeting `main`.
- [x] Install dependencies in the workflow.
- [x] Run a dependency compatibility check.
- [x] Run an application import check.
- [x] Run automated tests in the workflow.
- [x] Verify the workflow passes on a clean Linux runner.
- [x] Run an MCP tool-discovery or MCP tool-call check inside GitHub Actions.
- [x] Ensure deployment occurs only after CI passes.

## 13. Deployment

- [x] Deploy the application to Render or an equivalent host.
- [x] Provide a shareable deployed application URL.
- [x] Configure deployed secrets using environment variables.
- [x] Build Chroma during deployment.
- [x] Seed SQLite during deployment.
- [x] Avoid requiring a paid database.
- [x] Verify both agentic workflows in the deployed application.
- [x] Document expected free-tier cold-start behavior.
- [x] Record the deployed application and health URLs in `deployed.md`.

## 14. Evaluation Dataset

- [x] Expand the evaluation dataset to 20–30 questions or tasks.
- [x] Include straightforward policy questions.
- [x] Include questions requiring evidence from multiple policy documents.
- [x] Include employee-data tool questions.
- [x] Include combined policy and employee-data workflows.
- [x] Include incomplete requests requiring clarification.
- [x] Include invalid and unknown employee cases.
- [x] Include confirmation-safety cases.
- [x] Add explicit out-of-scope requests.
- [x] Provide semantic scoring criteria for each current case.
- [x] Provide a gold / expected answer for each evaluation case.
- [x] Store cases, scripts, and results under `evaluation/`.

## 15. Evaluation Results

## 15. Evaluation Results

- [x] Implement deterministic tool-selection checks.
- [x] Implement deterministic policy-citation checks.
- [x] Implement explicit forbidden-phrase safety checks.
- [x] Implement an LLM judge for semantic correctness.
- [x] Evaluate factual correctness.
- [x] Evaluate groundedness.
- [x] Evaluate safety.
- [x] Preserve tool evidence in evaluation results.
- [x] Produce a passing 24-case final evaluation: 24/24.
- [x] Report groundedness as a final aggregate metric: 100%.
- [x] Report citation accuracy as a final aggregate metric: 100%.
- [x] Report tool-selection accuracy as a final aggregate metric: 100%.
- [x] Report workflow-completion rate: 100%.
- [x] Report escalation or clarification accuracy: 100%.
- [x] Report action-safety pass rate: 100%.
- [x] Report warm latency: p50 18.55 seconds and p95 34.92 seconds.
- [x] Report deployed cold-start latency: 17.65 seconds.
- [x] Run and report a no-policy-search ablation: 18/24, or 75%.

## 16. Design Documentation

- [x] Create `design-and-evaluation.md`.
- [x] Maintain an up-to-date `ARCHITECTURE.md`.
- [x] Document the current web app, agent, MCP client, MCP servers, Chroma index, SQLite data, and LLM provider.
- [x] Include a text-based architecture diagram.
- [x] Document the embedding model and chunking strategy.
- [x] Document current retrieval behavior.
- [x] Document current MCP transport and tools.
- [x] Document current safety layers.
- [x] Document current limitations and pending work.
- [ ] Add final deployment architecture and verified deployment behavior.
- [ ] Add final evaluation questions, results, metrics, and comparison.
- [ ] Document both final demonstration workflows and their observed tool sequences.

## 17. General Documentation

- [x] Update `README.md` with an introduction and project overview.
- [x] Document local setup and execution.
- [x] Document local indexing and database creation.
- [x] Document automated testing.
- [x] Document evaluation commands.
- [x] Document CI behavior.
- [x] Document contributor setup and branch workflow.
- [x] Add final deployment instructions to `README.md`.
- [x] Create `ai-tooling.md`.
- [x] Explain what AI assistance worked well and what did not.
- [x] Create `deployed.md`.
- [x] Keep all current source code in the repository.

## 18. Demonstration Video

- [ ] Record a 7–10 minute screen-share demonstration with voiceover.
- [ ] Ensure every group member speaks and appears as required.
- [ ] Ensure every group member shows government ID as required.
- [ ] Demonstrate two agentic tasks end-to-end.
- [ ] Explain MCP tool names, arguments, outputs, citations, and final behavior for each task.
- [ ] Briefly explain system design and architecture.
- [ ] Briefly show deployment and CI/CD.
- [ ] Briefly present evaluation results.
- [ ] Produce a shareable presentation link.

## 19. Final Repository Audit

- [ ] Verify the repository contains no API keys, credentials, private data, or unnecessary environment files.
- [ ] Verify a new contributor can follow the README and run the application.
- [x] Verify CI passes from a clean checkout.
- [x] Verify all required files and folders are present.
- [x] Verify citations, snippets, and tool traces are readable in the deployed UI.
- [ ] Verify both demonstration workflows immediately before recording.
- [ ] Review this entire checklist against the final implementation.

## 20. Submission

- [ ] Share the GitHub repository with the `quantic-grader` account.
- [ ] Add the deployed application URL to `README.md`.
- [x] Create the GitHub repository.
- [ ] Prepare the final GitHub repository link for submission.
- [ ] Prepare the recorded presentation link.
- [ ] Complete and sign the group agreement if submitting as a group.
- [ ] Ensure only one group member submits.
- [ ] Submit both required links through the course dashboard.