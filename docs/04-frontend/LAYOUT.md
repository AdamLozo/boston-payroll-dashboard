# Frontend Layout Specification

## Design Philosophy

**Data Table First** - Unlike the map-centric building permits/restaurant dashboards, this is a data exploration tool. The table IS the primary interface.

## Page Structure

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER                                                       │
│ Boston Employee Earnings Dashboard                           │
│ Explore city employee compensation 2020-2024                 │
├─────────────────────────────────────────────────────────────┤
│ STATS BAR                                                    │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│ │ 23,456  │ │ $1.85B  │ │ $234M   │ │ $123M   │            │
│ │Employees│ │ Total   │ │Overtime │ │ Detail  │            │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
├─────────────────────────────────────────────────────────────┤
│ FILTERS                                                      │
│ ┌──────────┐ ┌─────────────────────┐ ┌────────────────────┐ │
│ │ 2024 ▼   │ │ All Departments ▼   │ │ 🔍 Search name...  │ │
│ └──────────┘ └─────────────────────┘ └────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ MAIN CONTENT AREA                                            │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │                   DATA TABLE                            │ │
│ │  Name | Department | Title | Regular | OT | Total ▼    │ │
│ │  -----|------------|-------|---------|----|---------   │ │
│ │  ...  | ...        | ...   | ...     |... | ...        │ │
│ │                                                         │ │
│ │  Showing 1-100 of 23,456     < 1 2 3 ... 235 >         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ CHARTS (Collapsible)                                        │
│ ┌─────────────────────────┐ ┌─────────────────────────────┐ │
│ │  Department Breakdown   │ │  Earnings Composition       │ │
│ │  [Horizontal Bar Chart] │ │  [Stacked Bar / Pie]        │ │
│ └─────────────────────────┘ └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ FOOTER                                                       │
│ Data: Analyze Boston | Built by Adam Lozo | © 2024          │
└─────────────────────────────────────────────────────────────┘
```

## Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| Desktop (>1200px) | Full layout, table shows all columns |
| Tablet (768-1200px) | Charts stack vertically, table scrolls horizontally |
| Mobile (<768px) | Simplified table (Name, Dept, Total only), charts hidden |

## Component Specifications

### Header
- Clean, minimal
- Title: "Boston Employee Earnings"
- Subtitle: "Explore city employee compensation 2020-2024"
- No logo, no nav (single-page app)

### Stats Bar
- 4 KPI cards in a row
- Large numbers (format with commas/abbreviations)
- Small labels below
- Update on filter change

### Filters
- Year dropdown (default: 2024)
- Department dropdown (all departments from data)
- Search input (debounced, 300ms)
- All filters update table + stats simultaneously

### Data Table (Primary)
- Server-side pagination
- Sortable columns (click header)
- 100 rows per page (configurable)
- Columns: Name, Department, Title, Regular, OT, Detail, Total
- Highlight rows on hover
- Click row to expand details (optional)

### Charts (Secondary)
- Collapsible/toggle section
- Department breakdown: Top 10 horizontal bar
- Earnings composition: Stacked bar or pie

## Color Palette

```css
:root {
  --primary: #1a365d;      /* Dark blue - headers */
  --secondary: #2c5282;    /* Medium blue - accents */
  --accent: #ed8936;       /* Orange - highlights, total column */
  --background: #f7fafc;   /* Light gray - page bg */
  --surface: #ffffff;      /* White - cards, table */
  --text: #1a202c;         /* Near black - body text */
  --text-muted: #718096;   /* Gray - labels */
  --border: #e2e8f0;       /* Light border */
  --success: #38a169;      /* Green - positive values */
  --warning: #d69e2e;      /* Yellow - caution */
}
```

## Typography

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.5;
}

h1 { font-size: 1.75rem; font-weight: 600; }
.stat-value { font-size: 2rem; font-weight: 700; }
.table-header { font-size: 0.75rem; text-transform: uppercase; }
```
