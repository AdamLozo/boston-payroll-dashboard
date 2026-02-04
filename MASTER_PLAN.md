# Boston Payroll Dashboard - Master Plan

> **Co-Founder Operating Agreement**: This document is the source of truth. Claude Code or any Claude instance can pick up any section and build it without asking questions.

## Quick Stats
| Metric | Value |
|--------|-------|
| URL | bostonpayroll.adamlozo.com |
| Data | 5 years (2020-2024), ~100K-125K records |
| Database | Shared Render PostgreSQL |
| Style | Data table focused (new design) |
| Est. Build Time | 4-6 hours total |

---

## Knowledge Base Structure

```
knowledge-base/
├── 00-overview/
│   ├── CONTEXT.md          # Project vision, use cases, constraints
│   ├── ARCHITECTURE.md     # System architecture diagram
│   └── DECISIONS.md        # Key decisions and rationale
│
├── 01-data-layer/
│   ├── CONTEXT.md          # Schema, data sources, sync strategy
│   ├── CHECKLIST.md        # Implementation tasks
│   ├── PATTERNS.md         # SQL patterns, upsert logic
│   └── SAMPLE_DATA.md      # Example records for testing
│
├── 02-backend-api/
│   ├── CONTEXT.md          # FastAPI endpoints, business logic
│   ├── CHECKLIST.md        # Implementation tasks
│   ├── PATTERNS.md         # API patterns, response formats
│   └── OPENAPI.md          # API specification
│
├── 03-frontend-ui/
│   ├── CONTEXT.md          # UI requirements, components
│   ├── CHECKLIST.md        # Implementation tasks
│   ├── PATTERNS.md         # HTML/JS patterns, DataTables config
│   ├── DESIGN_SPEC.md      # Visual design specification
│   └── MOCKUPS.md          # ASCII mockups of key views
│
├── 04-deployment/
│   ├── CONTEXT.md          # Render config, DNS, environment
│   ├── CHECKLIST.md        # Deployment steps
│   └── RUNBOOK.md          # Operational procedures
│
└── 05-testing/
    ├── CONTEXT.md          # Test strategy
    ├── CHECKLIST.md        # QA checklist
    └── QUERIES.md          # Validation SQL queries
```

---

## Build Sequence

### Phase 1: Data Layer (Claude Code)
**Time**: 45 minutes | **Skill**: `@sql-fundamentals`

1. Create PostgreSQL schema in shared database
2. Build CSV download + parse script
3. Implement upsert logic with year column
4. Load all 5 years of data
5. Validate record counts

**Handoff artifact**: `SELECT COUNT(*), year FROM boston_earnings GROUP BY year`

### Phase 2: Backend API (Claude Code)
**Time**: 45 minutes | **Skill**: None specific

1. FastAPI app with health check
2. `/api/employees` - paginated, searchable
3. `/api/departments` - aggregations
4. `/api/stats` - summary statistics
5. `/api/earnings-breakdown` - composition data

**Handoff artifact**: Working API at localhost:8000

### Phase 3: Frontend UI (Claude.ai Project)
**Time**: 90 minutes | **Skill**: `@frontend-design`

1. Design system (colors, typography)
2. Data table with search/sort/filter
3. Department breakdown charts
4. Earnings composition visualization
5. Responsive layout

**Handoff artifact**: Static HTML/JS files

### Phase 4: Deployment (Claude Code)
**Time**: 30 minutes

1. Create Render web service
2. Configure DNS at GoDaddy
3. Run initial data load
4. Verify production

**Handoff artifact**: Live at bostonpayroll.adamlozo.com

### Phase 5: Testing & Polish (Claude.ai)
**Time**: 30 minutes

1. Cross-browser testing
2. Mobile responsiveness
3. Edge case handling
4. Documentation

---

## When to Use What

### Claude Code (Terminal)
Best for:
- Database operations (schema, migrations, data loading)
- Backend API development (FastAPI, Python)
- File system operations
- Git operations
- Deployment scripts
- Anything requiring multiple file edits in sequence

Use command: `claude` in project directory

### Claude.ai Project
Best for:
- Frontend design discussions
- Complex UI component design
- Code review
- Architecture decisions
- Documentation writing
- Brainstorming sessions

Create project: "Boston Payroll Dashboard" with knowledge-base attached

### Claude.ai Chat (This Interface)
Best for:
- Quick questions
- Planning sessions
- File generation
- Research
- Debugging specific issues

---

## Skills Integration

### Must Use
| Skill | When | Why |
|-------|------|-----|
| `@frontend-design` | Phase 3 | Data table focused design, avoid generic AI aesthetics |
| `@sql-fundamentals` | Phase 1 | Complex queries for aggregations |
| `@writing-plans` | Before each phase | Create detailed implementation plans |
| `@executing-plans` | During each phase | Systematic task execution |

### Optional
| Skill | When | Why |
|-------|------|-----|
| `@brainstorming` | If stuck on design | Explore alternatives |
| `@excel-expertise` | If CSV parsing issues | Handle encoding/format issues |

---

## Automation Opportunities

### 10x Speed Boosters

1. **Template Clone Script**
   ```bash
   # Create in knowledge-base/scripts/
   # Clones boston-data-dashboard, renames, updates config
   ```

2. **Schema Generator**
   - Input: CSV sample
   - Output: PostgreSQL CREATE TABLE + indexes

3. **API Endpoint Generator**
   - Input: Table schema
   - Output: FastAPI CRUD endpoints

4. **Render Deploy Script**
   ```bash
   # One-click: create service, set env vars, deploy
   ```

5. **DNS Automation**
   - GoDaddy API for subdomain creation

### Future MCP Servers to Build

1. **Analyze Boston MCP**
   - Direct dataset discovery
   - Schema inference
   - Data preview

2. **Render MCP** (already have!)
   - Use existing `render:` tools

3. **GoDaddy DNS MCP**
   - Subdomain management
   - SSL verification

---

## Context Files to Generate

The following files will be created in the knowledge-base:

1. `00-overview/CONTEXT.md` - ✅ Will create
2. `01-data-layer/CONTEXT.md` - ✅ Will create  
3. `02-backend-api/CONTEXT.md` - ✅ Will create
4. `03-frontend-ui/CONTEXT.md` - ✅ Will create
5. `04-deployment/CONTEXT.md` - ✅ Will create
6. `05-testing/CONTEXT.md` - ✅ Will create

---

## Success Criteria

- [ ] 100K+ records loaded in < 5 minutes
- [ ] API response < 200ms for 1000 records
- [ ] Table renders in < 1 second
- [ ] Search is instant (client-side)
- [ ] Mobile works (responsive)
- [ ] Lighthouse score > 80

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| CSV format changes year-to-year | Document field mapping per year |
| Large data slows frontend | Server-side pagination, client-side for filtered |
| Shared DB conflicts | Prefix all tables with `payroll_` |
| Annual refresh forgotten | Document process, consider calendar reminder |

---

## Next Action

Run this in Claude Code:
```
Read MASTER_PLAN.md and 00-overview/CONTEXT.md, then start Phase 1 data layer implementation
```

Or continue in this chat:
```
Let's start Phase 1 - create the knowledge-base context files
```
