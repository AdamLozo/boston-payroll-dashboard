# Boston Payroll Dashboard

Searchable dashboard for Boston city employee earnings data (2020-2024).

## Overview

Transparent public dashboard showing Boston city employee compensation data from Analyze Boston's open data portal. Explore salaries, overtime, and department spending across 118,000+ employee records.

**Live Site:** https://bostonpayroll.adamlozo.com *(coming soon)*

## Data

- **Source:** [Analyze Boston - Employee Earnings Report](https://data.boston.gov/dataset/employee-earnings-report)
- **Years:** 2020-2024 (5 years)
- **Records:** 118,931 total
- **Total Payroll:** $10.18 billion

## Features

- 🔍 Search employees by name, department, or title
- 📊 Department-level analytics and aggregations
- 💰 Earnings breakdown (regular pay, overtime, detail pay, etc.)
- 📅 Year-over-year comparisons
- 📱 Mobile-responsive design

## Tech Stack

- **Backend:** Python/FastAPI
- **Database:** PostgreSQL
- **Frontend:** Vanilla JS with DataTables
- **Hosting:** Render
- **Data:** Analyze Boston CKAN API

## Project Status

- ✅ **Phase 1 Complete:** Data layer with PostgreSQL schema and data loader
- 🚧 **Phase 2 In Progress:** FastAPI backend endpoints
- ⏳ **Phase 3 Planned:** Frontend UI
- ⏳ **Phase 4 Planned:** Deployment to Render

## Local Development

### Prerequisites

- Python 3.9+
- PostgreSQL 14+

### Setup

```bash
# Clone repository
git clone https://github.com/AdamLozo/boston-payroll-dashboard.git
cd boston-payroll-dashboard

# Install dependencies
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env with your DATABASE_URL

# Create schema
python -m backend.database

# Load data (takes ~5 minutes)
python scripts/load_data.py --all

# Validate data
python scripts/validate_data.py
```

### Data Refresh

To update with latest data:

```bash
# Download and load specific year
python scripts/load_data.py --year 2024

# Or reload all years
python scripts/load_data.py --all
```

## Database Schema

```sql
CREATE TABLE payroll_earnings (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    title VARCHAR(255),
    regular DECIMAL(12,2),
    retro DECIMAL(12,2),
    other DECIMAL(12,2),
    overtime DECIMAL(12,2),
    injured DECIMAL(12,2),
    detail DECIMAL(12,2),
    quinn_education DECIMAL(12,2),
    total_gross DECIMAL(12,2),
    zip_code VARCHAR(10),
    created_at TIMESTAMP,
    UNIQUE(year, name, department, title)
);
```

## Project Structure

```
boston-payroll-dashboard/
├── backend/
│   ├── database.py          # Schema and connection pooling
│   ├── config.py            # Environment configuration
│   └── main.py              # FastAPI app (coming soon)
├── scripts/
│   ├── load_data.py         # Data loader for CSV/Excel files
│   └── validate_data.py     # Data quality validation
├── frontend/                # Frontend UI (coming soon)
├── docs/                    # Technical documentation
└── knowledge-base/          # Domain context and guides
```

## API Endpoints (Coming Soon)

- `GET /api/employees` - Paginated employee list with search/filter
- `GET /api/departments` - Department aggregations
- `GET /api/stats` - Summary statistics
- `GET /api/earnings-breakdown` - Earnings composition data

## Related Projects

- [Boston Building Permits](https://github.com/AdamLozo/boston-data-dashboard) - Map-focused permit tracking
- [Boston Restaurant Inspections](https://github.com/AdamLozo/boston-inspections-dashboard) - Restaurant health inspections

## License

Data: [Open Data Commons PDDL](https://opendatacommons.org/licenses/pddl/)
Code: MIT

## Acknowledgments

- Data provided by [Analyze Boston](https://data.boston.gov/)
- Built with [FastAPI](https://fastapi.tiangolo.com/) and [PostgreSQL](https://www.postgresql.org/)
