# Horizon HR Policy Agent — Project Scope

## 1. Project Goal

Build and deploy an agentic HR assistant for the fictional company Horizon Technologies.

The assistant combines:

- Retrieval-Augmented Generation over company policies
- Synthetic employee and HR information
- LangGraph agent orchestration
- Tools exposed through genuine MCP servers
- Grounded policy answers with citations
- Safe mock HR operations
- A browser-based FastAPI chat interface

The system currently runs locally. Deployment, expanded evaluation, visible UI tool traces, and final demonstration preparation remain pending.

## 2. Fictional Company and Data

Horizon Technologies is a fictional, medium-sized US software company with office-based, hybrid, and remote employees.

All policies, employee records, balances, benefits information, and HR tickets in this project are synthetic. The project contains no real employee information or confidential company data.

The application is an educational demonstration. It does not provide real HR, legal, tax, immigration, medical, or financial advice.

## 3. Implemented Policy Areas

The policy corpus contains 11 fictional policies covering:

1. Paid time off
2. Company holidays
3. Remote work
4. Temporary domestic and international work locations
5. Information security
6. Business expenses
7. Company equipment
8. Employee benefits
9. Employee leave
10. Employee onboarding
11. Workplace conduct

The corpus uses both Markdown and PDF source formats.

## 4. Selected Demonstration Workflow 1 — PTO Guidance

### Example request

> I am employee E1001. Can I take three PTO days next week?

### Intended behavior

The agent should:

1. Identify and validate the employee ID.
2. Retrieve the employee’s synthetic profile when relevant.
3. Retrieve the employee’s synthetic PTO balance.
4. Search for PTO policy evidence.
5. Compare the request with the balance and policy requirements.
6. Explain notice and manager-approval requirements with citations.
7. Avoid claiming that the request is approved.
8. Offer an appropriate mock next step.
9. Require explicit confirmation before creating a mock HR ticket.

### Expected implemented tool sequence

The exact sequence may vary depending on the request:

1. `hr_get_employee_summary`
2. `hr_get_pto_balance`
3. `policy_search_policies`
4. `hr_create_hr_ticket`, only after explicit confirmation

### Current status

The required policy-search, employee-summary, PTO-balance, and mock-ticket tools are implemented through MCP.

Employee-ID validation and explicit-confirmation safeguards are implemented and tested.

The final end-to-end workflow still needs to be verified in the deployed browser interface before recording the demonstration.

## 5. Selected Demonstration Workflow 2 — International Temporary Work

### Example request

> I am employee E1002. Can I work from another country for six weeks?

### Intended behavior

The agent should:

1. Identify and validate the employee ID.
2. Retrieve the employee’s synthetic profile and primary work location.
3. Search the temporary-work-location policy.
4. Retrieve related remote-work and information-security evidence when needed.
5. Combine employee information with policy evidence.
6. Explain location, duration, approval, security, and escalation requirements.
7. Cite the relevant policy IDs and sections.
8. Avoid approving the request.
9. Offer to create a mock HR review ticket.
10. Require explicit confirmation before creating the ticket.

### Expected implemented tool sequence

The exact sequence may vary depending on the evidence required:

1. `hr_get_employee_summary`
2. `policy_search_policies`
3. Additional calls to `policy_search_policies` when multiple policy subjects are needed
4. `hr_create_hr_ticket`, only after explicit confirmation

### Current status

The combined employee-profile and policy-search workflow is implemented and included in the evaluation suite.

The agent correctly identifies the 20-business-day limit, retrieves `POL-004`, recommends multi-department review, and does not approve the request.

The final workflow still needs to be verified in the deployed browser interface before recording the demonstration.

## 6. Implemented MCP Scope

The agent connects to two FastMCP servers using `stdio`.

### Policy MCP server

#### `policy_health_check`

Confirms that the policy MCP server can start and respond.

#### `policy_search_policies`

Searches the Chroma policy index and returns ranked policy evidence with:

- Policy ID
- Title
- Section
- Page number when applicable
- Chunk ID
- Source filename
- Snippet
- Full chunk content
- Relevance score

### HR MCP server

#### `hr_health_check`

Confirms that the HR MCP server can start and respond.

#### `hr_get_employee_summary`

Retrieves a synthetic employee profile by employee ID.

#### `hr_get_pto_balance`

Retrieves the synthetic PTO balance for an employee.

#### `hr_get_benefits_status`

Retrieves synthetic benefits eligibility and enrollment information.

#### `hr_create_hr_ticket`

Creates a clearly labeled mock HR ticket after explicit confirmation.

### Tool-count status

Seven MCP tools are discoverable by the agent. Five perform policy or HR operations, and two provide server health checks.

## 7. Implemented Safety Boundaries

The current implementation includes these boundaries:

- Only fictional policies and synthetic employee data are used.
- Employee IDs must follow the `E####` format.
- Invalid employee references are rejected before the LLM can reinterpret them.
- Employee tools return only the information required for the request.
- Missing records are reported without unsupported speculation.
- Policy answers must use retrieved company evidence.
- The agent does not approve HR requests.
- Sensitive or unsupported cases are escalated to HR review.
- Ticket creation is a mock operation.
- Explicit user confirmation is required before ticket creation.
- Unexpected internal errors are converted into safe user messages.
- Hidden chain-of-thought is not displayed.

## 8. Features Outside Scope

The project will not include:

- Real employee or company information
- Integration with a production HR information system
- Real email or messaging delivery
- Real HR ticket creation
- Payroll processing
- Automated approval or denial of employee requests
- Automated employment or disciplinary decisions
- Legal, tax, immigration, medical, or financial advice
- Voice interaction
- A mobile application
- Multiple organizations or tenants
- A paid production database
- A production-scale policy corpus

These exclusions keep the project safe, explainable, and compatible with modest hosting resources.

## 9. Remaining Work Before Submission

The following items remain within the project scope but are not yet complete:

- Record the required demonstration video
- Invite `quantic-grader` and submit the GitHub and presentation links

## 10. Definition of Scope Completion

The project scope will be complete when:

1. The application is accessible through a shareable deployed URL.
2. Both selected workflows run end-to-end through the deployed interface.
3. The workflows use genuine MCP tool calls.
4. Policy responses include grounded citations.
5. The interface provides a concise operational tool trace without exposing hidden reasoning.
6. Safety, error handling, and confirmation behavior work as intended.
7. The assignment-required evaluation and metrics are complete.
8. All required documentation is present.
9. CI passes for the final repository state.
10. The demonstration and submission requirements are satisfied.