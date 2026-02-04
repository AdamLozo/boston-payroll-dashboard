# Data Layer Implementation Checklist

## Prerequisites
- [ ] Access to Render PostgreSQL connection string
- [ ] Python 3.9+ installed
- [ ] Virtual environment created

## Tasks

### Task 1: Create Database Schema
**Files**: `backend/database.py`
**Time**: 10 minutes

- [ ] Create `payroll_earnings` table
- [ ] Create all indexes
- [ ] Test connection to shared database
- [ ] Verify table creation with `\dt payroll_*`

**Verification**:
```bash
psql $DATABASE_URL -c "\dt payroll_*"
# Should show: payroll_earnings
```

### Task 2: Build CSV Download Script
**Files**: `scripts/load_data.py`
**Time**: 15 minutes

- [ ] Define resource IDs dictionary
- [ ] Create download function with retry logic
- [ ] Handle encoding issues (UTF-8 with BOM)
- [ ] Save to temp directory

**Verification**:
```bash
python scripts/load_data.py --download-only --year 2024
# Should create: /tmp/boston_earnings_2024.csv
ls -la /tmp/boston_earnings_*.csv
```

### Task 3: Build CSV Parser
**Files**: `scripts/load_data.py`
**Time**: 15 minutes

- [ ] Parse CSV with pandas
- [ ] Handle column name variations
- [ ] Clean numeric fields (remove commas, handle blanks)
- [ ] Normalize text fields (strip whitespace)
- [ ] Add year column

**Verification**:
```python
# In script
df = parse_csv('/tmp/boston_earnings_2024.csv', year=2024)
print(f"Rows: {len(df)}, Columns: {list(df.columns)}")
print(df.head())
```

### Task 4: Implement Bulk Insert
**Files**: `scripts/load_data.py`
**Time**: 15 minutes

- [ ] Use `COPY` command for speed (or batch INSERT)
- [ ] Handle upsert on conflict
- [ ] Add progress indicator
- [ ] Transaction management

**Verification**:
```bash
python scripts/load_data.py --year 2024
# Should output: Inserted 22,XXX records for 2024
```

### Task 5: Load All Years
**Files**: `scripts/load_data.py`
**Time**: 10 minutes (execution)

- [ ] Loop through 2020-2024
- [ ] Track total records
- [ ] Log any errors

**Verification**:
```sql
SELECT year, COUNT(*) 
FROM payroll_earnings 
GROUP BY year 
ORDER BY year;
```

Expected output:
```
 year  | count
-------+-------
 2020  | ~20000
 2021  | ~20000
 2022  | ~21000
 2023  | ~22000
 2024  | ~22000
```

### Task 6: Validate Data Quality
**Files**: `scripts/validate_data.py`
**Time**: 10 minutes

- [ ] Check record counts match source
- [ ] Verify no duplicates
- [ ] Check department list is reasonable
- [ ] Verify earnings totals
- [ ] Check for orphaned/invalid data

**Verification**:
```bash
python scripts/validate_data.py
# Should output: All validations passed
```

### Task 7: Create Database Access Module
**Files**: `backend/database.py`
**Time**: 10 minutes

- [ ] Connection pool setup
- [ ] Context manager for connections
- [ ] Helper functions for common queries

**Verification**:
```python
from backend.database import get_db_connection
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM payroll_earnings")
    print(cur.fetchone())
```

## Completion Criteria

- [ ] All 5 years loaded (~100K total records)
- [ ] No duplicate entries
- [ ] All indexes created
- [ ] Validation script passes
- [ ] Connection pooling works
- [ ] Query performance acceptable (< 100ms for common queries)

## Handoff to Phase 2

After completing this phase, the following should work:

```sql
-- This query should return results
SELECT department, COUNT(*), SUM(total_gross)::money
FROM payroll_earnings
WHERE year = 2024
GROUP BY department
ORDER BY SUM(total_gross) DESC
LIMIT 10;
```

## Rollback Plan

If something goes wrong:
```sql
-- Drop table and start over
DROP TABLE IF EXISTS payroll_earnings CASCADE;
```

## Notes

- Shared database requires table prefix `payroll_`
- Keep load script for annual refresh
- Document any field mapping issues discovered
