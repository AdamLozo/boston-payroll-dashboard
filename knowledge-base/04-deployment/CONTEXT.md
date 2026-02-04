# Deployment Context

## Overview
Deploy to Render using existing infrastructure. Add DNS record at GoDaddy.

## Infrastructure

### Render Account
- **Status**: Existing paid account
- **Database**: Shared PostgreSQL Starter ($7/mo)
- **Other Services**: boston-permits, boston-restaurants

### Target URL
- **Production**: https://bostonpayroll.adamlozo.com
- **Render URL**: https://boston-payroll-web.onrender.com (temporary)

## Render Configuration

### render.yaml
```yaml
services:
  - type: web
    name: boston-payroll-web
    runtime: python
    region: ohio  # Match existing services
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: boston-shared-db
          property: connectionString
      - key: ENVIRONMENT
        value: production
    healthCheckPath: /api/health
```

### No Cron Job Needed
Unlike building permits, this data updates annually. Manual refresh documented in runbook.

## DNS Configuration

### GoDaddy Settings
**Domain**: adamlozo.com

Add CNAME record:
```
Type: CNAME
Name: bostonpayroll
Value: boston-payroll-web.onrender.com
TTL: 600 (10 minutes)
```

### SSL
Render handles SSL automatically via Let's Encrypt.

## Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| DATABASE_URL | (from Render DB) | Auto-linked |
| ENVIRONMENT | production | |
| PORT | (auto) | Render sets this |

## Deployment Steps

### Step 1: Create Repository
```bash
cd boston-payroll-dashboard
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/AdamLozo/boston-payroll-dashboard.git
git push -u origin main
```

### Step 2: Create Render Web Service
1. Go to https://dashboard.render.com
2. Click "New" → "Web Service"
3. Connect GitHub repo
4. Configure:
   - Name: `boston-payroll-web`
   - Region: Ohio (match existing)
   - Branch: main
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable:
   - DATABASE_URL → Link to existing database
6. Deploy

### Step 3: Verify Render Deployment
```bash
curl https://boston-payroll-web.onrender.com/api/health
# Should return healthy status
```

### Step 4: Configure Custom Domain
1. In Render dashboard → Settings → Custom Domains
2. Add: `bostonpayroll.adamlozo.com`
3. Copy verification value if needed

### Step 5: Add DNS Record
1. Go to GoDaddy DNS management
2. Add CNAME record:
   - Name: `bostonpayroll`
   - Value: `boston-payroll-web.onrender.com`
3. Wait for propagation (up to 10 minutes)

### Step 6: Verify Custom Domain
```bash
curl https://bostonpayroll.adamlozo.com/api/health
# Should return healthy status with SSL
```

### Step 7: Run Data Load (One-Time)
Using Render Shell or locally:
```bash
# Option A: Render Shell
# Go to Render → boston-payroll-web → Shell
python scripts/load_data.py --all-years

# Option B: Local with prod DATABASE_URL
DATABASE_URL="postgresql://..." python scripts/load_data.py --all-years
```

### Step 8: Verify Data
```bash
curl "https://bostonpayroll.adamlozo.com/api/stats?year=2024"
# Should show ~22,000 employees
```

## Rollback Plan

### If Deployment Fails
1. Check Render logs for errors
2. Revert to previous commit if needed:
```bash
git revert HEAD
git push
```

### If Database Issues
1. Data is in shared DB, won't affect other services
2. Can drop and recreate payroll_ tables:
```sql
DROP TABLE IF EXISTS payroll_earnings CASCADE;
```

## Monitoring

### Health Check
Render auto-monitors `/api/health` endpoint.

### Manual Checks
```bash
# Check API
curl https://bostonpayroll.adamlozo.com/api/health

# Check data freshness
curl https://bostonpayroll.adamlozo.com/api/years
```

### Uptime Monitoring (Optional)
Add to UptimeRobot:
- URL: https://bostonpayroll.adamlozo.com/api/health
- Interval: 5 minutes

## Cost

| Item | Cost |
|------|------|
| Web Service | Free tier |
| Database | Shared ($7/mo prorated) |
| Domain | Existing |
| SSL | Free (Render) |
| **Total** | ~$0-2/mo additional |

## Security Notes

- Database connection uses SSL
- No sensitive data (public records)
- CORS restricted to custom domain in production
- No authentication required (public dashboard)
