# Phase 1: Data Layer Implementation Plan

> **For Claude:** Use executing-plans skill to implement this plan task-by-task.

## Overview
Build the data layer for Boston Payroll Dashboard: PostgreSQL schema, CSV data loader, and database access patterns. This uses the shared Render PostgreSQL database (same as building permits and restaurants dashboards).

## Prerequisites
- [x] Design document reviewed (`knowledge-base/01-data-layer/CONTEXT.md`)
- [x] Shared DATABASE_URL from existing dashboards
- [ ] Python 3.9+ installed
- [ ] Project directory exists

## Database Connection Info
Use the same DATABASE_URL environment variable from your existing dashboards (building permits/restaurants).

## Tasks

### Task 1: Initialize Project Structure
**Files:**
- `backend/database.py`
- `backend/config.py`
- `scripts/load_data.py`
- `scripts/validate_data.py`
- `requirements.txt`
- `.env.example`
- `.gitignore`

**Implementation:**

Create `requirements.txt`:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pandas==2.1.3
requests==2.31.0
```

Create `.env.example`:
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Create `.gitignore`:
```
.env
__pycache__/
*.pyc
.venv/
venv/
*.log
.DS_Store
/tmp/
```

Create `backend/config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")
```

**Expected Outcome:**
- Project structure created
- Dependencies defined
- Configuration module ready

---

### Task 2: Create Database Schema Module
**Files:** `backend/database.py`

**Implementation:**

```python
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from backend.config import DATABASE_URL

# Connection pool
connection_pool = None

def init_pool():
    """Initialize connection pool."""
    global connection_pool
    if connection_pool is None:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL
        )
    return connection_pool

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    pool = init_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        pool.putconn(conn)

def create_schema():
    """Create payroll_earnings table and indexes."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Create table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS payroll_earnings (
                    id SERIAL PRIMARY KEY,

                    -- Year identifier
                    year INTEGER NOT NULL,

                    -- Employee info
                    name VARCHAR(255) NOT NULL,
                    department VARCHAR(255),
                    title VARCHAR(255),

                    -- Earnings breakdown (in dollars, can be negative for corrections)
                    regular DECIMAL(12,2) DEFAULT 0,
                    retro DECIMAL(12,2) DEFAULT 0,
                    other DECIMAL(12,2) DEFAULT 0,
                    overtime DECIMAL(12,2) DEFAULT 0,
                    injured DECIMAL(12,2) DEFAULT 0,
                    detail DECIMAL(12,2) DEFAULT 0,
                    quinn_education DECIMAL(12,2) DEFAULT 0,
                    total_gross DECIMAL(12,2) DEFAULT 0,

                    -- Location
                    zip_code VARCHAR(10),

                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    -- Composite unique constraint
                    UNIQUE(year, name, department, title)
                );
            """)

            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_payroll_year ON payroll_earnings(year)",
                "CREATE INDEX IF NOT EXISTS idx_payroll_department ON payroll_earnings(department)",
                "CREATE INDEX IF NOT EXISTS idx_payroll_total_gross ON payroll_earnings(total_gross DESC)",
                "CREATE INDEX IF NOT EXISTS idx_payroll_name_search ON payroll_earnings(name varchar_pattern_ops)",
                "CREATE INDEX IF NOT EXISTS idx_payroll_year_dept ON payroll_earnings(year, department)",
            ]

            for index_sql in indexes:
                cur.execute(index_sql)

            print("✓ Schema created successfully")

            # Verify table exists
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'payroll_earnings'
            """)
            if cur.fetchone():
                print("✓ Table 'payroll_earnings' verified")
            else:
                raise Exception("Table creation failed")

if __name__ == "__main__":
    create_schema()
```

**Test Command:**
```bash
cd ~/OneDrive/Claude/Projects/boston-payroll-dashboard
python -m backend.database
```

**Expected Outcome:**
- Table `payroll_earnings` created in shared database
- All 5 indexes created
- Verification messages printed

---

### Task 3: Build CSV Download and Parser
**Files:** `scripts/load_data.py`

**Implementation:**

```python
import os
import sys
import requests
import pandas as pd
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_db_connection

# Resource IDs for each year
RESOURCE_IDS = {
    2024: "579a4be3-9ca7-4183-bc95-7d67ee715b6d",
    2023: "6b3c5333-1dcb-4b3d-9cd7-6a03fb526da7",
    2022: "63ac638b-36c4-487d-9453-1d83eb5090d2",
    2021: "ec5aaf93-1509-4641-9310-28e62e028457",
    2020: "e2e2c23a-6fc7-4456-8751-5321d8aa869b",
}

CSV_URL_TEMPLATE = "https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/{resource_id}/download"

def download_csv(year, output_dir="/tmp"):
    """Download CSV for a specific year."""
    resource_id = RESOURCE_IDS.get(year)
    if not resource_id:
        raise ValueError(f"No resource ID for year {year}")

    url = CSV_URL_TEMPLATE.format(resource_id=resource_id)
    output_path = Path(output_dir) / f"boston_earnings_{year}.csv"

    print(f"Downloading {year} data from Analyze Boston...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    output_path.write_bytes(response.content)
    print(f"✓ Downloaded to {output_path} ({len(response.content)} bytes)")

    return str(output_path)

def parse_csv(csv_path, year):
    """Parse CSV and transform to database-ready format."""
    print(f"Parsing {csv_path}...")

    # Read CSV with UTF-8 encoding
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    # Column mapping (CSV -> database)
    column_map = {
        'NAME': 'name',
        'DEPARTMENT_NAME': 'department',
        'TITLE': 'title',
        'REGULAR': 'regular',
        'RETRO': 'retro',
        'OTHER': 'other',
        'OVERTIME': 'overtime',
        'INJURED': 'injured',
        'DETAIL': 'detail',
        'QUINN_EDUCATION': 'quinn_education',
        'TOTAL GROSS': 'total_gross',
        'POSTAL': 'zip_code',
    }

    # Rename columns
    df = df.rename(columns=column_map)

    # Add year column
    df['year'] = year

    # Clean text fields
    text_fields = ['name', 'department', 'title', 'zip_code']
    for field in text_fields:
        if field in df.columns:
            df[field] = df[field].fillna('').astype(str).str.strip()

    # Clean numeric fields (remove commas, convert to float)
    numeric_fields = ['regular', 'retro', 'other', 'overtime', 'injured',
                      'detail', 'quinn_education', 'total_gross']
    for field in numeric_fields:
        if field in df.columns:
            # Remove commas and convert to numeric
            df[field] = pd.to_numeric(
                df[field].astype(str).str.replace(',', '').str.replace('$', ''),
                errors='coerce'
            ).fillna(0)

    # Select only columns we need
    columns_to_keep = ['year', 'name', 'department', 'title'] + numeric_fields + ['zip_code']
    df = df[[col for col in columns_to_keep if col in df.columns]]

    print(f"✓ Parsed {len(df)} records")
    return df

def bulk_insert(df, year):
    """Insert DataFrame into database using bulk insert."""
    print(f"Inserting {len(df)} records for year {year}...")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Use executemany for bulk insert
            records = df.to_dict('records')

            insert_sql = """
                INSERT INTO payroll_earnings (
                    year, name, department, title,
                    regular, retro, other, overtime, injured, detail,
                    quinn_education, total_gross, zip_code
                ) VALUES (
                    %(year)s, %(name)s, %(department)s, %(title)s,
                    %(regular)s, %(retro)s, %(other)s, %(overtime)s,
                    %(injured)s, %(detail)s, %(quinn_education)s,
                    %(total_gross)s, %(zip_code)s
                )
                ON CONFLICT (year, name, department, title) DO UPDATE SET
                    regular = EXCLUDED.regular,
                    retro = EXCLUDED.retro,
                    other = EXCLUDED.other,
                    overtime = EXCLUDED.overtime,
                    injured = EXCLUDED.injured,
                    detail = EXCLUDED.detail,
                    quinn_education = EXCLUDED.quinn_education,
                    total_gross = EXCLUDED.total_gross,
                    zip_code = EXCLUDED.zip_code
            """

            cur.executemany(insert_sql, records)
            print(f"✓ Inserted {len(records)} records for {year}")

def load_year(year):
    """Download, parse, and load data for a specific year."""
    print(f"\n{'='*60}")
    print(f"Loading data for year {year}")
    print(f"{'='*60}")

    # Download CSV
    csv_path = download_csv(year)

    # Parse CSV
    df = parse_csv(csv_path, year)

    # Insert into database
    bulk_insert(df, year)

    # Cleanup temp file
    Path(csv_path).unlink()
    print(f"✓ Cleaned up temp file")

def load_all_years():
    """Load data for all years (2020-2024)."""
    for year in sorted(RESOURCE_IDS.keys()):
        try:
            load_year(year)
        except Exception as e:
            print(f"✗ Error loading year {year}: {e}")
            raise

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Load Boston payroll data')
    parser.add_argument('--year', type=int, help='Load specific year')
    parser.add_argument('--all', action='store_true', help='Load all years')

    args = parser.parse_args()

    if args.year:
        load_year(args.year)
    elif args.all:
        load_all_years()
    else:
        print("Usage: python scripts/load_data.py --year 2024  OR  --all")
```

**Test Commands:**
```bash
# Test single year
python scripts/load_data.py --year 2024

# Load all years
python scripts/load_data.py --all
```

**Expected Outcome:**
- Downloads CSV files from Analyze Boston
- Parses ~20K-22K records per year
- Inserts into database with upsert logic
- Total ~100K-105K records across 5 years

---

### Task 4: Create Data Validation Script
**Files:** `scripts/validate_data.py`

**Implementation:**

```python
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
                print("✗ ERROR: Expected 5 years of data")
                return False

            if total < 100000:
                print("✗ WARNING: Total records less than expected (~100K)")
            else:
                print("✓ Record counts look good")

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
                print(f"✗ ERROR: Found {len(duplicates)} duplicate records")
                print(tabulate(duplicates, headers=['Year', 'Name', 'Dept', 'Title', 'Count']))
                return False
            else:
                print("✓ No duplicates found")

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
                print("✗ ERROR: No departments found")
                return False
            else:
                print("✓ Departments look reasonable")

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
            print("✓ Earnings totals calculated")

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
                print(f"✗ ERROR: Missing indexes: {missing}")
                return False
            else:
                print(f"✓ All {len(expected_indexes)} indexes exist")
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
            print(f"\n✗ ERROR in {check.__name__}: {e}")
            results.append((check.__name__, False))

    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n🎉 All validations passed! Data layer is ready.")
    else:
        print("\n❌ Some validations failed. Review errors above.")

    return all_passed

if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)
```

**Test Command:**
```bash
python scripts/validate_data.py
```

**Expected Outcome:**
- All validation checks pass
- Record counts match expected (~100K total)
- No duplicates found
- Departments look reasonable
- All indexes exist

---

### Task 5: Update requirements.txt with tabulate
**Files:** `requirements.txt`

**Implementation:**

Add to existing requirements.txt:
```txt
tabulate==0.9.0
```

**Install command:**
```bash
pip install -r requirements.txt
```

---

## Completion Criteria

- [x] Database schema created in shared PostgreSQL
- [ ] All 5 years of data loaded (~100K records)
- [ ] All indexes created
- [ ] No duplicate records
- [ ] Validation script passes all checks
- [ ] Database connection module works

## Verification Query

After completing all tasks, this query should work:

```sql
SELECT department, COUNT(*) as employees, SUM(total_gross)::money as total_earnings
FROM payroll_earnings
WHERE year = 2024
GROUP BY department
ORDER BY total_earnings DESC
LIMIT 10;
```

Expected: Returns top 10 departments by total earnings for 2024

## Handoff to Phase 2

Once Phase 1 is complete:
- Database contains all payroll data (2020-2024)
- Schema is optimized with indexes
- Data quality is validated
- Ready to build FastAPI backend

## Rollback Plan

If something goes wrong:
```sql
-- Drop table and start over
DROP TABLE IF EXISTS payroll_earnings CASCADE;
```

Then re-run:
```bash
python -m backend.database
python scripts/load_data.py --all
python scripts/validate_data.py
```

## Skills Used
- @sql-fundamentals - For schema design and queries
- @executing-plans - For systematic task execution

## Notes
- Uses shared Render PostgreSQL (prefix: `payroll_`)
- CSV download is idempotent (can re-run safely)
- Upsert logic handles re-runs gracefully
- Keep scripts for annual refresh
