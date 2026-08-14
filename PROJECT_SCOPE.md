# HR Policy Agent - Project Scope

## 1. Project Goal

Build and deploy an agentic HR assistant for a fictional company. The assistant will answer policy questions using Retrieval-Augmented Generation (RAG), retrieve synthetic employee information through Model Context Protocol (MCP) tools, complete multi-step HR workflows, and provide grounded responses with readable citations and operational tool traces.

The system will be designed for local development and modest free-tier deployment.

## 2. Fictional Company

**Company name:** Horizon Technologies

Horizon Technologies is a fictional, medium-sized US software company with office-based, hybrid, and remote employees. All company documents, employee records, balances, and workflow results in this project will be synthetic.

No real employee information or confidential company information will be used.

## 3. Policy Areas

The policy corpus will cover these areas:

1. Paid time off (PTO)
2. Company holidays
3. Remote work
4. Temporary domestic and international work locations
5. Information and data security
6. Business expenses and reimbursement
7. Company equipment
8. Employee benefits
9. Employee leave
10. Employee onboarding
11. Workplace conduct

These topics provide enough breadth for ordinary policy questions while supporting the two selected multi-step demonstration workflows.

## 4. Demonstration Workflow 1 - PTO Request Guidance

### Example user request

> I am employee E1001. Can I take three PTO days next week?

### Intended behavior

The agent should:

1. Identify the employee ID supplied by the user.
2. Retrieve the employee's synthetic profile.
3. Retrieve the employee's synthetic PTO balance.
4. Search for relevant PTO policy evidence.
5. Determine whether the request appears to satisfy the available balance and policy rules.
6. Explain notice and manager-approval requirements with citations.
7. Offer an appropriate mock next step, such as drafting a manager message or creating a mock HR ticket.
8. Obtain explicit confirmation before performing the mock action.

### Expected MCP tool sequence

The exact sequence may vary when justified, but the normal sequence is:

1. `lookup_employee_profile`
2. `check_pto_balance`
3. `search_policy_documents`
4. `get_policy_section`, if more precise evidence is needed
5. `check_policy_compliance`
6. `create_mock_hr_ticket`, only after explicit confirmation and only if requested

### Requirements demonstrated

- Structured employee-data lookup
- Structured PTO-balance lookup
- Policy retrieval through MCP
- Grounded policy citations
- Multi-tool agent behavior
- Compliance checking
- Confirmation before a mock action
- Concise tool-call tracing

## 5. Demonstration Workflow 2 - Temporary International Remote Work

### Example user request

> I am employee E1002. Can I work from another country for six weeks?

### Intended behavior

The agent should:

1. Identify the employee ID supplied by the user.
2. Retrieve the employee's synthetic profile and normal work location.
3. Search the remote-work policy.
4. Search the temporary-location or international-work policy.
5. Search the information-security policy.
6. Combine evidence from multiple policy documents.
7. Check the request against the available policy rules.
8. Explain approval, security, location, duration, and escalation requirements with citations.
9. Offer to create a mock HR review ticket when appropriate.
10. Obtain explicit confirmation before creating the mock ticket.

### Expected MCP tool sequence

The exact sequence may vary when justified, but the normal sequence is:

1. `lookup_employee_profile`
2. `search_policy_documents` for remote-work evidence
3. `search_policy_documents` for international-location evidence
4. `search_policy_documents` for security evidence
5. `get_policy_section`, when more precise evidence is needed
6. `check_policy_compliance`
7. `create_mock_hr_ticket`, only after explicit confirmation and only if requested

### Requirements demonstrated

- Structured employee-data lookup
- Multi-document retrieval
- Policy evidence from several subject areas
- Grounded citations and snippets
- Multi-step agent planning and tool selection
- Escalation when automated approval is inappropriate
- Confirmation before a mock action
- Concise tool-call tracing

## 6. Initial MCP Tool Scope

The system will expose at least these six tools through MCP:

### `search_policy_documents`

Search the RAG index for policy evidence relevant to a query. Return matching content and citation metadata.

### `get_policy_section`

Retrieve a specific policy section using its document and section identifiers.

### `lookup_employee_profile`

Retrieve a synthetic employee profile by employee ID.

### `check_pto_balance`

Retrieve the synthetic PTO balance for an employee.

### `check_policy_compliance`

Compare a structured request with relevant policy rules and return an explainable preliminary result. This tool will not make legally binding or irreversible decisions.

### `create_mock_hr_ticket`

Create a clearly labeled mock HR ticket after explicit user confirmation. It will not contact a real HR system or person.

An additional `draft_hr_email` tool may be considered later if it adds useful functionality without unnecessarily increasing scope.

## 7. Safety Boundaries

- The assistant will use only fictional company policies and synthetic employee data.
- The assistant will not make real employment, legal, tax, benefits, or disciplinary decisions.
- The assistant will distinguish policy evidence from general recommendations.
- The assistant will state when the policy corpus does not contain enough evidence.
- The assistant will request missing employee IDs or other essential information.
- The assistant will request clarification when a materially ambiguous request cannot be handled safely.
- The assistant will escalate sensitive, unsupported, or exception-based cases to a fictional HR reviewer.
- Ticket creation, email drafting, and record changes will be mock operations.
- The assistant will obtain explicit user confirmation before performing a mock action that appears consequential.
- Operational traces will show tool names, arguments, results, citations, and decisions without exposing hidden chain-of-thought.

## 8. Features Outside the Initial Scope

The initial project will not include:

- Real employee or company data
- Integration with a real HR information system
- Real email or messaging delivery
- Real ticket creation
- Payroll processing
- Automated approval or denial of leave
- Automated employment or disciplinary decisions
- Legal, immigration, or tax advice
- Voice interaction
- A mobile application
- Multiple organizations or tenants
- Paid database infrastructure
- A large production-scale policy corpus

These exclusions keep the project focused, safe, explainable, and achievable while meeting the assignment requirements.

## 9. Definition of Scope Completion

This scope is complete when the deployed application can reliably demonstrate both selected workflows end-to-end, including genuine MCP tool calls, structured mock-data lookup, policy retrieval, readable citations, operational traces, graceful failure handling, and confirmation before mock actions.
