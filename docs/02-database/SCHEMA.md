# Database Schema

## Connection

Use existing Render PostgreSQL instance (shared with building permits and restaurant inspections).

```
Database: boston_data (or check existing database name)
Host: [from Render dashboard]
Port: 5432
```

## Table: employee_earnings

```sql
CREATE TABLE IF NOT EXISTS employee_earnings (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    department_name VARCHAR(200),
    title VARCHAR(200),
    regular DECIMAL(12,2) DEFAULT 0,
    retro DECIMAL(12,2) DEFAULT 0,
    other DECIMAL(12,2) DEFAULT 0,
    overtime DECIMAL(12,2) DEFAULT 0,
    injured DECIMAL(12,2) DEFAULT 0,
    detail DECIMAL(12,2) DEFAULT 0,
    quinn_education DECIMAL(12,2) DEFAULT 0,
    total_gross DECIMAL(12,2) DEFAULT 0,
    postal VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite unique constraint for upsert
    UNIQUE(year, name, department_name, title)
);
```

## Design Decisions

1. **Single table with year column** - Simpler than separate tables per year
2. **Decimal(12,2)** - Handles up to $9,999,999,999.99 (plenty of headroom)
3. **VARCHAR(200)** - Accommodates long department/title names
4. **Composite unique** - Allows upsert on reload without duplicates
5. **No separate dimension tables** - Keep it simple, department/title denormalized

## Alternative: Normalized Schema (Not Recommended)

```sql
-- Only if we need to track department changes over time
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE
);

CREATE TABLE titles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE
);

-- More complex, not needed for this use case
```

## Data Types Mapping

| CSV Column | PostgreSQL Type | Notes |
|------------|-----------------|-------|
| NAME | VARCHAR(200) | As-is |
| DEPARTMENT_NAME | VARCHAR(200) | As-is |
| TITLE | VARCHAR(200) | As-is |
| REGULAR | DECIMAL(12,2) | Parse commas |
| RETRO | DECIMAL(12,2) | Parse commas |
| OTHER | DECIMAL(12,2) | Parse commas |
| OVERTIME | DECIMAL(12,2) | Parse commas |
| INJURED | DECIMAL(12,2) | Parse commas |
| DETAIL | DECIMAL(12,2) | Parse commas |
| QUINN_EDUCATION | DECIMAL(12,2) | Parse commas |
| TOTAL GROSS | DECIMAL(12,2) | Parse commas |
| POSTAL | VARCHAR(10) | As-is |
| (added) year | INTEGER | From filename |
