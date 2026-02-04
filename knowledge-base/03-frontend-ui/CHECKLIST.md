# Frontend UI Implementation Checklist

## Prerequisites
- [ ] Phase 2 (Backend API) complete
- [ ] API running at localhost:8000
- [ ] All endpoints returning data

## Tasks

### Task 1: HTML Structure
**Files**: `frontend/index.html`
**Time**: 15 minutes

- [ ] Create HTML boilerplate
- [ ] Add CDN links (AG Grid, Chart.js)
- [ ] Create header section
- [ ] Create filter bar structure
- [ ] Create stats cards row
- [ ] Create table container
- [ ] Create chart containers
- [ ] Add footer

**Verification**:
```bash
# Open in browser
open frontend/index.html
# Should show basic structure (empty)
```

### Task 2: CSS Styling
**Files**: `frontend/css/style.css`
**Time**: 20 minutes

- [ ] Define CSS variables (colors, fonts)
- [ ] Style header
- [ ] Style filter bar
- [ ] Style stats cards
- [ ] Style table container
- [ ] Style chart containers
- [ ] Add responsive breakpoints
- [ ] Style buttons and inputs

**Verification**:
- Visual inspection at desktop width
- Visual inspection at mobile width (Chrome DevTools)

### Task 3: API Service Functions
**Files**: `frontend/js/app.js`
**Time**: 10 minutes

- [ ] Create fetchYears() function
- [ ] Create fetchEmployees() function
- [ ] Create fetchDepartments() function
- [ ] Create fetchStats() function
- [ ] Create fetchEarningsBreakdown() function
- [ ] Add error handling

**Verification**:
```javascript
// In browser console
fetchYears().then(console.log)
// Should log: {years: [2024, 2023, ...]}
```

### Task 4: Filter Controls
**Files**: `frontend/js/app.js`
**Time**: 15 minutes

- [ ] Populate year dropdown from API
- [ ] Populate department dropdown from API
- [ ] Wire up year change handler
- [ ] Wire up department change handler
- [ ] Wire up search input with debounce
- [ ] Store current filter state

**Verification**:
- Change year → Console logs new year
- Change department → Console logs new department
- Type in search → Console logs search term (after 300ms)

### Task 5: Stats Cards
**Files**: `frontend/js/app.js`
**Time**: 10 minutes

- [ ] Fetch stats on page load
- [ ] Update stats on filter change
- [ ] Format numbers (currency, abbreviations)
- [ ] Handle loading state

**Verification**:
- Page load shows stats
- Change year → Stats update
- Change department → Stats update

### Task 6: AG Grid Data Table
**Files**: `frontend/js/app.js`
**Time**: 30 minutes

- [ ] Initialize AG Grid with column definitions
- [ ] Configure currency formatters
- [ ] Enable sorting
- [ ] Enable pagination
- [ ] Load initial data from API
- [ ] Update data on filter change
- [ ] Implement client-side search
- [ ] Add export to CSV button
- [ ] Style grid theme

**Verification**:
- Table shows 50 rows
- Click column header → Sorts
- Click pagination → Changes page
- Type in search → Filters instantly
- Click Export → Downloads CSV

### Task 7: Department Bar Chart
**Files**: `frontend/js/app.js`
**Time**: 15 minutes

- [ ] Create horizontal bar chart
- [ ] Load top 15 departments
- [ ] Format currency on tooltips
- [ ] Update on filter change
- [ ] Add click handler to filter table

**Verification**:
- Chart shows departments
- Hover shows tooltip with amount
- Click bar → Table filters to that department

### Task 8: Earnings Composition Chart
**Files**: `frontend/js/app.js`
**Time**: 15 minutes

- [ ] Create donut chart
- [ ] Show Regular, OT, Detail, Other
- [ ] Show percentages in legend
- [ ] Update on filter change

**Verification**:
- Chart shows 4 categories
- Percentages match API response
- Change filters → Chart updates

### Task 9: Loading States
**Files**: `frontend/js/app.js`, `frontend/css/style.css`
**Time**: 10 minutes

- [ ] Add loading spinner component
- [ ] Show spinner while fetching
- [ ] Hide spinner when complete
- [ ] Handle errors gracefully

**Verification**:
- Refresh page → See spinner briefly
- Disconnect network → See error message

### Task 10: Responsive Design
**Files**: `frontend/css/style.css`
**Time**: 15 minutes

- [ ] Test at 1440px (desktop)
- [ ] Test at 1024px (small desktop)
- [ ] Test at 768px (tablet)
- [ ] Test at 375px (mobile)
- [ ] Fix any layout issues
- [ ] Ensure table scrolls horizontally on mobile

**Verification**:
- Chrome DevTools responsive mode
- Test all breakpoints
- All content accessible

### Task 11: Polish and Accessibility
**Files**: All frontend files
**Time**: 15 minutes

- [ ] Add proper ARIA labels
- [ ] Ensure keyboard navigation works
- [ ] Add focus states
- [ ] Check color contrast
- [ ] Add loading="lazy" to images if any
- [ ] Minify CSS/JS for production (optional)

**Verification**:
- Tab through all controls
- Screen reader test (basic)
- Lighthouse accessibility score > 80

## Completion Criteria

- [ ] All filters work correctly
- [ ] Table loads and sorts
- [ ] Search is instant
- [ ] Charts render and update
- [ ] Mobile layout works
- [ ] No console errors
- [ ] Export to CSV works

## Browser Testing

Test in:
- [ ] Chrome (primary)
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Mobile Chrome
- [ ] Mobile Safari (if available)

## Performance Checklist

- [ ] Initial load < 3 seconds
- [ ] Table interaction < 100ms
- [ ] Search response < 100ms
- [ ] Filter change < 500ms
- [ ] No memory leaks (check DevTools)

## Handoff to Phase 4

After completing this phase:
1. Frontend works locally with API
2. All features implemented
3. Ready for deployment

Files to deploy:
```
frontend/
├── index.html
├── css/style.css
└── js/app.js
```
