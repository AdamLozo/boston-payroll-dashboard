# System Architecture

## High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Static HTML/JS                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │   │
│  │  │  Filters │  │  Stats   │  │   DataTables Grid    │  │   │
│  │  │ Year/Dept│  │  Cards   │  │   (AG Grid/DT)       │  │   │
│  │  └──────────┘  └──────────┘  └──────────────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────────┐│   │
│  │  │              Charts (Chart.js)                      ││   │
│  │  │   Dept Breakdown    │    Earnings Composition       ││   │
│  │  └─────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     FastAPI                              │   │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │   │
│  │  │ /api/      │  │ /api/      │  │ /api/            │  │   │
│  │  │ employees  │  │ departments│  │ stats            │  │   │
│  │  └────────────┘  └────────────┘  └──────────────────┘  │   │
│  │  ┌────────────┐  ┌────────────┐                        │   │
│  │  │ /api/      │  │ /api/      │                        │   │
│  │  │ earnings   │  │ health     │                        │   │
│  │  └────────────┘  └────────────┘                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SQL
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED POSTGRESQL                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  payroll_earnings (main table)                           │   │
│  │  ├── id (PK)                                             │   │
│  │  ├── year                                                │   │
│  │  ├── name                                                │   │
│  │  ├── department                                          │   │
│  │  ├── title                                               │   │
│  │  ├── regular, retro, other, overtime, injured, detail    │   │
│  │  ├── quinn_education                                     │   │
│  │  ├── total_gross                                         │   │
│  │  └── zip_code                                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│  Also in this DB: building_permits, restaurants, etc.           │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Initial Load (One-Time)
```
Analyze Boston CSVs (2020-2024)
         │
         ▼
    Download Script
    (Python requests)
         │
         ▼
    Parse & Transform
    (Add year column)
         │
         ▼
    Bulk Insert
    (PostgreSQL COPY)
         │
         ▼
    ~100K records loaded
```

### Request Flow (Runtime)
```
User Action                API Call                    Database Query
───────────────────────────────────────────────────────────────────
Page Load           →   /api/stats              →   SELECT aggregates
                    →   /api/departments        →   SELECT DISTINCT
                    →   /api/employees?limit=50 →   SELECT with pagination

Filter Change       →   /api/employees?dept=X   →   SELECT WHERE dept = X
                    →   /api/stats?dept=X       →   SELECT aggregates WHERE

Search              →   (client-side)           →   (no DB call)
```

## Component Responsibilities

### Frontend (`frontend/`)
- Static HTML/CSS/JS served by FastAPI
- DataTables or AG Grid for employee table
- Chart.js for visualizations
- Client-side search (after initial data load)
- Responsive Bootstrap/Tailwind layout

### Backend (`backend/`)
- FastAPI application
- PostgreSQL connection pooling
- JSON API endpoints
- Static file serving
- Health check endpoint

### Database
- Shared Render PostgreSQL instance
- Table prefix: `payroll_`
- Indexes on: year, department, total_gross

### Scripts (`scripts/`)
- `load_data.py` - One-time CSV load
- `validate_data.py` - Post-load validation

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | HTML/JS + DataTables | Fast, simple, no build step |
| Charts | Chart.js | Lightweight, sufficient for needs |
| Backend | FastAPI | Async, fast, existing pattern |
| Database | PostgreSQL | Shared infrastructure |
| Hosting | Render | Existing account, easy deploy |
| DNS | GoDaddy | Existing domain |

## File Structure

```
boston-payroll-dashboard/
├── MASTER_PLAN.md
├── README.md
├── requirements.txt
├── render.yaml
│
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── config.py        # Settings
│   ├── database.py      # DB connection, schema
│   └── models.py        # Pydantic models
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── scripts/
│   ├── load_data.py
│   └── validate_data.py
│
├── knowledge-base/
│   └── ... (this documentation)
│
└── tests/
    └── test_api.py
```
