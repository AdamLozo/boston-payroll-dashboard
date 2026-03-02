import os
import sys
import requests
import pandas as pd
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_db_connection

# Resource IDs for each year
RESOURCE_IDS = {
    2025: "ca45bfb5-7bc2-4756-a862-77014547faf8",
    2024: "579a4be3-9ca7-4183-bc95-7d67ee715b6d",
    2023: "6b3c5333-1dcb-4b3d-9cd7-6a03fb526da7",
    2022: "63ac638b-36c4-487d-9453-1d83eb5090d2",
    2021: "ec5aaf93-1509-4641-9310-28e62e028457",
    2020: "e2e2c23a-6fc7-4456-8751-5321d8aa869b",
}

CSV_URL_TEMPLATE = "https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/{resource_id}/download"

def download_csv(year, output_dir=None):
    """Download data file for a specific year (CSV or XLSX)."""
    resource_id = RESOURCE_IDS.get(year)
    if not resource_id:
        raise ValueError(f"No resource ID for year {year}")

    url = CSV_URL_TEMPLATE.format(resource_id=resource_id)

    # Use system temp directory if not specified
    if output_dir is None:
        output_dir = tempfile.gettempdir()

    print(f"Downloading {year} data from Analyze Boston...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    # Detect file type from content
    is_excel = response.content[:2] == b'PK'  # Excel files start with PK (ZIP signature)

    if is_excel:
        output_path = Path(output_dir) / f"boston_earnings_{year}.xlsx"
        print(f"[INFO] Detected Excel file format")
    else:
        output_path = Path(output_dir) / f"boston_earnings_{year}.csv"

    output_path.write_bytes(response.content)
    print(f"[OK] Downloaded to {output_path} ({len(response.content)} bytes)")

    return str(output_path)

def parse_csv(csv_path, year):
    """Parse CSV or Excel file and transform to database-ready format."""
    print(f"Parsing {csv_path}...")

    df = None

    # Check if it's an Excel file
    if csv_path.endswith('.xlsx') or csv_path.endswith('.xls'):
        try:
            df = pd.read_excel(csv_path, engine='openpyxl')
            print(f"[OK] Successfully parsed Excel file")
        except Exception as e:
            print(f"[ERROR] Failed to parse Excel: {e}")
            raise
    else:
        # Try multiple encodings for CSV
        encodings = ['utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding, on_bad_lines='skip', engine='python')
                print(f"[OK] Successfully parsed with encoding: {encoding}")
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
            except Exception as e:
                print(f"[WARNING] Failed with {encoding}: {e}")
                continue

        if df is None:
            raise ValueError(f"Could not parse file with any known encoding")

    # Strip whitespace from column names first
    df.columns = df.columns.str.strip()

    # Column mapping (CSV -> database)
    # Handle variations in column names across years
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
        'QUINN / EDUCATION INCENTIVE': 'quinn_education',
        'QUINN_EDUCATION_INCENTIVE': 'quinn_education',
        'TOTAL GROSS': 'total_gross',
        'TOTAL_GROSS': 'total_gross',
        'TOTAL_ GROSS': 'total_gross',  # 2022 has a space before GROSS
        'TOTAL EARNINGS': 'total_gross',
        'POSTAL': 'zip_code',
    }

    # Rename columns
    df = df.rename(columns=column_map)

    # Debug: show what columns we have after mapping
    print(f"[DEBUG] Columns after mapping: {list(df.columns)}")

    # Add year column
    df['year'] = year

    # Drop rows with no employee name (handles Excel padding with empty rows)
    df = df.dropna(subset=['name'])
    df = df[df['name'].astype(str).str.strip() != '']

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

    # Ensure all required columns exist (add missing ones with default values)
    all_required_columns = ['year', 'name', 'department', 'title'] + numeric_fields + ['zip_code']
    for col in all_required_columns:
        if col not in df.columns:
            if col in numeric_fields:
                df[col] = 0.0
            else:
                df[col] = ''

    # Select columns in the correct order
    df = df[all_required_columns]

    print(f"[OK] Parsed {len(df)} records")
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
            print(f"[OK] Inserted {len(records)} records for {year}")

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
    print(f"[OK] Cleaned up temp file")

def load_all_years():
    """Load data for all years (2020-2024)."""
    for year in sorted(RESOURCE_IDS.keys()):
        try:
            load_year(year)
        except Exception as e:
            print(f"[ERROR] Error loading year {year}: {e}")
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
