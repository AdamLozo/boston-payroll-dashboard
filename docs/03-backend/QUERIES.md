# SQL Queries

## Employee List Query

```sql
-- GET /api/employees
SELECT 
    id, year, name, department_name, title,
    regular, retro, other, overtime, injured, 
    detail, quinn_education, total_gross, postal
FROM employee_earnings
WHERE year = :year
    AND (:department IS NULL OR department_name = :department)
    AND (:search IS NULL OR 
         name ILIKE '%' || :search || '%' OR
         title ILIKE '%' || :search || '%' OR
         department_name ILIKE '%' || :search || '%')
ORDER BY 
    CASE WHEN :sort_order = 'desc' THEN
        CASE :sort_by
            WHEN 'total_gross' THEN total_gross
            WHEN 'overtime' THEN overtime
            WHEN 'detail' THEN detail
            WHEN 'regular' THEN regular
            WHEN 'name' THEN NULL  -- handled separately
        END
    END DESC NULLS LAST,
    CASE WHEN :sort_order = 'asc' THEN
        CASE :sort_by
            WHEN 'total_gross' THEN total_gross
            WHEN 'overtime' THEN overtime
            WHEN 'detail' THEN detail
            WHEN 'regular' THEN regular
        END
    END ASC NULLS LAST,
    CASE WHEN :sort_by = 'name' AND :sort_order = 'asc' THEN name END ASC,
    CASE WHEN :sort_by = 'name' AND :sort_order = 'desc' THEN name END DESC
LIMIT :limit OFFSET :offset;

-- Count for pagination
SELECT COUNT(*) as total
FROM employee_earnings
WHERE year = :year
    AND (:department IS NULL OR department_name = :department)
    AND (:search IS NULL OR 
         name ILIKE '%' || :search || '%' OR
         title ILIKE '%' || :search || '%' OR
         department_name ILIKE '%' || :search || '%');
```

## Stats Query

```sql
-- GET /api/stats
SELECT 
    COUNT(*) as total_employees,
    SUM(total_gross) as total_payroll,
    AVG(total_gross) as avg_salary,
    SUM(overtime) as total_overtime,
    SUM(detail) as total_detail
FROM employee_earnings
WHERE year = :year
    AND (:department IS NULL OR department_name = :department);

-- Max earner
SELECT name, total_gross
FROM employee_earnings
WHERE year = :year
    AND (:department IS NULL OR department_name = :department)
ORDER BY total_gross DESC
LIMIT 1;
```

## Department Aggregation Query

```sql
-- GET /api/departments
SELECT 
    department_name,
    COUNT(*) as employee_count,
    SUM(total_gross) as total_payroll,
    SUM(overtime) as total_overtime,
    SUM(detail) as total_detail,
    AVG(total_gross) as avg_salary
FROM employee_earnings
WHERE year = :year
GROUP BY department_name
ORDER BY 
    CASE :sort_by
        WHEN 'total' THEN SUM(total_gross)
        WHEN 'overtime' THEN SUM(overtime)
        WHEN 'detail' THEN SUM(detail)
        WHEN 'count' THEN COUNT(*)
    END DESC
LIMIT :limit;
```

## Earnings Breakdown Query

```sql
-- GET /api/earnings-breakdown
SELECT 
    SUM(regular) as regular,
    SUM(retro) as retro,
    SUM(other) as other,
    SUM(overtime) as overtime,
    SUM(injured) as injured,
    SUM(detail) as detail,
    SUM(quinn_education) as quinn_education,
    SUM(total_gross) as total
FROM employee_earnings
WHERE year = :year
    AND (:department IS NULL OR department_name = :department);
```

## Utility Queries

```sql
-- GET /api/years
SELECT DISTINCT year FROM employee_earnings ORDER BY year DESC;

-- GET /api/department-list
SELECT DISTINCT department_name 
FROM employee_earnings 
WHERE (:year IS NULL OR year = :year)
ORDER BY department_name;

-- GET /api/health
SELECT COUNT(*) as record_count FROM employee_earnings;
```

## Performance Notes

1. Always include `year` in WHERE clause - it's indexed
2. Search uses ILIKE which benefits from trigram index
3. Limit max results to 500 to prevent memory issues
4. Use connection pooling in production
