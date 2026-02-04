# Pre-Launch Checklist

## Database ✅

- [ ] Table `employee_earnings` created
- [ ] Indexes created (year, department, total_gross, name trigram)
- [ ] Data loaded for years 2020-2024
- [ ] Verify row counts match expectations (~110K total)
- [ ] Test query performance (<100ms for common queries)

```sql
-- Verification queries
SELECT year, COUNT(*) FROM employee_earnings GROUP BY year ORDER BY year;
SELECT COUNT(*) FROM employee_earnings WHERE total_gross > 200000;
```

## Backend ✅

- [ ] All API endpoints working locally
- [ ] `/api/health` returns OK
- [ ] `/api/employees` returns paginated data
- [ ] `/api/stats` returns correct totals
- [ ] `/api/departments` returns top departments
- [ ] Search (ILIKE) working
- [ ] Sorting working on all columns

```bash
# Local test commands
curl http://localhost:8000/api/health
curl "http://localhost:8000/api/employees?year=2024&limit=10"
curl http://localhost:8000/api/stats?year=2024
```

## Frontend ✅

- [ ] Table loads and displays data
- [ ] Sorting works (click column headers)
- [ ] Pagination works
- [ ] Year filter updates table + stats
- [ ] Department filter works
- [ ] Search box works (debounced)
- [ ] Currency formatting correct
- [ ] Charts render (department breakdown, composition)
- [ ] Mobile responsive (table scrolls)
- [ ] No console errors

## Deployment ✅

- [ ] Code pushed to GitHub
- [ ] Render web service created
- [ ] DATABASE_URL configured (internal URL)
- [ ] First deploy successful (check logs)
- [ ] Site accessible at `*.onrender.com`

## DNS ✅

- [ ] CNAME added in GoDaddy
- [ ] Custom domain added in Render
- [ ] DNS propagated (check with nslookup)
- [ ] SSL certificate active
- [ ] `https://bostonpayroll.adamlozo.com` works

## Final Verification ✅

- [ ] Homepage loads <2 seconds
- [ ] Table search feels instant
- [ ] Stats bar shows correct numbers
- [ ] All years (2020-2024) work
- [ ] Department filter has all departments
- [ ] Export/share URL works with filters

## Post-Launch

- [ ] Test from mobile device
- [ ] Share on social media (optional)
- [ ] Add to portfolio/readme (optional)
- [ ] Set up UptimeRobot monitoring (optional)

---

## Quick Fix Commands

**Rebuild on Render:**
Render Dashboard → boston-payroll → Manual Deploy → Deploy latest commit

**Check logs:**
Render Dashboard → boston-payroll → Logs

**Database shell:**
```bash
psql $DATABASE_URL
```

**Force SSL redirect (if needed in main.py):**
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)
```
