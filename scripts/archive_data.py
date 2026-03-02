"""
Archive existing payroll data to CSV before refreshing from Analyze Boston.

Preserves data locally in case Boston drops older years from their rolling dataset.
Run this BEFORE load_data.py to snapshot what's currently in the database.

Usage:
    python scripts/archive_data.py              # Archive all years
    python scripts/archive_data.py --year 2020  # Archive specific year
"""
import os
import sys
import csv
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_db_connection

# Archive directory (persisted in repo)
ARCHIVE_DIR = Path(__file__).parent.parent / "data" / "archive"


def archive_year(year: int, force: bool = False) -> Path:
    """Export a single year's data to CSV. Returns the output file path."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    output_path = ARCHIVE_DIR / f"boston_payroll_{year}.csv"

    # Skip if archive already exists (unless forced)
    if output_path.exists() and not force:
        print(f"[SKIP] Archive already exists: {output_path}")
        return output_path

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT year, name, department, title,
                       regular, retro, other, overtime, injured, detail,
                       quinn_education, total_gross, zip_code
                FROM payroll_earnings
                WHERE year = %s
                ORDER BY total_gross DESC
                """,
                (year,),
            )
            rows = cur.fetchall()
            columns = [
                "year", "name", "department", "title",
                "regular", "retro", "other", "overtime", "injured", "detail",
                "quinn_education", "total_gross", "zip_code",
            ]

    if not rows:
        print(f"[WARN] No data found for year {year}")
        return output_path

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"[OK] Archived {len(rows):,} records for {year} -> {output_path}")
    return output_path


def archive_all(force: bool = False):
    """Archive every year currently in the database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT year FROM payroll_earnings ORDER BY year"
            )
            years = [row[0] for row in cur.fetchall()]

    if not years:
        print("[WARN] No data in database to archive")
        return

    print(f"Archiving {len(years)} years: {years}")
    print(f"Archive directory: {ARCHIVE_DIR}")
    print("=" * 60)

    for year in years:
        archive_year(year, force=force)

    # Write a manifest with archive metadata
    manifest_path = ARCHIVE_DIR / "manifest.txt"
    with open(manifest_path, "w") as f:
        f.write(f"Boston Payroll Data Archive\n")
        f.write(f"Archived at: {datetime.now().isoformat()}\n")
        f.write(f"Years: {years}\n")
        f.write(f"\nFiles:\n")
        for year in years:
            csv_path = ARCHIVE_DIR / f"boston_payroll_{year}.csv"
            if csv_path.exists():
                size_mb = csv_path.stat().st_size / (1024 * 1024)
                f.write(f"  boston_payroll_{year}.csv  ({size_mb:.1f} MB)\n")

    print("=" * 60)
    print(f"[OK] Archive complete. Manifest: {manifest_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Archive Boston payroll data to CSV")
    parser.add_argument("--year", type=int, help="Archive specific year")
    parser.add_argument("--force", action="store_true", help="Overwrite existing archives")
    parser.add_argument("--all", action="store_true", help="Archive all years")

    args = parser.parse_args()

    if args.year:
        archive_year(args.year, force=args.force)
    else:
        archive_all(force=args.force)
