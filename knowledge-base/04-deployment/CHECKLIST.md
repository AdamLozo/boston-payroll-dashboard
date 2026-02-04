# Deployment Checklist

## Prerequisites
- [ ] Phase 3 (Frontend) complete
- [ ] All local tests passing
- [ ] GitHub repository created

## Tasks

### Task 1: Prepare Repository
**Time**: 5 minutes

- [ ] Initialize git if not done
- [ ] Create .gitignore
- [ ] Commit all files
- [ ] Push to GitHub

**Verification**:
```bash
git status
# Should show clean working tree
```

### Task 2: Create Render Web Service
**Time**: 10 minutes

- [ ] Log into Render dashboard
- [ ] Create new Web Service
- [ ] Connect GitHub repository
- [ ] Configure build/start commands
- [ ] Link to existing database
- [ ] Deploy

**Verification**:
```bash
# Wait for deploy to complete
curl https://boston-payroll-web.onrender.com/api/health
```

### Task 3: Configure Custom Domain
**Time**: 10 minutes

- [ ] Add custom domain in Render
- [ ] Note any verification requirements
- [ ] Add CNAME in GoDaddy
- [ ] Wait for DNS propagation

**Verification**:
```bash
# Check DNS
dig bostonpayroll.adamlozo.com

# Check HTTPS
curl -I https://bostonpayroll.adamlozo.com
# Should show 200 OK with valid SSL
```

### Task 4: Load Production Data
**Time**: 15 minutes

- [ ] Access Render Shell (or use local + prod DB)
- [ ] Run load_data.py for all years
- [ ] Monitor for errors
- [ ] Verify record counts

**Verification**:
```bash
curl "https://bostonpayroll.adamlozo.com/api/stats?year=2024"
# Check total_employees > 20000
```

### Task 5: Smoke Test Production
**Time**: 10 minutes

- [ ] Load homepage
- [ ] Test year filter
- [ ] Test department filter
- [ ] Test search
- [ ] Test table sorting
- [ ] Test pagination
- [ ] Test export CSV
- [ ] Test on mobile

**Verification**:
- All features work as expected

### Task 6: Update DNS TTL (Optional)
**Time**: 2 minutes

- [ ] Once working, increase TTL to 3600 (1 hour)

## Completion Criteria

- [ ] Site accessible at bostonpayroll.adamlozo.com
- [ ] SSL certificate valid
- [ ] All API endpoints working
- [ ] Frontend fully functional
- [ ] Data loaded for all 5 years

## Post-Deployment

- [ ] Add to portfolio/README
- [ ] Set up monitoring (optional)
- [ ] Document annual refresh process
- [ ] Share with community (optional)
