# Render Configuration

## Service Type: Web Service (not Static Site)

Since we have a FastAPI backend, this is a Web Service.

## Render Dashboard Setup

### Web Service Settings

| Setting | Value |
|---------|-------|
| Name | `boston-payroll` |
| Region | Ohio (us-east) |
| Branch | `main` |
| Root Directory | (leave blank) |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free (or Starter) |
| Auto-Deploy | Yes |

### Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | (from existing Render PostgreSQL) | Use internal URL |
| `PYTHON_VERSION` | `3.11.4` | Optional but recommended |

### Getting DATABASE_URL

1. Go to Render Dashboard → PostgreSQL → `boston-data` (your existing DB)
2. Copy **Internal Database URL**
3. Paste as `DATABASE_URL` in web service env vars

## File: render.yaml (Blueprint)

```yaml
services:
  - type: web
    name: boston-payroll
    runtime: python
    region: ohio
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: boston-data
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.11.4
    autoDeploy: true
```

## Static Files

FastAPI serves static files directly:

```python
# In main.py
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve index.html at root
@app.get("/")
async def root():
    return FileResponse("frontend/index.html")
```

## Health Check

Render pings `/` by default. We'll also expose `/api/health`:

```python
@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

## Deployment Steps

1. Push code to GitHub
2. In Render Dashboard, click "New" → "Web Service"
3. Connect to `adamlozo/boston-payroll-dashboard` repo
4. Configure settings per above
5. Click "Create Web Service"
6. Wait ~3-5 minutes for first deploy

## Logs

Monitor at: Render Dashboard → boston-payroll → Logs

Key things to watch:
- Build success
- Database connection
- First request timing
