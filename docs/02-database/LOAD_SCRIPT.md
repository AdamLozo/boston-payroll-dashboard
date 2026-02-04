# Data Load Script

## Python Script: load_data.py

```python
#!/usr/bin/env python3
"""
Load Boston Employee Earnings data into PostgreSQL.
Run once for initial load, then annually for updates.
"""

import os
import csv
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from decimal import Decimal

# Configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
DATA_DIR = 'data/raw'

# Files to load
FILES = {
    2024: 'earnings_2024.csv',
    2023: 'earnings_2023.xlsx',  # Note: XLSX format
    2022: 'earnings_2022.csv',
    2021: 'earnings_2021.csv',
    2020: 'earnings_2020.csv',
}

def parse_currency(value):
    """Convert currency string to float."""
    if pd.isna(value) or value == '' or value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(',', '').replace('$', ''))

def load_file(filepath, year):
    """Load a single file and return list of tuples."""
    print(f"Loading {filepath} for year {year}...")
    
    # Handle XLSX vs CSV
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)
    
    # Normalize column names (handle variations)
    df.columns = [c.upper().strip() for c in df.columns]
    
    # Map to standard names
    column_map = {
        'TOTAL GROSS': 'TOTAL_GROSS',
        'QUINN_EDUCATION': 'QUINN_EDUCATION',
        'QUINN EDUCATION': 'QUINN_EDUCATION',
    }
    df.rename(columns=column_map, inplace=True)
    
    records = []
    for _, row in df.iterrows():
        records.append((
            year,
            str(row.get('NAME', '')).strip(),
            str(row.get('DEPARTMENT_NAME', '')).strip(),
            str(row.get('TITLE', '')).strip(),
            parse_currency(row.get('REGULAR', 0)),
            parse_currency(row.get('RETRO', 0)),
            parse_currency(row.get('OTHER', 0)),
            parse_currency(row.get('OVERTIME', 0)),
            parse_currency(row.get('INJURED', 0)),
            parse_currency(row.get('DETAIL', 0)),
            parse_currency(row.get('QUINN_EDUCATION', 0)),
            parse_currency(row.get('TOTAL_GROSS', 0)),
            str(row.get('POSTAL', '')).strip(),
        ))
    
    print(f"  Loaded {len(records)} records")
    return records

def create_table(conn):
    """Create table if not exists."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employee_earnings (
                id SERIAL PRIMARY KEY,
                year INTEGER NOT NULL,
                name VARCHAR(200) NOT NULL,
                department_name VARCHAR(200),
                title VARCHAR(200),
                regular DECIMAL(12,2) DEFAULT 0,
                retro DECIMAL(12,2) DEFAULT 0,
                other DECIMAL(12,2) DEFAULT 0,
                overtime DECIMAL(12,2) DEFAULT 0,
                injured DECIMAL(12,2) DEFAULT 0,
                detail DECIMAL(12,2) DEFAULT 0,
                quinn_education DECIMAL(12,2) DEFAULT 0,
                total_gross DECIMAL(12,2) DEFAULT 0,
                postal VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(year, name, department_name, title)
            );
        """)
        conn.commit()

def create_indexes(conn):
    """Create indexes for performance."""
    with conn.cursor() as cur:
        # Enable trigram extension for fuzzy search
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_earnings_year ON employee_earnings(year);",
            "CREATE INDEX IF NOT EXISTS idx_earnings_department ON employee_earnings(department_name);",
            "CREATE INDEX IF NOT EXISTS idx_earnings_total_gross ON employee_earnings(total_gross DESC);",
            "CREATE INDEX IF NOT EXISTS idx_earnings_year_dept ON employee_earnings(year, department_name);",
            "CREATE INDEX IF NOT EXISTS idx_earnings_year_total ON employee_earnings(year, total_gross DESC);",
            "CREATE INDEX IF NOT EXISTS idx_earnings_name_trgm ON employee_earnings USING gin(name gin_trgm_ops);",
        ]
        for idx in indexes:
            cur.execute(idx)
        conn.commit()

def insert_records(conn, records):
    """Bulk insert with upsert."""
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO employee_earnings 
                (year, name, department_name, title, regular, retro, other, 
                 overtime, injured, detail, quinn_education, total_gross, postal)
            VALUES %s
            ON CONFLICT (year, name, department_name, title) 
            DO UPDATE SET
                regular = EXCLUDED.regular,
                retro = EXCLUDED.retro,
                other = EXCLUDED.other,
                overtime = EXCLUDED.overtime,
                injured = EXCLUDED.injured,
                detail = EXCLUDED.detail,
                quinn_education = EXCLUDED.quinn_education,
                total_gross = EXCLUDED.total_gross,
                postal = EXCLUDED.postal
            """,
            records,
            page_size=1000
        )
        conn.commit()

def main():
    conn = psycopg2.connect(DATABASE_URL)
    
    print("Creating table...")
    create_table(conn)
    
    print("Loading data...")
    all_records = []
    for year, filename in FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            records = load_file(filepath, year)
            all_records.extend(records)
        else:
            print(f"  WARNING: {filepath} not found, skipping")
    
    print(f"Inserting {len(all_records)} total records...")
    insert_records(conn, all_records)
    
    print("Creating indexes...")
    create_indexes(conn)
    
    # Verify
    with conn.cursor() as cur:
        cur.execute("SELECT year, COUNT(*) FROM employee_earnings GROUP BY year ORDER BY year;")
        print("\nRow counts by year:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]:,}")
    
    conn.close()
    print("\nDone!")

if __name__ == '__main__':
    main()
```

## Usage

```bash
# Set database URL
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

# Download data first (see RESOURCE_IDS.md)
# Then run load script
python scripts/load_data.py
```

## Expected Output

```
Creating table...
Loading data...
Loading data/raw/earnings_2024.csv for year 2024...
  Loaded 23,456 records
Loading data/raw/earnings_2023.xlsx for year 2023...
  Loaded 22,789 records
...
Inserting 110,234 total records...
Creating indexes...

Row counts by year:
  2020: 21,023
  2021: 21,456
  2022: 22,012
  2023: 22,789
  2024: 23,456

Done!
```

## Annual Update Process

1. Download new year's CSV from Analyze Boston
2. Add to FILES dict in script
3. Run script (upsert handles existing data)
4. Verify counts
