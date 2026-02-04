# Existing Dashboards Reference

## Building Permits Dashboard

**URL**: https://bostonbuilding.adamlozo.com (or similar)
**Repo**: https://github.com/adamlozo/boston-building-permits

### What to Reuse
- FastAPI app structure
- Database connection pattern
- Render deployment config
- CORS configuration
- Health endpoint pattern

### What's Different
- This uses CKAN streaming API (datastore_search_sql)
- Has map as primary interface
- Uses Leaflet.js for mapping
- Has cron job for continuous sync

## Restaurant Inspections Dashboard

**URL**: https://bostonrestaurants.adamlozo.com (or similar)
**Repo**: https://github.com/adamlozo/boston-restaurant-inspections

### What to Reuse
- Similar structure to building permits
- Category filtering pattern
- Date range filtering

### What's Different
- Different data structure (inspections vs earnings)
- Different visualizations

## Code Patterns to Copy

### FastAPI App Setup
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Boston Payroll Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")
```

### Database Connection
```python
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(os.environ['DATABASE_URL'], cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()
```

### API Pattern
```python
@app.get("/api/data")
async def get_data(
    limit: int = 100,
    offset: int = 0,
    year: Optional[int] = None
):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM table WHERE ...")
            return {"data": cur.fetchall()}
```

## Directory Structure (Both Projects)

```
project/
├── backend/
│   ├── __init__.py
│   ├── main.py         # FastAPI app
│   ├── database.py     # DB connection
│   └── config.py       # Settings
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── scripts/
│   └── load_data.py    # One-time data load
├── requirements.txt
├── render.yaml
└── README.md
```
