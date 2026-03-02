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
    description="API for Boston city employee earnings data (2020-2025)",
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

@app.get("/")
def root():
    """Root endpoint for health checks."""
    return {"status": "ok", "service": "Boston Payroll API"}

@app.get("/health")
def health_simple():
    """Simple health check endpoint for Render."""
    return {"status": "healthy"}

@app.get("/api/health", response_model=HealthResponse)
def health():
    """Health check endpoint."""
    return get_health_check()

@app.get("/api/employees", response_model=EmployeeListResponse)
def list_employees(
    year: int = Query(default=2025, ge=2020, le=2025),
    department: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    earnings_type: Optional[str] = Query(default=None),
    sort_by: str = Query(default="total_gross"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=50, ge=1, le=30000),
    offset: int = Query(default=0, ge=0)
):
    """Get employees with filters and pagination."""
    try:
        data, total = get_employees(
            year=year,
            department=department,
            search=search,
            earnings_type=earnings_type,
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
    year: int = Query(default=2025, ge=2020, le=2025)
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
    year: int = Query(default=2025, ge=2020, le=2025),
    department: Optional[str] = Query(default=None)
):
    """Get summary statistics."""
    try:
        return get_stats(year=year, department=department)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/earnings-breakdown", response_model=EarningsBreakdown)
def earnings_breakdown(
    year: int = Query(default=2025, ge=2020, le=2025),
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
    year: int = Query(default=2025, ge=2020, le=2025),
    department: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    earnings_type: Optional[str] = Query(default=None)
):
    """Export filtered employees as CSV."""
    try:
        # Get all matching records (no pagination)
        data, _ = get_employees(
            year=year,
            department=department,
            search=search,
            earnings_type=earnings_type,
            sort_by="name",
            sort_order="asc",
            limit=30000,
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
