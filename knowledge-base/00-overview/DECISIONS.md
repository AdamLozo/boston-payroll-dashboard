# Key Decisions

## Decision Log

### D1: Data Table Focus vs Map Focus
**Decision**: Data table focused design
**Date**: 2026-02-04
**Rationale**: 
- Dataset only has ZIP codes, no lat/long coordinates
- Primary use cases are search and comparison, not geographic exploration
- Enables richer filtering and sorting capabilities
- Differentiates from existing map-focused dashboards

**Alternatives Considered**:
- ZIP code choropleth map (rejected: less useful than table)
- Hybrid map + table (rejected: complexity without benefit)

---

### D2: 5 Years vs All Years
**Decision**: Load only 2020-2024 (5 years)
**Date**: 2026-02-04
**Rationale**:
- Sufficient for trend analysis
- Keeps data volume manageable (~100K vs ~200K records)
- Pre-2020 data less relevant for current analysis
- Can expand later if needed

**Alternatives Considered**:
- All 14 years (rejected: unnecessary data, slower queries)
- Last 3 years (rejected: too short for trends)

---

### D3: Shared Database vs Dedicated
**Decision**: Share existing Render PostgreSQL
**Date**: 2026-02-04
**Rationale**:
- Cost savings ($7/mo Starter plan shared across projects)
- Simpler infrastructure management
- Sufficient capacity for ~100K additional records
- Table prefixing prevents conflicts

**Alternatives Considered**:
- Dedicated database (rejected: unnecessary cost)
- SQLite file (rejected: doesn't scale, no concurrent access)

**Mitigation**:
- All tables prefixed with `payroll_`
- Document in shared DB schema registry

---

### D4: DataTables vs AG Grid vs Custom
**Decision**: TBD - Evaluate during Phase 3
**Options**:

| Library | Pros | Cons |
|---------|------|------|
| DataTables | Free, mature, simple | Less modern, jQuery dependency |
| AG Grid Free | Powerful, modern | Larger bundle, more complex |
| Custom | Full control | Development time |

**Evaluation Criteria**:
1. Bundle size (target < 100KB)
2. Search performance (100K rows)
3. Mobile experience
4. Export capability (CSV)

---

### D5: Server-Side vs Client-Side Pagination
**Decision**: Hybrid approach
**Date**: 2026-02-04
**Rationale**:
- Initial load: Server-side (paginated API, 50 rows default)
- After filter: Client-side (load all filtered results, up to 5000)
- Search: Client-side (instant feedback)

**Why Hybrid**:
- Full dataset too large for client (100K rows = ~20MB JSON)
- Filtered datasets usually small enough (< 5000 rows)
- Search needs instant response (no API round-trip)

---

### D6: No Automated Sync
**Decision**: Manual annual refresh
**Date**: 2026-02-04
**Rationale**:
- Data updates once per year
- Cron job overhead not worth it for annual updates
- Manual process documented in runbook
- Calendar reminder for refresh

**Process**:
1. Check Analyze Boston for new year's CSV (typically January/February)
2. Run load script with new year parameter
3. Verify record counts
4. Update UI year filter

---

### D7: Earnings Composition Calculation
**Decision**: Pre-calculate in database
**Rationale**:
- Consistent across all views
- Handles edge cases (nulls, negatives) once
- Faster API responses

**Categories**:
```sql
-- Composition breakdown
regular_pct = regular / NULLIF(total_gross, 0) * 100
overtime_pct = overtime / NULLIF(total_gross, 0) * 100
detail_pct = detail / NULLIF(total_gross, 0) * 100
other_pct = (retro + other + injured + quinn_education) / NULLIF(total_gross, 0) * 100
```

---

### D8: Name Privacy
**Decision**: Display full names as provided
**Date**: 2026-02-04
**Rationale**:
- Data is already public record
- Source dataset includes full names
- Consistent with original Analyze Boston data
- No additional privacy exposure

**Note**: This is public government salary data, not private information.

---

## Pending Decisions

### P1: Chart Library
**Options**: Chart.js, Recharts, D3.js
**Decide By**: Phase 3 start
**Criteria**: Bundle size, ease of use, visual quality

### P2: CSS Framework
**Options**: Tailwind, Bootstrap, Custom
**Decide By**: Phase 3 start
**Criteria**: Developer speed, bundle size, design flexibility

### P3: Export Functionality
**Options**: CSV only, CSV + Excel, PDF
**Decide By**: Phase 3
**Criteria**: User need, implementation effort
