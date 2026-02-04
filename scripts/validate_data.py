import sys
from pathlib import Path
from tabulate import tabulate

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_db_connection

def validate_record_counts():
    """Verify record counts by year."""
    print("\n" + "="*60)
    print("VALIDATION: Record Counts by Year")
    print("="*60)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT year, COUNT(*) as count
                FROM payroll_earnings
                GROUP BY year
                ORDER BY year
            """)
            results = cur.fetchall()

            print(tabulate(results, headers=['Year', 'Count'], tablefmt='grid'))

            total = sum(row[1] for row in results)
            print(f"\nTotal records: {total:,}")

            # Expected ranges
            if len(results) != 5:
                print("[ERROR] Expected 5 years of data")
                return False

            if total < 100000:
                print("[WARNING] Total records less than expected (~100K)")
            else:
                print("[OK] Record counts look good")

    return True

def validate_no_duplicates():
    """Check for duplicate records."""
    print("\n" + "="*60)
    print("VALIDATION: Duplicate Check")
    print("="*60)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT year, name, department, title, COUNT(*) as count
                FROM payroll_earnings
                GROUP BY year, name, department, title
                HAVING COUNT(*) > 1
                LIMIT 10
            """)
            duplicates = cur.fetchall()

            if duplicates:
                print(f"[ERROR] Found {len(duplicates)} duplicate records")
                print(tabulate(duplicates, headers=['Year', 'Name', 'Dept', 'Title', 'Count']))
                return False
            else:
                print("[OK] No duplicates found")

    return True

def validate_departments():
    """Check department counts."""
    print("\n" + "="*60)
    print("VALIDATION: Top 10 Departments by Employee Count (2024)")
    print("="*60)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT department, COUNT(*) as employees
                FROM payroll_earnings
                WHERE year = 2024
                GROUP BY department
                ORDER BY employees DESC
                LIMIT 10
            """)
            results = cur.fetchall()

            print(tabulate(results, headers=['Department', 'Employees'], tablefmt='grid'))

            if not results:
                print("[ERROR] No departments found")
                return False
            else:
                print("[OK] Departments look reasonable")

    return True

def validate_earnings_totals():
    """Check total earnings by year."""
    print("\n" + "="*60)
    print("VALIDATION: Total Earnings by Year")
    print("="*60)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    year,
                    SUM(total_gross)::numeric(15,2) as total_earnings,
                    AVG(total_gross)::numeric(10,2) as avg_earnings
                FROM payroll_earnings
                GROUP BY year
                ORDER BY year
            """)
            results = cur.fetchall()

            # Format as currency
            formatted = [
                (row[0], f"${row[1]:,.2f}", f"${row[2]:,.2f}")
                for row in results
            ]

            print(tabulate(formatted, headers=['Year', 'Total Earnings', 'Avg Earnings'], tablefmt='grid'))
            print("[OK] Earnings totals calculated")

    return True

def validate_indexes():
    """Verify all indexes exist."""
    print("\n" + "="*60)
    print("VALIDATION: Index Check")
    print("="*60)

    expected_indexes = [
        'idx_payroll_year',
        'idx_payroll_department',
        'idx_payroll_total_gross',
        'idx_payroll_name_search',
        'idx_payroll_year_dept',
    ]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'payroll_earnings'
                AND indexname LIKE 'idx_payroll%'
            """)
            results = [row[0] for row in cur.fetchall()]

            missing = set(expected_indexes) - set(results)

            if missing:
                print(f"[ERROR] Missing indexes: {missing}")
                return False
            else:
                print(f"[OK] All {len(expected_indexes)} indexes exist")
                for idx in sorted(results):
                    print(f"  - {idx}")

    return True

def run_all_validations():
    """Run all validation checks."""
    print("\n" + "="*80)
    print("BOSTON PAYROLL DATA VALIDATION")
    print("="*80)

    checks = [
        validate_record_counts,
        validate_no_duplicates,
        validate_departments,
        validate_earnings_totals,
        validate_indexes,
    ]

    results = []
    for check in checks:
        try:
            passed = check()
            results.append((check.__name__, passed))
        except Exception as e:
            print(f"\n[ERROR] in {check.__name__}: {e}")
            results.append((check.__name__, False))

    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)

    for name, passed in results:
        status = "[OK] PASS" if passed else "[ERROR] FAIL"
        print(f"{status}: {name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n[SUCCESS] All validations passed! Data layer is ready.")
    else:
        print("\n[ERROR] Some validations failed. Review errors above.")

    return all_passed

if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)
