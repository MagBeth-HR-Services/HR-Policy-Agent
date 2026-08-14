# HR Policy Agent - Project Requirements Checklist

This checklist translates the project brief into verifiable requirements. Check an item only after it has been implemented and tested.

## 1. Project Scope

- [ ] Build an agentic AI system for HR policy and operations tasks.
- [ ] Combine policy Retrieval-Augmented Generation (RAG) with agent workflows over synthetic structured data.
- [ ] Select two multi-step agentic workflows for the deployed demonstration.
- [ ] Ensure the complete system runs locally for development.
- [ ] Keep the architecture compatible with modest or free-tier resources.

## 2. Environment and Reproducibility

- [ ] Create and document a Python virtual environment.
- [ ] List all dependencies in `requirements.txt` or an equivalent dependency file.
- [ ] Provide setup and local-run instructions in `README.md`.
- [ ] Set fixed seeds where deterministic behavior is applicable.
- [ ] Read API keys and other secrets from environment variables.
- [ ] Provide a safe `.env.example` without real secret values.
- [ ] Exclude real secrets and local environment files from Git.

## 3. Policy Corpus

- [ ] Create or legally obtain 5-20 coherent company policy and procedure documents.
- [ ] Ensure the corpus totals approximately 30-120 pages.
- [ ] Cover several relevant topics, such as PTO, holidays, remote work, expenses, security, benefits, onboarding, equipment, leave, and conduct.
- [ ] Support at least two source formats where feasible, such as Markdown, HTML, PDF, or TXT.
- [ ] Ensure the repository contains no private, paid, or improperly licensed material.

## 4. Mock Structured HR Data

- [ ] Create clearly synthetic employee or HR records with no real personal information.
- [ ] Include employee profiles and manager relationships where needed by the workflows.
- [ ] Include PTO balances, benefits data, office locations, employment types, or ticket records as needed.
- [ ] Store the mock data under `mock_data/` or an equivalent documented folder.

## 5. Policy Ingestion and Indexing

- [ ] Parse and clean each supported document format.
- [ ] Implement and justify a chunking strategy.
- [ ] Use deterministic chunking where applicable.
- [ ] Generate embeddings using a local, free, or free-tier embedding model.
- [ ] Store embedded chunks in Chroma or another lightweight vector database.
- [ ] Persist metadata needed for citations, including document ID or title, section, and source snippet.
- [ ] Make the index reproducible locally and during deployment.

## 6. Retrieval-Augmented Generation

- [ ] Implement top-k policy retrieval.
- [ ] Add optional filtering, query rewriting, or reranking if useful.
- [ ] Inject retrieved text and source metadata into the LLM prompt.
- [ ] Generate answers containing identifiable policy citations.
- [ ] Include supporting snippets where appropriate.
- [ ] Refuse or redirect policy questions unsupported by the corpus.
- [ ] Clearly separate policy facts from suggestions or recommendations.
- [ ] Limit unsupported claims.
- [ ] Successfully answer at least one question requiring evidence from multiple policy documents.

## 7. Agent Orchestration

- [ ] Interpret user intent and determine whether RAG alone is sufficient.
- [ ] Select and call the appropriate MCP-exposed tools.
- [ ] Support at least two multi-step HR workflows.
- [ ] Combine tool results and retrieved evidence into a grounded final response.
- [ ] Produce a concise operational trace showing selected tools, arguments, outputs, sources, response basis, and escalation decisions.
- [ ] Do not expose hidden chain-of-thought.

## 8. MCP Servers and Tools

- [ ] Implement one or more genuine MCP servers.
- [ ] Use and document an MCP-compatible transport such as `stdio` or Streamable HTTP.
- [ ] Expose at least five MCP tools.
- [ ] Include at least one MCP tool that searches or retrieves from the RAG index.
- [ ] Include at least one MCP tool that reads structured mock data or performs a mock operation.
- [ ] Ensure the agent discovers and calls tools through MCP rather than disguised direct function calls.
- [ ] Document MCP architecture, transport, tool schemas, discovery, and tool invocation.
- [ ] Store MCP server code and tool definitions under `mcp/` or an equivalent documented folder.

## 9. Safety and Failure Handling

- [ ] Handle unavailable MCP tools gracefully.
- [ ] Handle missing or invalid employee IDs gracefully.
- [ ] Handle incomplete policy evidence without inventing an answer.
- [ ] Ask for clarification when a request is materially ambiguous.
- [ ] Make all ticket creation, messages, and record updates mock operations.
- [ ] Require explicit user confirmation before any action that appears consequential.
- [ ] Include escalation behavior for sensitive or unsupported cases.

## 10. Web Application

- [ ] Provide a web chat interface for HR questions and workflows.
- [ ] Provide a `/chat` endpoint or documented equivalent.
- [ ] Return the final answer, citations, snippets, and concise tool-call trace.
- [ ] Provide a `/health` endpoint or documented equivalent.
- [ ] Include application status and MCP connectivity status where feasible in the health response.
- [ ] Make both demonstration workflows reproducible through the UI or an API client.

## 11. Automated Testing

- [ ] Add unit, integration, or smoke tests appropriate to the system.
- [ ] Add at least one automated test confirming the application can start.
- [ ] Add at least one test or script confirming MCP tool discovery or a simple MCP tool call.
- [ ] Test core retrieval and citation behavior.
- [ ] Test safety, missing-data, and failure-handling behavior.

## 12. CI/CD

- [ ] Create a GitHub Actions workflow or equivalent CI/CD pipeline.
- [ ] Run the workflow on pushes or pull requests.
- [ ] Install dependencies in the workflow.
- [ ] Run a build, start, or import check.
- [ ] Run automated tests in the workflow.
- [ ] Prevent deployment when tests fail.

## 13. Deployment

- [ ] Deploy the application to Render, Railway, or an equivalent free-tier or zero-cost host.
- [ ] Provide a shareable deployed application URL.
- [ ] Configure deployed secrets using environment variables.
- [ ] Avoid requiring a paid database.
- [ ] Verify both agentic workflows on the deployed application.
- [ ] Document expected free-tier cold-start behavior.
- [ ] Record the deployed application and health URLs in `deployed.md`.

## 14. Evaluation Dataset

- [ ] Create 20-30 evaluation questions or tasks.
- [ ] Include straightforward policy questions.
- [ ] Include multi-document questions.
- [ ] Include tool-requiring agentic tasks.
- [ ] Include ambiguous requests requiring clarification.
- [ ] Include out-of-scope requests.
- [ ] Provide gold answers, expected answers, or scoring rubrics.
- [ ] Store questions, rubrics, scripts, and results under `evaluation/` or an equivalent folder.

## 15. Evaluation Results

- [ ] Measure and report groundedness.
- [ ] Measure and report citation accuracy.
- [ ] Measure exact or partial answer match if appropriate.
- [ ] Measure tool-selection accuracy.
- [ ] Measure workflow-completion rate.
- [ ] Measure escalation or clarification accuracy.
- [ ] Measure action-safety pass rate.
- [ ] Report warm latency p50 and p95 over 10-20 representative tasks.
- [ ] Report cold-start latency separately where possible.
- [ ] Run and report at least one ablation or comparison, such as retrieval k, chunk size, prompt, or tool availability.

## 16. Design Documentation

- [ ] Create `design-and-evaluation.md`.
- [ ] Justify the agent framework or orchestration approach.
- [ ] Explain MCP server design, transport, and tool schemas.
- [ ] Explain the embedding model, chunking strategy, retrieval k, and vector store.
- [ ] Explain the deployment architecture.
- [ ] Explain safety guardrails and confirmation behavior.
- [ ] Include an architecture diagram or clear text-based architecture.
- [ ] Show the web app, agent orchestrator, MCP client, MCP servers, RAG index, mock data, and LLM provider.
- [ ] Describe the two demo workflows and their expected MCP tool-call sequences.
- [ ] Include evaluation questions, expected answers or rubrics, and evaluation results.

## 17. General Documentation

- [ ] Complete `README.md` with an introduction and project overview.
- [ ] Document setup, local execution, deployment, and evaluation procedures.
- [ ] Create `ai-tooling.md` describing all AI development tools used.
- [ ] Explain in `ai-tooling.md` what AI assistance worked well and what did not.
- [ ] Create `deployed.md` with deployed and health endpoint URLs.
- [ ] Keep all required source code in the repository.

## 18. Demonstration Video

- [ ] Record a 7-10 minute screen-share demonstration with voiceover.
- [ ] Ensure every group member, if applicable, speaks, appears on camera, and shows government ID as required.
- [ ] Demonstrate two agentic tasks end-to-end on the deployed application.
- [ ] For each task, explain MCP tool names, arguments, outputs, retrieved citations, and final behavior.
- [ ] Briefly explain the system design and architecture.
- [ ] Briefly show deployment and CI/CD.
- [ ] Briefly present the evaluation results.
- [ ] Produce a shareable presentation link.

## 19. Final Repository Audit

- [ ] Verify the repository contains no API keys, credentials, private data, or unnecessary environment files.
- [ ] Verify a new user can follow the README and run the application.
- [ ] Verify CI passes from a clean checkout.
- [ ] Verify all required files and folders are present.
- [ ] Verify citations and tool traces are readable in the deployed UI.
- [ ] Verify both demo workflows still work immediately before recording or submission.
- [ ] Review this entire checklist against the final implementation.

## 20. Submission

- [ ] Share the GitHub repository with the `quantic-grader` account.
- [ ] Put the deployed application URL in the repository README.
- [ ] Prepare the GitHub repository link for submission.
- [ ] Prepare the recorded presentation link for submission.
- [ ] If working in a group, ensure only one member submits and include the required signed agreement page.
- [ ] Submit both required links through the course dashboard.
