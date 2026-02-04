# Database Indexes

## Required Indexes

```sql
-- Primary search/filter indexes
CREATE INDEX idx_earnings_year ON employee_earnings(year);
CREATE INDEX idx_earnings_department ON employee_earnings(department_name);
CREATE INDEX idx_earnings_total_gross ON employee_earnings(total_gross DESC);

-- Composite indexes for common queries
CREATE INDEX idx_earnings_year_dept ON employee_earnings(year, department_name);
CREATE INDEX idx_earnings_year_total ON employee_earnings(year, total_gross DESC);

-- Full-text search on name (for search box)
CREATE INDEX idx_earnings_name_trgm ON employee_earnings USING gin(name gin_trgm_ops);

-- Note: Requires pg_trgm extension
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## Index Strategy

### For Table Sorting/Filtering
- `idx_earnings_year` - Filter by year dropdown
- `idx_earnings_department` - Filter by department dropdown
- `idx_earnings_total_gross` - Sort by earnings (default sort)

### For Aggregations
- `idx_earnings_year_dept` - Department breakdown charts by year

### For Search
- `idx_earnings_name_trgm` - Fuzzy name search (ILIKE '%smith%')

## Query Performance Targets

| Query | Target | Index Used |
|-------|--------|------------|
| Top 100 earners (2024) | < 50ms | idx_earnings_year_total |
| Filter by department | < 100ms | idx_earnings_year_dept |
| Name search | < 200ms | idx_earnings_name_trgm |
| Department totals | < 200ms | idx_earnings_year_dept |

## Verify Indexes

```sql
-- Check existing indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'employee_earnings';

-- Analyze query plan
EXPLAIN ANALYZE 
SELECT * FROM employee_earnings 
WHERE year = 2024 
ORDER BY total_gross DESC 
LIMIT 100;
```
