# Claude Code Quick Start

> **Purpose**: Get Claude Code up to speed in 30 seconds.

## Project Summary
Boston Employee Earnings Dashboard - searchable data table for city payroll data (2020-2024).

## Key Files to Read First
1. `MASTER_PLAN.md` - Full project overview
2. `knowledge-base/00-overview/CONTEXT.md` - Requirements
3. `knowledge-base/00-overview/ARCHITECTURE.md` - System design

## Current Status
**Phase**: Ready to start Phase 1 (Data Layer)

## Quick Commands

### Start Phase 1 (Data Layer)
```
Read knowledge-base/01-data-layer/CONTEXT.md and CHECKLIST.md, then implement the data layer
```

### Start Phase 2 (Backend API)
```
Read knowledge-base/02-backend-api/CONTEXT.md and CHECKLIST.md, then implement the API
```

### Start Phase 3 (Frontend UI)
```
Read knowledge-base/03-frontend-ui/CONTEXT.md and CHECKLIST.md, then implement the frontend. Use @frontend-design skill.
```

### Start Phase 4 (Deployment)
```
Read knowledge-base/04-deployment/CONTEXT.md and CHECKLIST.md, then deploy to Render
```

## Critical Constraints
- **Database**: Shared PostgreSQL - prefix tables with `payroll_`
- **No cron job**: Manual annual refresh
- **Design**: Data table focused, NOT map-focused

## Resource IDs (Don't Search - Use These)
```python
RESOURCE_IDS = {
    2024: "579a4be3-9ca7-4183-bc95-7d67ee715b6d",
    2023: "6b3c5333-1dcb-4b3d-9cd7-6a03fb526da7",
    2022: "63ac638b-36c4-487d-9453-1d83eb5090d2",
    2021: "ec5aaf93-1509-4641-9310-28e62e028457",
    2020: "e2e2c23a-6fc7-4456-8751-5321d8aa869b",
}
CSV_URL = "https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/{resource_id}/download"
```

## Don't Ask About
- URL (it's bostonpayroll.adamlozo.com)
- Database (share existing Render PostgreSQL)
- Design style (data table focused)
- Year range (2020-2024 only)
- Automation (manual annual refresh)

## Skills to Use
- `@frontend-design` for Phase 3
- `@sql-fundamentals` for Phase 1

## Stop and Ask If
- Database connection fails
- CSV download fails
- Schema needs changes
- Design decisions unclear
