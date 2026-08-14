# Synthetic HR Data Schema

All records in this project are fictional and created only for educational use.

## Data Storage Strategy

Human-readable source data will be committed as JSON files under `mock_data/`.

The application will later load the JSON records into:

```text
./data/hr_data.db
```

The SQLite database is the runtime data store used by MCP tools.

## Employee Profiles

File: `employees.json`

| Field | Type | Description |
| --- | --- | --- |
| employee_id | string | Stable fictional identifier such as E1001 |
| first_name | string | Fictional first name |
| last_name | string | Fictional last name |
| employment_type | string | full_time, part_time, intern, or contractor |
| department | string | Fictional department |
| job_title | string | Fictional role |
| manager_id | string or null | Employee ID of the fictional manager |
| work_mode | string | office, hybrid, or remote |
| primary_city | string | Approved primary work city |
| primary_state | string | Approved US state |
| primary_country | string | Approved country |
| hire_date | string | ISO date in YYYY-MM-DD format |
| status | string | active or inactive |
| data_access_level | string | standard, confidential, or restricted |

## PTO Balances

File: `pto_balances.json`

| Field | Type | Description |
| --- | --- | --- |
| employee_id | string | Links to an employee profile |
| available_hours | number | PTO currently available |
| approved_future_hours | number | PTO already approved for future dates |
| annual_accrual_hours | number | Expected yearly accrual |
| carryover_hours | number | Hours carried from the prior year |
| last_updated | string | ISO date |
| notes | string | Optional synthetic explanation |

## Benefits Status

File: `benefits.json`

| Field | Type | Description |
| --- | --- | --- |
| employee_id | string | Links to an employee profile |
| benefits_eligible | boolean | Whether the employee is currently eligible |
| medical_status | string | enrolled, waived, pending, or ineligible |
| dental_status | string | enrolled, waived, pending, or ineligible |
| vision_status | string | enrolled, waived, pending, or ineligible |
| enrollment_effective_date | string or null | ISO date |
| last_updated | string | ISO date |

## Mock HR Tickets

File: `hr_tickets.json`

| Field | Type | Description |
| --- | --- | --- |
| ticket_id | string | Stable mock ticket identifier |
| employee_id | string | Employee connected to the request |
| category | string | PTO, remote_work, benefits, conduct, or other |
| summary | string | Non-sensitive mock description |
| status | string | draft, open, or closed |
| created_at | string | ISO date-time |
| confirmed_by_user | boolean | Whether explicit confirmation was received |

## Data Rules

- All data must be clearly synthetic.
- Employee IDs must be unique.
- Relationships must reference valid employee IDs.
- PTO and benefits records must reference valid employees.
- Dates must use ISO format.
- No real names, emails, addresses, or private employee information may be used.
- The application must not expose unnecessary employee fields.
- Mock ticket creation requires explicit user confirmation.
- Missing or conflicting records must produce a clear error or escalation.