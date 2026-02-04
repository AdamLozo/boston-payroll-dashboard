# Backend API Implementation Checklist

## Prerequisites
- [ ] Phase 1 (Data Layer) complete
- [ ] Database has ~100K records loaded
- [ ] Virtual environment active

## Tasks

### Task 1: Project Setup
**Files**: `backend/__init__.py`, `backend/config.py`, `requirements.txt`
**Time**: 5 minutes

- [ ] Create backend directory structure
- [ ] Create config.py with settings
- [ ] Create requirements.txt
- [ ] Install dependencies

**Verification**:
```bash
pip install -r requirements.txt
python -c "from backend.config import settings; print(settings.DATABASE_URL[:20])"
```

### Task 2: Database Connection Module
**Files**: `backend/database.py`
**Time**: 10 minutes

- [ ] Create connection pool
- [ ] Create context manager
- [ ] Test connection

**Verification**:
```python
from backend.database import get_db
with get_db() as conn:
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("Connected!")
```

### Task 3: Pydantic Models
**Files**: `backend/models.py`
**Time**: 10 minutes

- [ ] Create Employee model
- [ ] Create EmployeeListResponse model
- [ ] Create Department model
- [ ] Create Stats model
- [ ] Create EarningsBreakdown model

**Verification**:
```python
from backend.models import Employee
emp = Employee(id=1, year=2024, name="Test", ...)
print(emp.model_dump_json())
```

### Task 4: Health Endpoint
**Files**: `backend/main.py`
**Time**: 5 minutes

- [ ] Create FastAPI app
- [ ] Implement /api/health
- [ ] Test endpoint

**Verification**:
```bash
uvicorn backend.main:app --reload &
curl http://localhost:8000/api/health
# Should return JSON with status: healthy
```

### Task 5: Years Endpoint
**Files**: `backend/main.py`
**Time**: 5 minutes

- [ ] Implement /api/years
- [ ] Query distinct years from database

**Verification**:
```bash
curl http://localhost:8000/api/years
# Should return: {"years": [2024, 2023, 2022, 2021, 2020], "default": 2024}
```

### Task 6: Employees Endpoint
**Files**: `backend/main.py`
**Time**: 20 minutes

- [ ] Implement /api/employees with all parameters
- [ ] Add year filter
- [ ] Add department filter
- [ ] Add search filter (ILIKE on name, title)
- [ ] Add sorting
- [ ] Add pagination
- [ ] Add total count

**Verification**:
```bash
# Basic query
curl "http://localhost:8000/api/employees?year=2024&limit=5"

# With filters
curl "http://localhost:8000/api/employees?year=2024&department=Boston%20Police%20Department&limit=5"

# With search
curl "http://localhost:8000/api/employees?year=2024&search=smith&limit=5"

# With sorting
curl "http://localhost:8000/api/employees?year=2024&sort_by=overtime&sort_order=desc&limit=5"
```

### Task 7: Departments Endpoint
**Files**: `backend/main.py`
**Time**: 10 minutes

- [ ] Implement /api/departments
- [ ] Aggregate by department
- [ ] Include all stats (count, totals, averages)

**Verification**:
```bash
curl "http://localhost:8000/api/departments?year=2024"
# Should return list of departments with stats
```

### Task 8: Stats Endpoint
**Files**: `backend/main.py`
**Time**: 10 minutes

- [ ] Implement /api/stats
- [ ] Calculate totals, averages
- [ ] Calculate median (requires window function or app logic)
- [ ] Find top department

**Verification**:
```bash
curl "http://localhost:8000/api/stats?year=2024"
# Should return summary statistics

curl "http://localhost:8000/api/stats?year=2024&department=Boston%20Fire%20Department"
# Should return filtered statistics
```

### Task 9: Earnings Breakdown Endpoint
**Files**: `backend/main.py`
**Time**: 10 minutes

- [ ] Implement /api/earnings-breakdown
- [ ] Sum by category
- [ ] Calculate percentages

**Verification**:
```bash
curl "http://localhost:8000/api/earnings-breakdown?year=2024"
# Should return breakdown with amounts and percentages
```

### Task 10: CORS and Static Files
**Files**: `backend/main.py`
**Time**: 5 minutes

- [ ] Add CORS middleware
- [ ] Mount static files directory
- [ ] Create placeholder index.html

**Verification**:
```bash
curl http://localhost:8000/
# Should return index.html content
```

### Task 11: Error Handling
**Files**: `backend/main.py`
**Time**: 5 minutes

- [ ] Add exception handlers
- [ ] Handle database errors gracefully
- [ ] Return proper HTTP status codes

**Verification**:
```bash
curl "http://localhost:8000/api/employees?year=invalid"
# Should return 422 with validation error

curl "http://localhost:8000/api/notfound"
# Should return 404
```

## Completion Criteria

- [ ] All 7 endpoints working
- [ ] Response times under targets
- [ ] Error handling complete
- [ ] CORS enabled
- [ ] Static file serving works

## API Test Script

Create `tests/test_api.py`:
```python
import requests

BASE = "http://localhost:8000"

def test_health():
    r = requests.get(f"{BASE}/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_years():
    r = requests.get(f"{BASE}/api/years")
    assert r.status_code == 200
    assert 2024 in r.json()["years"]

def test_employees():
    r = requests.get(f"{BASE}/api/employees?year=2024&limit=10")
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]) <= 10
    assert data["total"] > 0

def test_departments():
    r = requests.get(f"{BASE}/api/departments?year=2024")
    assert r.status_code == 200
    assert len(r.json()["departments"]) > 0

def test_stats():
    r = requests.get(f"{BASE}/api/stats?year=2024")
    assert r.status_code == 200
    assert r.json()["total_employees"] > 0

def test_earnings_breakdown():
    r = requests.get(f"{BASE}/api/earnings-breakdown?year=2024")
    assert r.status_code == 200
    assert "regular" in r.json()["breakdown"]

if __name__ == "__main__":
    test_health()
    test_years()
    test_employees()
    test_departments()
    test_stats()
    test_earnings_breakdown()
    print("All tests passed!")
```

## Handoff to Phase 3

After completing this phase:
1. API is running and all endpoints work
2. Test script passes
3. Ready for frontend integration

```bash
# Start server for Phase 3
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
