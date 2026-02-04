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

            print("[OK] Schema created successfully")

            # Verify table exists
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'payroll_earnings'
            """)
            if cur.fetchone():
                print("[OK] Table 'payroll_earnings' verified")
            else:
                raise Exception("Table creation failed")

if __name__ == "__main__":
    create_schema()
