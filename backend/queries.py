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
                    AVG(overtime) as avg_overtime,
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

            # Get prior year stats for comparison
            prior_year = year - 1
            prior_where_sql = "year = %s"
            prior_params = [prior_year]

            if department:
                prior_where_sql += " AND department = %s"
                prior_params.append(department)

            prior_sql = f"""
                SELECT
                    COUNT(*) as total_employees,
                    SUM(total_gross) as total_payroll,
                    AVG(total_gross) as avg_salary,
                    SUM(overtime) as total_overtime
                FROM payroll_earnings
                WHERE {prior_where_sql}
            """
            cur.execute(prior_sql, prior_params)
            prior_stats = cur.fetchone()

            if prior_stats and prior_stats['total_employees']:
                stats['prior_year_employees'] = prior_stats['total_employees']
                stats['prior_year_payroll'] = prior_stats['total_payroll']
                stats['prior_year_avg_salary'] = prior_stats['avg_salary']
                stats['prior_year_overtime'] = prior_stats['total_overtime']
            else:
                stats['prior_year_employees'] = None
                stats['prior_year_payroll'] = None
                stats['prior_year_avg_salary'] = None
                stats['prior_year_overtime'] = None

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
