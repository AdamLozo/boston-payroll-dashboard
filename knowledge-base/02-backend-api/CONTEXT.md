# Backend API Context

## Overview
FastAPI backend serving JSON endpoints for the payroll dashboard. Follows same patterns as building permits dashboard.

## Endpoints

### GET /api/health
Health check endpoint for monitoring.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "total_records": 105234,
  "years_available": [2020, 2021, 2022, 2023, 2024]
}
```

### GET /api/employees
Main data endpoint with pagination, filtering, and sorting.

**Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| year | int | 2024 | Filter by year |
| department | str | null | Filter by department (exact match) |
| search | str | null | Search name, title (ILIKE) |
| sort_by | str | total_gross | Column to sort by |
| sort_order | str | desc | asc or desc |
| limit | int | 50 | Max records (max 5000) |
| offset | int | 0 | Pagination offset |

**Response**:
```json
{
  "data": [
    {
      "id": 1,
      "year": 2024,
      "name": "SMITH, JOHN",
      "department": "Boston Police Department",
      "title": "Police Officer",
      "regular": 95000.00,
      "retro": 0.00,
      "other": 5000.00,
      "overtime": 85000.00,
      "injured": 0.00,
      "detail": 45000.00,
      "quinn_education": 12000.00,
      "total_gross": 242000.00,
      "zip_code": "02127"
    }
  ],
  "total": 22456,
  "limit": 50,
  "offset": 0,
  "year": 2024
}
```

### GET /api/departments
List all departments with aggregated stats.

**Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| year | int | 2024 | Filter by year |

**Response**:
```json
{
  "departments": [
    {
      "name": "Boston Police Department",
      "employee_count": 2345,
      "total_earnings": 456789012.34,
      "avg_earnings": 194814.12,
      "total_overtime": 123456789.00,
      "total_detail": 98765432.10
    }
  ],
  "year": 2024
}
```

### GET /api/stats
Summary statistics for dashboard header.

**Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| year | int | 2024 | Filter by year |
| department | str | null | Optional department filter |

**Response**:
```json
{
  "year": 2024,
  "total_employees": 22456,
  "total_payroll": 2345678901.23,
  "avg_salary": 104500.12,
  "median_salary": 85000.00,
  "total_overtime": 345678901.23,
  "total_detail": 234567890.12,
  "top_department": "Boston Police Department",
  "top_department_total": 456789012.34
}
```

### GET /api/earnings-breakdown
Earnings composition by category.

**Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| year | int | 2024 | Filter by year |
| department | str | null | Optional department filter |

**Response**:
```json
{
  "year": 2024,
  "breakdown": {
    "regular": 1500000000.00,
    "overtime": 345678901.23,
    "detail": 234567890.12,
    "other": 265432109.88
  },
  "percentages": {
    "regular": 63.9,
    "overtime": 14.7,
    "detail": 10.0,
    "other": 11.4
  }
}
```

### GET /api/years
List available years.

**Response**:
```json
{
  "years": [2024, 2023, 2022, 2021, 2020],
  "default": 2024
}
```

### GET /api/export
Export filtered data as CSV.

**Parameters**: Same as /api/employees (without pagination)

**Response**: CSV file download

## Request/Response Models

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

class EmployeeListResponse(BaseModel):
    data: List[Employee]
    total: int
    limit: int
    offset: int
    year: int

class Department(BaseModel):
    name: str
    employee_count: int
    total_earnings: Decimal
    avg_earnings: Decimal
    total_overtime: Decimal
    total_detail: Decimal

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
```

## Error Handling

```python
from fastapi import HTTPException

# Standard error responses
400: {"detail": "Invalid year parameter"}
404: {"detail": "Department not found"}
500: {"detail": "Database connection error"}
```

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Static File Serving

```python
from fastapi.staticfiles import StaticFiles

# Serve frontend from /frontend directory
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

## Performance Targets

| Endpoint | Target | Max Records |
|----------|--------|-------------|
| /api/health | < 50ms | N/A |
| /api/employees | < 200ms | 5000 |
| /api/departments | < 100ms | N/A |
| /api/stats | < 100ms | N/A |
| /api/earnings-breakdown | < 100ms | N/A |

## Dependencies

```
fastapi==0.109.0
uvicorn==0.27.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic==2.5.0
```

## Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
PORT=8000
ENVIRONMENT=production
```
