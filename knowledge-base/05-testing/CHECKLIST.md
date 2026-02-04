# Testing Checklist

## Phase 1: Data Validation
**Run after**: Data load complete
**Time**: 10 minutes

### Record Counts
- [ ] 2020 records: 19,000 - 21,000
- [ ] 2021 records: 19,000 - 21,000
- [ ] 2022 records: 20,000 - 22,000
- [ ] 2023 records: 21,000 - 23,000
- [ ] 2024 records: 21,000 - 23,000
- [ ] Total: ~100,000 - 110,000

### Data Quality
- [ ] No duplicate records
- [ ] No null names
- [ ] Departments count: 50-80
- [ ] Known departments exist (Police, Fire, Schools)

### Earnings Sanity
- [ ] Total payroll per year: $1.5B - $3B
- [ ] Average salary: $80K - $150K
- [ ] Top earner: < $500K (reasonable)
- [ ] Negative earnings < 1% of records

## Phase 2: API Testing
**Run after**: Backend complete
**Time**: 15 minutes

### Endpoint Tests
- [ ] GET /api/health returns 200
- [ ] GET /api/years returns 5 years
- [ ] GET /api/employees returns paginated data
- [ ] GET /api/employees?department=X filters correctly
- [ ] GET /api/employees?search=X searches name/title
- [ ] GET /api/employees?sort_by=X sorts correctly
- [ ] GET /api/departments returns all departments
- [ ] GET /api/stats returns summary
- [ ] GET /api/earnings-breakdown returns composition

### Error Handling
- [ ] Invalid year returns 422
- [ ] Unknown endpoint returns 404
- [ ] Database error returns 500 (test by disconnecting)

### Performance
- [ ] Health check < 50ms
- [ ] Employees query < 200ms
- [ ] Stats query < 100ms

## Phase 3: Frontend Testing
**Run after**: Frontend complete
**Time**: 20 minutes

### Filter Controls
- [ ] Year dropdown populated
- [ ] Department dropdown populated
- [ ] Year change updates table
- [ ] Department change updates table
- [ ] Search filters in real-time
- [ ] Filters combine correctly
- [ ] Clear filters works

### Data Table
- [ ] Loads 50 rows on page load
- [ ] All columns display correctly
- [ ] Currency formatting correct
- [ ] Click header sorts ascending
- [ ] Click again sorts descending
- [ ] Pagination controls work
- [ ] Page size works (if configurable)
- [ ] Row hover highlights
- [ ] Export CSV downloads file

### Charts
- [ ] Department bar chart renders
- [ ] Top 15 departments shown
- [ ] Click bar filters table
- [ ] Earnings donut chart renders
- [ ] 4 categories shown
- [ ] Percentages total ~100%
- [ ] Charts update on filter change

### Stats Cards
- [ ] All 4 stats display
- [ ] Numbers formatted correctly
- [ ] Update on filter change

### Responsive Design
- [ ] 1440px: Full layout correct
- [ ] 1024px: Minor adjustments
- [ ] 768px: Charts stack
- [ ] 375px: Mobile layout works
- [ ] Table scrolls horizontally on mobile

### Loading States
- [ ] Spinner shows during load
- [ ] Spinner hides after load
- [ ] Error message on failure

## Phase 4: Integration Testing
**Run after**: Deployment complete
**Time**: 15 minutes

### Production Verification
- [ ] https://bostonpayroll.adamlozo.com loads
- [ ] SSL certificate valid
- [ ] /api/health returns healthy
- [ ] Data present (>100K records)
- [ ] All filters work
- [ ] Charts render
- [ ] Export works

### Cross-Browser
- [ ] Chrome desktop
- [ ] Firefox desktop
- [ ] Safari desktop (if available)
- [ ] Chrome mobile
- [ ] Safari iOS (if available)

### Performance Production
- [ ] Initial load < 3s
- [ ] No console errors
- [ ] No failed network requests

## Final QA Checklist
**Run after**: All phases complete
**Time**: 10 minutes

### Functionality
- [ ] Can find specific employee by name
- [ ] Can see top earners by department
- [ ] Can compare years
- [ ] Can analyze overtime patterns
- [ ] Export produces valid CSV

### Usability
- [ ] Intuitive to use without instructions
- [ ] No confusing UI elements
- [ ] Accessible via keyboard
- [ ] Screen reader compatible (basic)

### Documentation
- [ ] README updated
- [ ] Annual refresh process documented
- [ ] Known issues documented

## Sign-Off

**Tested by**: _______________
**Date**: _______________
**Version**: _______________

### Issues Found
| # | Description | Severity | Status |
|---|-------------|----------|--------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### Approval
- [ ] All critical tests pass
- [ ] No blocking issues
- [ ] Ready for launch
