# Phase 2: Backend API Implementation Plan

> **For Claude:** Use executing-plans skill to implement this plan task-by-task.

## Overview
Build FastAPI backend with JSON endpoints for the Boston Payroll Dashboard. Provides employee search, department aggregations, summary statistics, and earnings breakdown data.

## Prerequisites
- [x] Phase 1 complete (database with 118,931 records)
- [x] Database connection module working
- [ ] FastAPI and dependencies installed

## Tasks

### Task 1: Create FastAPI Application Structure
**Files:**
- `backend/main.py`
- `backend/models.py`
- `backend/queries.py`

**Implementation:**

Create `backend/models.py`:
```python
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

class Employee(BaseModel):
    id: int
    year: int
    name: str
    department: Optional[str]
    title: Optional[str]
    regular: Decimal
    retro: Decimal
    other: Decimal
    overtime: Decimal
    injured: Decimal
    detail: Decimal
    quinn_education: Decimal
    total_gross: Decimal
    zip_code: Optional[str]

    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    data: List[Employee]
    total: int
    limit: int
    offset: int
    year: int

class DepartmentStats(BaseModel):
    name: str
    employee_count: int
    total_earnings: Decimal
    avg_earnings: Decimal
    total_overtime: Decimal
    total_detail: Decimal

class DepartmentsResponse(BaseModel):
    departments: List[DepartmentStats]
    year: int

class Stats(BaseModel):
    year: int
    total_employees: int
    total_payroll: Decimal
    avg_salary: Decimal
    median_salary: Decimal
    total_overtime: Decimal
    total_detail: Decimal
    top_department: str
    top_department_total: Decimal

class EarningsBreakdown(BaseModel):
    year: int
    breakdown: dict  # {regular: amount, overtime: amount, ...}
    percentages: dict  # {regular: %, overtime: %, ...}

class YearsResponse(BaseModel):
    years: List[int]
    default: int

class HealthResponse(BaseModel):
    status: str
    database: str
    total_records: int
    years_available: List[int]
```

Create `backend/queries.py`:
```python
from typing import Optional, List, Dict, Any
from psycopg2.extras import RealDictCursor
from backend.database import get_db_connection

def get_employees(
    year: int = 2024,
    department: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "total_gross",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0
) -> tuple[List[Dict[str, Any]], int]:
    """Get employees with filters, sorting, and pagination."""

    # Validate inputs
    valid_sort_columns = ['name', 'department', 'title', 'total_gross', 'overtime', 'regular']
    if sort_by not in valid_sort_columns:
        sort_by = 'total_gross'

    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'

    if limit > 5000:
        limit = 5000

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Build WHERE clause
            where_clauses = ["year = %s"]
            params = [year]

            if department:
                where_clauses.append("department = %s")
                params.append(department)

            if search:
                where_clauses.append("(name ILIKE %s OR title ILIKE %s)")
                search_param = f"%{search}%"
                params.extend([search_param, search_param])

            where_sql = " AND ".join(where_clauses)

            # Get total count
            count_sql = f"SELECT COUNT(*) FROM payroll_earnings WHERE {where_sql}"
            cur.execute(count_sql, params)
            total = cur.fetchone()['count']

            # Get data
            data_sql = f"""
                SELECT
                    id, year, name, department, title,
                    regular, retro, other, overtime, injured, detail,
                    quinn_education, total_gross, zip_code
                FROM payroll_earnings
                WHERE {where_sql}
                ORDER BY {sort_by} {sort_order}
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            cur.execute(data_sql, params)
            data = cur.fetchall()

            return [dict(row) for row in data], total

def get_departments(year: int = 2024) -> List[Dict[str, Any]]:
    """Get department aggregations."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = """
                SELECT
                    department as name,
                    COUNT(*) as employee_count,
                    SUM(total_gross) as total_earnings,
                    AVG(total_gross) as avg_earnings,
                    SUM(overtime) as total_overtime,
                    SUM(detail) as total_detail
                FROM payroll_earnings
                WHERE year = %s AND department IS NOT NULL AND department != ''
                GROUP BY department
                ORDER BY total_earnings DESC
            """
            cur.execute(sql, (year,))
            return [dict(row) for row in cur.fetchall()]

def get_stats(year: int = 2024, department: Optional[str] = None) -> Dict[str, Any]:
    """Get summary statistics."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Build WHERE clause
            where_sql = "year = %s"
            params = [year]

            if department:
                where_sql += " AND department = %s"
                params.append(department)

            # Main stats
            sql = f"""
                SELECT
                    COUNT(*) as total_employees,
                    SUM(total_gross) as total_payroll,
                    AVG(total_gross) as avg_salary,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_gross) as median_salary,
                    SUM(overtime) as total_overtime,
                    SUM(detail) as total_detail
                FROM payroll_earnings
                WHERE {where_sql}
            """
            cur.execute(sql, params)
            stats = dict(cur.fetchone())

            # Top department (if not filtering by department)
            if not department:
                top_dept_sql = """
                    SELECT
                        department as name,
                        SUM(total_gross) as total
                    FROM payroll_earnings
                    WHERE year = %s AND department IS NOT NULL AND department != ''
                    GROUP BY department
                    ORDER BY total DESC
                    LIMIT 1
                """
                cur.execute(top_dept_sql, (year,))
                top_dept = cur.fetchone()

                if top_dept:
                    stats['top_department'] = top_dept['name']
                    stats['top_department_total'] = top_dept['total']
                else:
                    stats['top_department'] = None
                    stats['top_department_total'] = 0
            else:
                stats['top_department'] = department
                stats['top_department_total'] = stats['total_payroll']

            stats['year'] = year
            return stats

def get_earnings_breakdown(year: int = 2024, department: Optional[str] = None) -> Dict[str, Any]:
    """Get earnings composition breakdown."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            where_sql = "year = %s"
            params = [year]

            if department:
                where_sql += " AND department = %s"
                params.append(department)

            sql = f"""
                SELECT
                    SUM(regular) as regular,
                    SUM(overtime) as overtime,
                    SUM(detail) as detail,
                    SUM(retro) as retro,
                    SUM(other) as other,
                    SUM(injured) as injured,
                    SUM(quinn_education) as quinn_education
                FROM payroll_earnings
                WHERE {where_sql}
            """
            cur.execute(sql, params)
            breakdown = dict(cur.fetchone())

            # Calculate total
            total = sum(float(v) for v in breakdown.values() if v)

            # Calculate percentages
            percentages = {}
            if total > 0:
                for key, value in breakdown.items():
                    if value:
                        percentages[key] = round((float(value) / total) * 100, 1)
                    else:
                        percentages[key] = 0.0

            return {
                'year': year,
                'breakdown': breakdown,
                'percentages': percentages
            }

def get_available_years() -> List[int]:
    """Get list of available years in database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT year
                FROM payroll_earnings
                ORDER BY year DESC
            """)
            return [row[0] for row in cur.fetchall()]

def get_health_check() -> Dict[str, Any]:
    """Health check with database stats."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM payroll_earnings")
                total = cur.fetchone()[0]

                years = get_available_years()

                return {
                    'status': 'healthy',
                    'database': 'connected',
                    'total_records': total,
                    'years_available': years
                }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e),
            'total_records': 0,
            'years_available': []
        }
```

Create `backend/main.py`:
```python
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import csv

from backend.models import (
    EmployeeListResponse,
    DepartmentsResponse,
    Stats,
    EarningsBreakdown,
    YearsResponse,
    HealthResponse
)
from backend.queries import (
    get_employees,
    get_departments,
    get_stats,
    get_earnings_breakdown,
    get_available_years,
    get_health_check
)

app = FastAPI(
    title="Boston Payroll API",
    description="API for Boston city employee earnings data (2020-2024)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
def health():
    """Health check endpoint."""
    return get_health_check()

@app.get("/api/employees", response_model=EmployeeListResponse)
def list_employees(
    year: int = Query(default=2024, ge=2020, le=2024),
    department: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="total_gross"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=50, ge=1, le=5000),
    offset: int = Query(default=0, ge=0)
):
    """Get employees with filters and pagination."""
    try:
        data, total = get_employees(
            year=year,
            department=department,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )

        return EmployeeListResponse(
            data=data,
            total=total,
            limit=limit,
            offset=offset,
            year=year
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/departments", response_model=DepartmentsResponse)
def list_departments(
    year: int = Query(default=2024, ge=2020, le=2024)
):
    """Get department aggregations."""
    try:
        departments = get_departments(year=year)
        return DepartmentsResponse(
            departments=departments,
            year=year
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/stats", response_model=Stats)
def get_statistics(
    year: int = Query(default=2024, ge=2020, le=2024),
    department: Optional[str] = Query(default=None)
):
    """Get summary statistics."""
    try:
        return get_stats(year=year, department=department)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/earnings-breakdown", response_model=EarningsBreakdown)
def earnings_breakdown(
    year: int = Query(default=2024, ge=2020, le=2024),
    department: Optional[str] = Query(default=None)
):
    """Get earnings composition breakdown."""
    try:
        return get_earnings_breakdown(year=year, department=department)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/years", response_model=YearsResponse)
def list_years():
    """Get available years."""
    try:
        years = get_available_years()
        return YearsResponse(
            years=years,
            default=years[0] if years else 2024
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/export")
def export_employees(
    year: int = Query(default=2024, ge=2020, le=2024),
    department: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None)
):
    """Export filtered employees as CSV."""
    try:
        # Get all matching records (no pagination)
        data, _ = get_employees(
            year=year,
            department=department,
            search=search,
            sort_by="name",
            sort_order="asc",
            limit=5000,
            offset=0
        )

        # Create CSV in memory
        output = io.StringIO()
        if data:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        # Return as streaming response
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=boston_payroll_{year}.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Test Commands:**
```bash
# Start the server
cd ~/OneDrive/Claude/Projects/boston-payroll-dashboard
python -m backend.main

# In another terminal, test endpoints
curl http://localhost:8000/api/health
curl "http://localhost:8000/api/employees?year=2024&limit=5"
curl http://localhost:8000/api/departments?year=2024
curl http://localhost:8000/api/stats?year=2024
```

**Expected Outcome:**
- FastAPI server running on port 8000
- All endpoints return valid JSON
- Health check shows database connected

---

### Task 2: Add Update requirements.txt
**Files:** `requirements.txt`

**Implementation:**

Update `requirements.txt` to include all FastAPI dependencies:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pandas==2.1.3
requests==2.31.0
tabulate==0.9.0
openpyxl==3.1.5
pydantic==2.5.0
```

**Test Command:**
```bash
pip install -r requirements.txt
```

**Expected Outcome:**
- All dependencies installed
- No version conflicts

---

### Task 3: Test All API Endpoints
**Files:** `scripts/test_api.py`

**Implementation:**

Create `scripts/test_api.py`:
```python
import requests
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*60)
    print("Testing /api/health")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert data['status'] == 'healthy', "Database not healthy"
    assert data['total_records'] > 100000, "Not enough records"
    assert len(data['years_available']) == 5, "Should have 5 years"

    print("[OK] Health check passed")
    print(f"  Records: {data['total_records']:,}")
    print(f"  Years: {data['years_available']}")

def test_employees():
    """Test employees endpoint."""
    print("\n" + "="*60)
    print("Testing /api/employees")
    print("="*60)

    # Test basic query
    response = requests.get(f"{BASE_URL}/api/employees?year=2024&limit=5")
    assert response.status_code == 200

    data = response.json()
    assert len(data['data']) == 5, "Should return 5 records"
    assert data['year'] == 2024
    assert data['total'] > 20000, "Should have ~25K records for 2024"

    print(f"[OK] Basic query passed")
    print(f"  Records returned: {len(data['data'])}")
    print(f"  Total available: {data['total']:,}")

    # Test search
    response = requests.get(f"{BASE_URL}/api/employees?year=2024&search=police&limit=10")
    assert response.status_code == 200
    data = response.json()
    print(f"[OK] Search query passed (found {len(data['data'])} records)")

    # Test department filter
    response = requests.get(f"{BASE_URL}/api/employees?year=2024&department=Boston+Police+Department&limit=10")
    assert response.status_code == 200
    data = response.json()
    print(f"[OK] Department filter passed ({data['total']:,} in department)")

def test_departments():
    """Test departments endpoint."""
    print("\n" + "="*60)
    print("Testing /api/departments")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/departments?year=2024")
    assert response.status_code == 200

    data = response.json()
    assert len(data['departments']) > 50, "Should have 50+ departments"
    assert data['year'] == 2024

    # Check top department
    top_dept = data['departments'][0]
    print(f"[OK] Departments endpoint passed")
    print(f"  Total departments: {len(data['departments'])}")
    print(f"  Top department: {top_dept['name']}")
    print(f"    Employees: {top_dept['employee_count']:,}")
    print(f"    Total earnings: ${top_dept['total_earnings']:,.2f}")

def test_stats():
    """Test stats endpoint."""
    print("\n" + "="*60)
    print("Testing /api/stats")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/stats?year=2024")
    assert response.status_code == 200

    data = response.json()
    assert data['year'] == 2024
    assert data['total_employees'] > 20000
    assert data['total_payroll'] > 2000000000  # $2B+

    print(f"[OK] Stats endpoint passed")
    print(f"  Total employees: {data['total_employees']:,}")
    print(f"  Total payroll: ${data['total_payroll']:,.2f}")
    print(f"  Avg salary: ${data['avg_salary']:,.2f}")
    print(f"  Median salary: ${data['median_salary']:,.2f}")

def test_earnings_breakdown():
    """Test earnings breakdown endpoint."""
    print("\n" + "="*60)
    print("Testing /api/earnings-breakdown")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/earnings-breakdown?year=2024")
    assert response.status_code == 200

    data = response.json()
    assert data['year'] == 2024
    assert 'breakdown' in data
    assert 'percentages' in data

    # Check percentages add up to ~100%
    total_pct = sum(data['percentages'].values())
    assert 99 <= total_pct <= 101, f"Percentages should add to ~100%, got {total_pct}"

    print(f"[OK] Earnings breakdown passed")
    print(f"  Regular: {data['percentages']['regular']:.1f}%")
    print(f"  Overtime: {data['percentages']['overtime']:.1f}%")
    print(f"  Detail: {data['percentages']['detail']:.1f}%")

def test_years():
    """Test years endpoint."""
    print("\n" + "="*60)
    print("Testing /api/years")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/years")
    assert response.status_code == 200

    data = response.json()
    assert len(data['years']) == 5
    assert data['default'] == 2024
    assert data['years'] == [2024, 2023, 2022, 2021, 2020]

    print(f"[OK] Years endpoint passed")
    print(f"  Available: {data['years']}")

def run_all_tests():
    """Run all API tests."""
    print("\n" + "="*80)
    print("BOSTON PAYROLL API TEST SUITE")
    print("="*80)

    try:
        test_health()
        test_employees()
        test_departments()
        test_stats()
        test_earnings_breakdown()
        test_years()

        print("\n" + "="*80)
        print("[SUCCESS] All API tests passed!")
        print("="*80)
        return True
    except AssertionError as e:
        print(f"\n[ERROR] Test failed: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Could not connect to {BASE_URL}")
        print("Make sure the API server is running: python -m backend.main")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

**Test Commands:**
```bash
# Start server in one terminal
python -m backend.main

# Run tests in another terminal
python scripts/test_api.py
```

**Expected Outcome:**
- All tests pass
- API endpoints return correct data
- Response times under target

---

### Task 4: Add API Documentation
**Files:** `docs/API.md`

**Implementation:**

Create `docs/API.md`:
```markdown
# Boston Payroll API Documentation

Base URL: `http://localhost:8000` (development)
Production: `https://bostonpayroll.adamlozo.com`

## Authentication

No authentication required (public data).

## Endpoints

### GET /api/health

Health check endpoint.

**Response:**
\`\`\`json
{
  "status": "healthy",
  "database": "connected",
  "total_records": 118931,
  "years_available": [2024, 2023, 2022, 2021, 2020]
}
\`\`\`

### GET /api/employees

Get employee list with filters.

**Query Parameters:**
- `year` (int, default: 2024): Filter by year (2020-2024)
- `department` (string, optional): Exact department name
- `search` (string, optional): Search name or title (case-insensitive)
- `sort_by` (string, default: "total_gross"): Column to sort by
- `sort_order` (string, default: "desc"): "asc" or "desc"
- `limit` (int, default: 50, max: 5000): Records per page
- `offset` (int, default: 0): Pagination offset

**Example:**
\`\`\`bash
curl "http://localhost:8000/api/employees?year=2024&search=police&limit=10"
\`\`\`

### GET /api/departments

Get department aggregations.

**Query Parameters:**
- `year` (int, default: 2024): Filter by year

**Example:**
\`\`\`bash
curl "http://localhost:8000/api/departments?year=2024"
\`\`\`

### GET /api/stats

Get summary statistics.

**Query Parameters:**
- `year` (int, default: 2024): Filter by year
- `department` (string, optional): Filter by department

**Example:**
\`\`\`bash
curl "http://localhost:8000/api/stats?year=2024"
\`\`\`

### GET /api/earnings-breakdown

Get earnings composition.

**Query Parameters:**
- `year` (int, default: 2024): Filter by year
- `department` (string, optional): Filter by department

**Example:**
\`\`\`bash
curl "http://localhost:8000/api/earnings-breakdown?year=2024"
\`\`\`

### GET /api/years

Get available years.

**Example:**
\`\`\`bash
curl "http://localhost:8000/api/years"
\`\`\`

### GET /api/export

Export filtered data as CSV.

**Query Parameters:** Same as `/api/employees` (without pagination)

**Example:**
\`\`\`bash
curl "http://localhost:8000/api/export?year=2024&department=Boston+Police+Department" -o payroll.csv
\`\`\`

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Database error

Error response format:
\`\`\`json
{
  "detail": "Error message"
}
\`\`\`

## Performance

Target response times:
- `/api/health`: < 50ms
- `/api/employees`: < 200ms (up to 5000 records)
- `/api/departments`: < 100ms
- `/api/stats`: < 100ms
- `/api/earnings-breakdown`: < 100ms
```

**Expected Outcome:**
- Complete API documentation
- Examples for all endpoints
- Ready for frontend integration

---

## Completion Criteria

- [ ] FastAPI server running on port 8000
- [ ] All 7 endpoints implemented and tested
- [ ] Response models match specification
- [ ] Query parameters validated
- [ ] Error handling implemented
- [ ] CORS enabled for frontend
- [ ] All tests passing
- [ ] API documentation complete

## Handoff to Phase 3

After completing Phase 2:
- API serving JSON data at http://localhost:8000
- All endpoints tested and documented
- Ready to build frontend UI that consumes the API

## Rollback Plan

If something goes wrong, the data layer (Phase 1) is unaffected. Simply stop the server and debug backend code.

## Notes

- Use existing database connection from Phase 1
- Follow FastAPI best practices
- Keep queries efficient (use indexes)
- Add caching later if needed for performance
