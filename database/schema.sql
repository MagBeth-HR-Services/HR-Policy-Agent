PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    employment_type TEXT NOT NULL,
    department TEXT NOT NULL,
    job_title TEXT NOT NULL,
    manager_id TEXT,
    work_mode TEXT NOT NULL,
    primary_city TEXT NOT NULL,
    primary_state TEXT NOT NULL,
    primary_country TEXT NOT NULL,
    hire_date TEXT NOT NULL,
    status TEXT NOT NULL,
    data_access_level TEXT NOT NULL,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS pto_balances (
    employee_id TEXT PRIMARY KEY,
    available_hours REAL NOT NULL,
    approved_future_hours REAL NOT NULL,
    annual_accrual_hours REAL NOT NULL,
    carryover_hours REAL NOT NULL,
    last_updated TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS benefits (
    employee_id TEXT PRIMARY KEY,
    benefits_eligible INTEGER NOT NULL,
    medical_status TEXT NOT NULL,
    dental_status TEXT NOT NULL,
    vision_status TEXT NOT NULL,
    enrollment_effective_date TEXT,
    last_updated TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS hr_tickets (
    ticket_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    category TEXT NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    confirmed_by_user INTEGER NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);