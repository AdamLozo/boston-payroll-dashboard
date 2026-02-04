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
    avg_overtime: Decimal
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
    prior_year_employees: Optional[int]
    prior_year_payroll: Optional[Decimal]
    prior_year_avg_salary: Optional[Decimal]
    prior_year_overtime: Optional[Decimal]

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
