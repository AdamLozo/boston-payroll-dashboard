"""
Load Boston payroll data to Render PostgreSQL database
Run this once to populate the production database
"""
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from pathlib import Path
from decimal import Decimal

import os

# Render PostgreSQL connection (External URL) - set via environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

def create_table(conn):
    """Create payroll_earnings table if it doesn't exist"""
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
    print("OK Table created successfully")

def load_csv_file(filepath, year, conn):
    """Load a single CSV file with error handling for different encodings"""
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            print(f"  Loaded with {encoding} encoding")
            break
        except (UnicodeDecodeError, Exception) as e:
            continue

    if df is None:
        raise Exception(f"Could not load {filepath} with any encoding")

    # Column mapping variations
    column_map = {
        'NAME': 'name',
        'Name': 'name',
        'DEPARTMENT_NAME': 'department',
        'DEPARTMENT': 'department',
        'Department Name': 'department',
        'TITLE': 'title',
        'Title': 'title',
        'REGULAR': 'regular',
        'Regular': 'regular',
        'RETRO': 'retro',
        'Retro': 'retro',
        'OTHER': 'other',
        'Other': 'other',
        'OVERTIME': 'overtime',
        'Overtime': 'overtime',
        'INJURED': 'injured',
        'Injured': 'injured',
        'DETAIL': 'detail',
        'Detail': 'detail',
        'QUINN/EDUCATION INCENTIVE': 'quinn_education',
        'Quinn/Education Incentive': 'quinn_education',
        'QUINN': 'quinn_education',
        'Quinn': 'quinn_education',
        'TOTAL GROSS': 'total_gross',
        'Total Gross': 'total_gross',
        'POSTAL': 'zip_code',
        'Postal': 'zip_code',
        'ZIP': 'zip_code',
        'Zip': 'zip_code'
    }

    df.rename(columns=column_map, inplace=True)

    # Ensure required columns exist
    required = ['name', 'total_gross']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in {filepath}")

    # Add missing columns with defaults
    optional_numeric = ['regular', 'retro', 'other', 'overtime', 'injured', 'detail', 'quinn_education']
    for col in optional_numeric:
        if col not in df.columns:
            df[col] = 0

    optional_text = ['department', 'title', 'zip_code']
    for col in optional_text:
        if col not in df.columns:
            df[col] = None

    df['year'] = year

    # Convert to appropriate types
    for col in optional_numeric + ['total_gross']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Clean text fields
    for col in ['name', 'department', 'title']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', None)

    return df

def load_excel_file(filepath, year, conn):
    """Load Excel file (for 2023 data)"""
    df = pd.read_excel(filepath)

    # Column mapping for Excel format
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
        'QUINN/EDUCATION INCENTIVE': 'quinn_education',
        'TOTAL GROSS': 'total_gross',
        'POSTAL': 'zip_code'
    }

    df.rename(columns=column_map, inplace=True)

    # Add missing columns
    optional_numeric = ['regular', 'retro', 'other', 'overtime', 'injured', 'detail', 'quinn_education']
    for col in optional_numeric:
        if col not in df.columns:
            df[col] = 0

    df['year'] = year

    # Convert to appropriate types
    for col in optional_numeric + ['total_gross']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

def insert_data(df, conn):
    """Insert data using upsert to avoid duplicates"""
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

    # Prepare data tuples
    records = []
    for _, row in df.iterrows():
        records.append((
            int(row['year']),
            row['name'],
            row['department'] if pd.notna(row['department']) else None,
            row['title'] if pd.notna(row['title']) else None,
            float(row['regular']),
            float(row['retro']),
            float(row['other']),
            float(row['overtime']),
            float(row['injured']),
            float(row['detail']),
            float(row['quinn_education']),
            float(row['total_gross']),
            row['zip_code'] if pd.notna(row['zip_code']) else None
        ))

    with conn.cursor() as cur:
        execute_values(cur, insert_sql, records)
        conn.commit()

    print(f"  Inserted {len(records):,} records")

def main():
    print("Loading Boston Payroll Data to Render PostgreSQL")
    print("=" * 60)

    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    print("OK Connected to Render PostgreSQL\n")

    # Create table
    create_table(conn)
    print()

    # Data directory
    data_dir = Path(r"C:\Users\adam\OneDrive\Claude\Projects\boston-payroll-dashboard\data")

    # Load each year
    files = [
        ('employee-earnings-report-2020.csv', 2020),
        ('employee-earnings-report-2021.csv', 2021),
        ('employee-earnings-report-2022.csv', 2022),
        ('employee-earnings-report-2023.xlsx', 2023),
        ('employee-earnings-report-2024.csv', 2024),
    ]

    total_records = 0

    for filename, year in files:
        filepath = data_dir / filename
        print(f"Loading {year} data from {filename}...")

        try:
            if filename.endswith('.csv'):
                df = load_csv_file(filepath, year, conn)
            else:
                df = load_excel_file(filepath, year, conn)

            insert_data(df, conn)
            total_records += len(df)
            print(f"OK {year} complete\n")

        except Exception as e:
            print(f"ERROR Error loading {filename}: {e}\n")
            continue

    # Verify data
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM payroll_earnings")
        count = cur.fetchone()[0]

        cur.execute("SELECT SUM(total_gross) FROM payroll_earnings")
        total_payroll = cur.fetchone()[0]

    print("=" * 60)
    print(f"OK Data load complete!")
    print(f"  Total records: {count:,}")
    print(f"  Total payroll: ${total_payroll:,.2f}")
    print("=" * 60)

    conn.close()

if __name__ == "__main__":
    main()
