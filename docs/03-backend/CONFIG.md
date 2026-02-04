# Backend Configuration

## Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:password@host:5432/boston_data

# Optional
PORT=8000
LOG_LEVEL=INFO
```

## File: backend/config.py

```python
"""Configuration settings for Boston Payroll Dashboard."""
import os

class Settings:
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # API Settings
    DEFAULT_LIMIT = 100
    MAX_LIMIT = 500
    DEFAULT_YEAR = 2024
    MIN_YEAR = 2020
    MAX_YEAR = 2024
    
    # Valid sort columns (prevent SQL injection)
    VALID_SORT_COLUMNS = [
        'total_gross', 'regular', 'overtime', 'detail', 
        'name', 'department_name', 'year'
    ]
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://bostonpayroll.adamlozo.com",
    ]

settings = Settings()
```

## File: backend/database.py

```python
"""Database connection and utilities."""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from .config import settings

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = psycopg2.connect(
        settings.DATABASE_URL,
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database schema."""
    # See SCHEMA.md for full implementation
    pass
```

## Dependencies

**File: requirements.txt**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pandas==2.2.0
openpyxl==3.1.2
```

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."

# Run server
uvicorn backend.main:app --reload --port 8000
```
