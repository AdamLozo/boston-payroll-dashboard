# Testing Context

## Overview
Testing strategy for the Boston Payroll Dashboard, covering data validation, API testing, frontend testing, and production verification.

## Testing Phases

### 1. Data Validation (Phase 1)
Verify data integrity after loading.

### 2. API Testing (Phase 2)
Verify all endpoints return correct data.

### 3. Frontend Testing (Phase 3)
Verify UI components and interactions.

### 4. Integration Testing (Phase 4)
Verify full stack works in production.

## Data Validation Queries

### Record Counts
```sql
-- Total by year (expected: ~100K total)
SELECT year, COUNT(*) as records
FROM payroll_earnings
GROUP BY year
ORDER BY year;

-- Expected ranges:
-- 2020: 19,000 - 21,000
-- 2021: 19,000 - 21,000
-- 2022: 20,000 - 22,000
-- 2023: 21,000 - 23,000
-- 2024: 21,000 - 23,000
```

### Data Quality
```sql
-- Check for duplicates (should return 0)
SELECT year, name, department, title, COUNT(*)
FROM payroll_earnings
GROUP BY year, name, department, title
HAVING COUNT(*) > 1;

-- Check for null names (should return 0)
SELECT COUNT(*) FROM payroll_earnings WHERE name IS NULL;

-- Check total gross calculation
SELECT COUNT(*) 
FROM payroll_earnings 
WHERE ABS(total_gross - (regular + retro + other + overtime + injured + detail + quinn_education)) > 1;
-- Small differences OK due to rounding

-- Negative earnings (valid, but check count is reasonable)
SELECT year, COUNT(*) as negative_count
FROM payroll_earnings
WHERE total_gross < 0
GROUP BY year;
```

### Department Validation
```sql
-- Department count (expected: 50-80)
SELECT COUNT(DISTINCT department) FROM payroll_earnings;

-- Top departments (verify known large departments exist)
SELECT department, COUNT(*) as employees
FROM payroll_earnings
WHERE year = 2024
GROUP BY department
ORDER BY employees DESC
LIMIT 10;
-- Should include: Boston Police, Fire, Schools, Public Works
```

### Earnings Validation
```sql
-- Total payroll by year (sanity check)
SELECT year, 
       SUM(total_gross)::money as total_payroll,
       AVG(total_gross)::money as avg_salary
FROM payroll_earnings
GROUP BY year
ORDER BY year;

-- Top earner each year (verify reasonable amounts)
SELECT DISTINCT ON (year)
       year, name, department, total_gross::money
FROM payroll_earnings
ORDER BY year, total_gross DESC;
```

## API Test Cases

### Health Endpoint
```bash
# Should return 200 with healthy status
curl -w "%{http_code}" http://localhost:8000/api/health
```

### Years Endpoint
```bash
# Should return 5 years
curl http://localhost:8000/api/years
# Expected: {"years": [2024, 2023, 2022, 2021, 2020], "default": 2024}
```

### Employees Endpoint
```bash
# Basic query
curl "http://localhost:8000/api/employees?year=2024&limit=5"
# Should return 5 records with all fields

# With department filter
curl "http://localhost:8000/api/employees?year=2024&department=Boston%20Police%20Department&limit=5"
# Should return only police employees

# With search
curl "http://localhost:8000/api/employees?year=2024&search=smith&limit=5"
# Should return employees with "smith" in name

# Pagination
curl "http://localhost:8000/api/employees?year=2024&limit=10&offset=100"
# Should return records 101-110

# Sorting
curl "http://localhost:8000/api/employees?year=2024&sort_by=overtime&sort_order=desc&limit=5"
# Should return top OT earners
```

### Departments Endpoint
```bash
curl "http://localhost:8000/api/departments?year=2024"
# Should return 50+ departments with stats
```

### Stats Endpoint
```bash
# Overall stats
curl "http://localhost:8000/api/stats?year=2024"
# Should return total_employees > 20000

# Department stats
curl "http://localhost:8000/api/stats?year=2024&department=Boston%20Fire%20Department"
# Should return filtered stats
```

### Earnings Breakdown
```bash
curl "http://localhost:8000/api/earnings-breakdown?year=2024"
# Should return breakdown with percentages totaling ~100%
```

## Frontend Test Cases

### Filters
| Test | Steps | Expected |
|------|-------|----------|
| Year filter | Select different year | Table and stats update |
| Department filter | Select department | Table filters, stats update |
| Search | Type name | Table filters in real-time |
| Clear search | Clear input | Table shows all |
| Combined filters | Year + Dept + Search | All filters combine |

### Data Table
| Test | Steps | Expected |
|------|-------|----------|
| Initial load | Open page | Shows 50 rows |
| Sort ascending | Click column header | Sorts A-Z or low-high |
| Sort descending | Click again | Sorts Z-A or high-low |
| Pagination | Click page 2 | Shows rows 51-100 |
| Row hover | Hover over row | Row highlights |
| Export CSV | Click export | Downloads CSV file |

### Charts
| Test | Steps | Expected |
|------|-------|----------|
| Dept chart load | Open page | Shows bar chart |
| Dept chart click | Click bar | Table filters to that dept |
| Earnings chart | Open page | Shows donut chart |
| Chart update | Change filter | Both charts update |

### Responsive
| Test | Viewport | Expected |
|------|----------|----------|
| Desktop | 1440px | Full layout |
| Tablet | 768px | Charts stack |
| Mobile | 375px | Single column, table scrolls |

## Performance Benchmarks

| Metric | Target | How to Test |
|--------|--------|-------------|
| Initial load | < 3s | Chrome DevTools Network |
| API response | < 200ms | curl with timing |
| Table sort | < 100ms | Manual observation |
| Search filter | < 100ms | Manual observation |
| Memory usage | < 100MB | Chrome DevTools Memory |

## Test Automation

### Python API Tests
```python
# tests/test_api.py
import requests
import pytest

BASE_URL = "http://localhost:8000"

def test_health():
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_employees_pagination():
    r = requests.get(f"{BASE_URL}/api/employees?year=2024&limit=10")
    data = r.json()
    assert len(data["data"]) == 10
    assert data["total"] > 20000

def test_employees_search():
    r = requests.get(f"{BASE_URL}/api/employees?year=2024&search=police&limit=50")
    data = r.json()
    # All results should contain "police" (case insensitive)
    for emp in data["data"]:
        assert "police" in emp["name"].lower() or "police" in (emp["title"] or "").lower()

def test_stats_totals():
    r = requests.get(f"{BASE_URL}/api/stats?year=2024")
    data = r.json()
    assert data["total_employees"] > 20000
    assert data["total_payroll"] > 1000000000  # > $1B

def test_earnings_breakdown_sums():
    r = requests.get(f"{BASE_URL}/api/earnings-breakdown?year=2024")
    data = r.json()
    total_pct = sum(data["percentages"].values())
    assert 99.0 <= total_pct <= 101.0  # Allow rounding error
```

### Run Tests
```bash
pip install pytest requests
pytest tests/test_api.py -v
```

## Production Verification

After deployment, run these checks:

```bash
# 1. SSL Certificate
curl -I https://bostonpayroll.adamlozo.com
# Verify: HTTP/2 200, valid SSL

# 2. API Health
curl https://bostonpayroll.adamlozo.com/api/health
# Verify: status healthy, database connected

# 3. Data Present
curl "https://bostonpayroll.adamlozo.com/api/stats?year=2024"
# Verify: total_employees > 20000

# 4. Frontend Loads
curl -s https://bostonpayroll.adamlozo.com | head -20
# Verify: HTML content returned
```

## Known Edge Cases

1. **Negative earnings**: Valid (corrections), should display correctly
2. **Empty department**: Some records have null department
3. **Special characters in names**: Apostrophes, hyphens common
4. **Very long titles**: Should truncate or wrap
5. **Zero total gross**: Valid (part-year employees)
