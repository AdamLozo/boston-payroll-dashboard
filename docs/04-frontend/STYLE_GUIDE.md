# Style Guide: Data Table Focus

## Design Principles

1. **Content Density** - Show more data, less whitespace (unlike map dashboards)
2. **Scannable** - Easy to scan columns, find outliers
3. **Sortable Everything** - Every column clickable
4. **Professional** - Think Bloomberg/Excel, not consumer app

## Key Differences from Map Dashboards

| Aspect | Map Dashboard | Data Table Dashboard |
|--------|---------------|----------------------|
| Primary element | Map (60% viewport) | Table (80% viewport) |
| Whitespace | Generous | Minimal |
| Font size | 14-16px | 12-14px |
| Row height | N/A | Compact (36px) |
| Mobile | Map simplifies | Table scrolls |

## CSS Framework: None (Vanilla)

Keep it simple. No Bootstrap, Tailwind, etc. Just clean vanilla CSS.

## Core Styles

```css
/* Reset & Base */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    --primary: #1a365d;
    --secondary: #2c5282;
    --accent: #ed8936;
    --bg: #f7fafc;
    --surface: #ffffff;
    --text: #1a202c;
    --text-muted: #718096;
    --border: #e2e8f0;
    --success: #38a169;
    --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

body {
    font-family: var(--font);
    font-size: 14px;
    line-height: 1.5;
    background: var(--bg);
    color: var(--text);
}

/* Header */
.header {
    background: var(--primary);
    color: white;
    padding: 1rem 2rem;
}

.header h1 {
    font-size: 1.5rem;
    font-weight: 600;
}

.header .subtitle {
    font-size: 0.875rem;
    opacity: 0.8;
}

/* Stats Bar */
.stats-bar {
    display: flex;
    gap: 1rem;
    padding: 1rem 2rem;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
}

.stat-card {
    flex: 1;
    text-align: center;
    padding: 0.75rem;
}

.stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--primary);
}

.stat-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Filters */
.filters {
    display: flex;
    gap: 1rem;
    padding: 1rem 2rem;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.filter-group label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
}

.filter-group select,
.filter-group input {
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 0.875rem;
    min-width: 150px;
}

.filter-group input[type="search"] {
    min-width: 250px;
}

/* Main Container */
.main-content {
    padding: 1rem 2rem;
}

/* Table Container */
.table-container {
    background: var(--surface);
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    overflow: hidden;
}

/* DataTables Overrides */
.dataTables_wrapper {
    padding: 0;
}

table.dataTable {
    border-collapse: collapse;
    width: 100%;
}

table.dataTable thead th {
    background: var(--bg);
    border-bottom: 2px solid var(--border);
    padding: 0.75rem 1rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
}

table.dataTable tbody td {
    padding: 0.5rem 1rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.8125rem;
}

table.dataTable tbody tr:hover {
    background: #edf2f7;
}

/* Currency columns */
.currency-col {
    font-family: 'SF Mono', Monaco, 'Courier New', monospace;
    font-size: 0.8125rem;
}

.total-col {
    font-weight: 600;
    color: var(--primary);
}

/* Name column */
.name-col {
    font-weight: 500;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Department column */
.dept-col {
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Pagination */
.dataTables_paginate {
    padding: 1rem;
    text-align: right;
}

.dataTables_paginate .paginate_button {
    padding: 0.5rem 0.75rem;
    margin: 0 0.125rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    cursor: pointer;
}

.dataTables_paginate .paginate_button.current {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
}

/* Info text */
.dataTables_info {
    padding: 1rem;
    font-size: 0.8125rem;
    color: var(--text-muted);
}

/* Loading */
.dataTables_processing {
    background: rgba(255,255,255,0.9);
    padding: 2rem;
    text-align: center;
}

/* Footer */
.footer {
    padding: 1.5rem 2rem;
    text-align: center;
    font-size: 0.8125rem;
    color: var(--text-muted);
}

.footer a {
    color: var(--secondary);
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
    .stats-bar {
        flex-wrap: wrap;
    }
    
    .stat-card {
        flex: 0 0 48%;
    }
    
    .filters {
        flex-direction: column;
    }
    
    .filter-group select,
    .filter-group input {
        width: 100%;
    }
    
    .header, .main-content, .filters, .stats-bar, .footer {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
```

## Icons

Use simple Unicode or no icons. Keep it clean.

```html
<!-- Search icon in input -->
<input type="search" placeholder="🔍 Search by name...">

<!-- Or use CSS pseudo-element -->
```

## No Animations

Skip animations. This is a data tool, not a marketing site.
