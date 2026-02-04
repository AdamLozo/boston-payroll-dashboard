# Data Layer Context

## Overview
The data layer handles PostgreSQL schema, CSV data loading, and data access patterns. This uses the shared Render PostgreSQL database.

## Database Connection

**Shared Database**: Same Render PostgreSQL instance as building permits and restaurants dashboards.

```python
# Connection string format
DATABASE_URL = "postgresql://user:password@host:5432/dbname"
# Accessed via environment variable
```

## Schema Design

### Main Table: `payroll_earnings`

```sql
CREATE TABLE IF NOT EXISTS payroll_earnings (
    id SERIAL PRIMARY KEY,
    
    -- Year identifier (derived from source file)
    year INTEGER NOT NULL,
    
    -- Employee info
    name VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    title VARCHAR(255),
    
    -- Earnings breakdown (all in dollars, can be negative for corrections)
    regular DECIMAL(12,2) DEFAULT 0,
    retro DECIMAL(12,2) DEFAULT 0,
    other DECIMAL(12,2) DEFAULT 0,
    overtime DECIMAL(12,2) DEFAULT 0,
    injured DECIMAL(12,2) DEFAULT 0,
    detail DECIMAL(12,2) DEFAULT 0,
    quinn_education DECIMAL(12,2) DEFAULT 0,
    total_gross DECIMAL(12,2) DEFAULT 0,
    
    -- Location
    zip_code VARCHAR(10),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite unique constraint (same person can appear in multiple years)
    UNIQUE(year, name, department, title)
);

-- Indexes for common queries
CREATE INDEX idx_payroll_year ON payroll_earnings(year);
CREATE INDEX idx_payroll_department ON payroll_earnings(department);
CREATE INDEX idx_payroll_total_gross ON payroll_earnings(total_gross DESC);
CREATE INDEX idx_payroll_name_search ON payroll_earnings(name varchar_pattern_ops);
CREATE INDEX idx_payroll_year_dept ON payroll_earnings(year, department);
```

### Why These Indexes
- `year`: Filter by year (most common filter)
- `department`: Filter and group by department
- `total_gross DESC`: Top earners queries
- `name varchar_pattern_ops`: LIKE searches for name filtering
- `year, department`: Combined filter optimization

## Data Sources

### CSV Resource IDs
| Year | Resource ID | Expected Records |
|------|-------------|------------------|
| 2024 | `579a4be3-9ca7-4183-bc95-7d67ee715b6d` | ~22,000 |
| 2023 | `6b3c5333-1dcb-4b3d-9cd7-6a03fb526da7` | ~22,000 |
| 2022 | `63ac638b-36c4-487d-9453-1d83eb5090d2` | ~21,000 |
| 2021 | `ec5aaf93-1509-4641-9310-28e62e028457` | ~20,000 |
| 2020 | `e2e2c23a-6fc7-4456-8751-5321d8aa869b` | ~20,000 |

### CSV Download URLs
```python
BASE_URL = "https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/{resource_id}/download"
```

### Field Mapping

| CSV Column | Database Column | Transform |
|------------|-----------------|-----------|
| NAME | name | Strip whitespace |
| DEPARTMENT_NAME | department | Strip whitespace |
| TITLE | title | Strip whitespace |
| REGULAR | regular | Parse as decimal, handle empty |
| RETRO | retro | Parse as decimal, handle empty |
| OTHER | other | Parse as decimal, handle empty |
| OVERTIME | overtime | Parse as decimal, handle empty |
| INJURED | injured | Parse as decimal, handle empty |
| DETAIL | detail | Parse as decimal, handle empty |
| QUINN_EDUCATION | quinn_education | Parse as decimal, handle empty |
| TOTAL GROSS | total_gross | Parse as decimal, handle empty |
| POSTAL | zip_code | Strip whitespace, validate format |

### Data Quality Notes
- Some earnings values can be negative (corrections/adjustments)
- Some employees have incomplete data (blanks in certain columns)
- ZIP codes may be missing or malformed
- Names may have inconsistent formatting across years

## Load Strategy

### Initial Load Process
1. Download CSV for each year
2. Parse and transform records
3. Bulk insert using `COPY` or batch INSERT
4. Validate record counts

### Upsert Logic
```python
def upsert_earnings(conn, record, year):
    """
    Insert or update an earnings record.
    Conflict on (year, name, department, title) updates all earnings fields.
    """
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO payroll_earnings (
            year, name, department, title,
            regular, retro, other, overtime, injured, detail,
            quinn_education, total_gross, zip_code
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (year, name, department, title) DO UPDATE SET
            regular = EXCLUDED.regular,
            retro = EXCLUDED.retro,
            other = EXCLUDED.other,
            overtime = EXCLUDED.overtime,
            injured = EXCLUDED.injured,
            detail = EXCLUDED.detail,
            quinn_education = EXCLUDED.quinn_education,
            total_gross = EXCLUDED.total_gross,
            zip_code = EXCLUDED.zip_code
        RETURNING id
    """, (
        year, record['name'], record['department'], record['title'],
        record['regular'], record['retro'], record['other'],
        record['overtime'], record['injured'], record['detail'],
        record['quinn_education'], record['total_gross'], record['zip_code']
    ))
    return cur.fetchone()[0]
```

## Query Patterns

### Common Queries

**Top Earners by Year**
```sql
SELECT name, department, title, total_gross
FROM payroll_earnings
WHERE year = $1
ORDER BY total_gross DESC
LIMIT 50;
```

**Department Aggregation**
```sql
SELECT 
    department,
    COUNT(*) as employee_count,
    SUM(total_gross) as total_earnings,
    AVG(total_gross) as avg_earnings,
    SUM(overtime) as total_overtime,
    SUM(detail) as total_detail
FROM payroll_earnings
WHERE year = $1
GROUP BY department
ORDER BY total_earnings DESC;
```

**Search by Name**
```sql
SELECT *
FROM payroll_earnings
WHERE year = $1
  AND name ILIKE '%' || $2 || '%'
ORDER BY total_gross DESC
LIMIT 100;
```

**Year-over-Year for Department**
```sql
SELECT 
    year,
    COUNT(*) as employees,
    SUM(total_gross) as total,
    AVG(total_gross) as average
FROM payroll_earnings
WHERE department = $1
GROUP BY year
ORDER BY year;
```

## Validation Queries

Run these after data load:

```sql
-- Record counts by year
SELECT year, COUNT(*) FROM payroll_earnings GROUP BY year ORDER BY year;

-- Total earnings by year (sanity check)
SELECT year, SUM(total_gross)::money FROM payroll_earnings GROUP BY year ORDER BY year;

-- Check for duplicates
SELECT year, name, department, title, COUNT(*)
FROM payroll_earnings
GROUP BY year, name, department, title
HAVING COUNT(*) > 1;

-- Check for negative totals (unusual but valid)
SELECT * FROM payroll_earnings WHERE total_gross < 0 LIMIT 10;

-- Department count
SELECT COUNT(DISTINCT department) FROM payroll_earnings;

-- Top departments by employee count
SELECT department, COUNT(*) as employees
FROM payroll_earnings
WHERE year = 2024
GROUP BY department
ORDER BY employees DESC
LIMIT 20;
```

## Performance Considerations

- **Index on total_gross DESC**: Speeds up "top earners" queries
- **Composite index (year, department)**: Most common filter combination
- **LIMIT clauses**: Always use pagination
- **Connection pooling**: Use psycopg2 pool or asyncpg

## Dependencies
- PostgreSQL 14+
- psycopg2 or asyncpg
- pandas (for CSV parsing)
- requests (for CSV download)
