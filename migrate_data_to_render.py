"""
Migrate payroll data from local PostgreSQL to Render PostgreSQL
"""
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

# Source: Local PostgreSQL
LOCAL_DB = "postgresql://postgres:D01&ozo$866A@localhost:5432/boston_permits"

# Target: Render PostgreSQL
RENDER_DB = "postgresql://dashboard:iFtQwJtXDWgXQjxnZqPWuGPXdERmOV72@dpg-d61893ggjchc73evihmg-a.oregon-postgres.render.com/boston_permits"

def create_table(conn):
    """Create payroll_earnings table on Render"""
    create_sql = """
    CREATE TABLE IF NOT EXISTS payroll_earnings (
        id SERIAL PRIMARY KEY,
        year INTEGER NOT NULL,
        name VARCHAR(255) NOT NULL,
        department VARCHAR(255),
        title VARCHAR(255),
        regular NUMERIC(12, 2) DEFAULT 0,
        retro NUMERIC(12, 2) DEFAULT 0,
        other NUMERIC(12, 2) DEFAULT 0,
        overtime NUMERIC(12, 2) DEFAULT 0,
        injured NUMERIC(12, 2) DEFAULT 0,
        detail NUMERIC(12, 2) DEFAULT 0,
        quinn_education NUMERIC(12, 2) DEFAULT 0,
        total_gross NUMERIC(12, 2) NOT NULL,
        zip_code VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(year, name, department, title)
    );

    CREATE INDEX IF NOT EXISTS idx_payroll_year ON payroll_earnings(year);
    CREATE INDEX IF NOT EXISTS idx_payroll_dept ON payroll_earnings(department);
    CREATE INDEX IF NOT EXISTS idx_payroll_name ON payroll_earnings(name);
    """

    with conn.cursor() as cur:
        cur.execute(create_sql)
        conn.commit()
    print("OK Table created on Render")

def copy_data(local_conn, render_conn):
    """Copy all data from local to Render"""
    print("\nFetching data from local database...")

    with local_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT year, name, department, title, regular, retro, other, overtime,
                   injured, detail, quinn_education, total_gross, zip_code
            FROM payroll_earnings
            ORDER BY year, name
        """)
        records = cur.fetchall()

    print(f"Found {len(records):,} records to migrate\n")

    if len(records) == 0:
        print("No data to migrate!")
        return

    # Insert in batches
    insert_sql = """
    INSERT INTO payroll_earnings (
        year, name, department, title, regular, retro, other, overtime,
        injured, detail, quinn_education, total_gross, zip_code
    ) VALUES %s
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

    # Prepare tuples
    values = []
    for r in records:
        values.append((
            r['year'], r['name'], r['department'], r['title'],
            r['regular'], r['retro'], r['other'], r['overtime'],
            r['injured'], r['detail'], r['quinn_education'],
            r['total_gross'], r['zip_code']
        ))

    # Insert in batches of 1000
    batch_size = 1000
    total = len(values)

    print("Inserting data to Render...")
    for i in range(0, total, batch_size):
        batch = values[i:i + batch_size]
        with render_conn.cursor() as cur:
            execute_values(cur, insert_sql, batch)
            render_conn.commit()
        print(f"  Progress: {min(i + batch_size, total):,} / {total:,} records")

    print("OK Data migration complete!\n")

def verify_data(conn):
    """Verify migrated data"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM payroll_earnings")
        count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT year) FROM payroll_earnings")
        years = cur.fetchone()[0]

        cur.execute("SELECT SUM(total_gross) FROM payroll_earnings")
        total = cur.fetchone()[0]

        cur.execute("SELECT year, COUNT(*) as cnt FROM payroll_earnings GROUP BY year ORDER BY year")
        year_counts = cur.fetchall()

    print("=" * 60)
    print("Data Verification:")
    print(f"  Total records: {count:,}")
    print(f"  Years: {years}")
    print(f"  Total payroll: ${total:,.2f}")
    print("\nRecords by year:")
    for year, cnt in year_counts:
        print(f"    {year}: {cnt:,} records")
    print("=" * 60)

def main():
    print("Migrating Payroll Data: Local -> Render PostgreSQL")
    print("=" * 60)

    # Connect to both databases
    print("Connecting to databases...")
    local_conn = psycopg2.connect(LOCAL_DB)
    print("  OK Local PostgreSQL")

    render_conn = psycopg2.connect(RENDER_DB)
    print("  OK Render PostgreSQL\n")

    # Create table on Render
    create_table(render_conn)

    # Copy data
    copy_data(local_conn, render_conn)

    # Verify
    verify_data(render_conn)

    # Close connections
    local_conn.close()
    render_conn.close()

    print("\nMigration complete!")

if __name__ == "__main__":
    main()
