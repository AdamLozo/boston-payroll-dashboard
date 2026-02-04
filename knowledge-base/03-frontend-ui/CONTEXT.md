# Frontend UI Context

## Overview
Data table focused dashboard for exploring Boston employee compensation. Different design pattern from map-focused dashboards.

## Design Philosophy

### Data Table First
Unlike building permits/restaurants dashboards which are map-centric, this dashboard puts the searchable data table front and center. The table IS the main interaction.

### Design Principles
1. **Dense but readable** - Show lots of data without overwhelming
2. **Instant search** - Client-side filtering for immediate feedback
3. **Sortable everything** - Click any column header to sort
4. **Visual earnings breakdown** - Charts support the table, not replace it
5. **Responsive** - Works on mobile (table scrolls horizontally)

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Boston Employee Earnings Dashboard                      │
│  Subtitle: Explore city employee compensation 2020-2024          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  FILTERS BAR                                                     │
│  ┌──────────┐  ┌─────────────────┐  ┌───────────────────────┐  │
│  │ Year ▼   │  │ Department ▼    │  │ 🔍 Search name/title  │  │
│  │ 2024     │  │ All Departments │  │                       │  │
│  └──────────┘  └─────────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  STATS CARDS (compact row)                                       │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │ 22,456    │ │ $2.3B     │ │ $104,500  │ │ $345M OT  │       │
│  │ Employees │ │ Total     │ │ Average   │ │ Overtime  │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  MAIN DATA TABLE                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Name ▼ │ Department │ Title │ Regular │ OT │ Detail │ Total ││
│  ├────────┼────────────┼───────┼─────────┼────┼────────┼───────┤│
│  │ SMITH  │ Police     │ Ofcr  │ $95,000 │$85K│ $45K   │ $242K ││
│  │ JONES  │ Fire       │ FF    │ $92,000 │$78K│ $38K   │ $225K ││
│  │ ...    │            │       │         │    │        │       ││
│  └─────────────────────────────────────────────────────────────┘│
│  Showing 1-50 of 22,456 | ◀ 1 2 3 4 5 ... 450 ▶  | Export CSV   │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐ ┌────────────────────────────────┐
│  DEPARTMENT BREAKDOWN        │ │  EARNINGS COMPOSITION          │
│  (horizontal bar chart)      │ │  (donut/pie chart)             │
│                              │ │                                │
│  Police ████████████ $456M   │ │      ┌───────────┐            │
│  Fire   ████████ $345M       │ │     /  Regular   \            │
│  Schools████████ $312M       │ │    │   63.9%     │            │
│  ...                         │ │    │  ┌─────┐    │            │
│                              │ │     \ │ OT  │   /             │
│                              │ │      └─────────┘              │
└──────────────────────────────┘ └────────────────────────────────┘
```

## Components

### 1. Header
- Title: "Boston Employee Earnings"
- Subtitle: "Explore city employee compensation 2020-2024"
- Minimal, clean design

### 2. Filter Bar
- **Year Dropdown**: 2024, 2023, 2022, 2021, 2020
- **Department Dropdown**: All departments from API (sorted alphabetically)
- **Search Box**: Live search on name and title (debounced 300ms)

### 3. Stats Cards
Four compact cards in a row:
1. Total Employees (count)
2. Total Payroll (sum, formatted as $2.3B)
3. Average Salary (formatted)
4. Total Overtime (sum)

### 4. Data Table (Primary Component)
**Columns**:
| Column | Width | Sortable | Format |
|--------|-------|----------|--------|
| Name | 200px | Yes | UPPERCASE |
| Department | 180px | Yes | Title Case |
| Title | 150px | Yes | Title Case |
| Regular | 100px | Yes | Currency |
| Overtime | 90px | Yes | Currency |
| Detail | 90px | Yes | Currency |
| Other | 90px | Yes | Currency |
| Total | 110px | Yes | Currency, **bold** |

**Features**:
- Sortable by any column (click header)
- Client-side search (after initial load)
- Pagination (50 per page)
- Row hover highlight
- Export to CSV button

### 5. Department Breakdown Chart
- Horizontal bar chart
- Top 15 departments by total earnings
- Shows department name and total
- Click to filter table

### 6. Earnings Composition Chart
- Donut or pie chart
- Categories: Regular, Overtime, Detail, Other
- Shows percentages
- Legend below

## Color Scheme

**Option A: Professional Blue** (recommended)
```css
--primary: #1a365d;      /* Dark navy header */
--secondary: #2b6cb0;    /* Blue accents */
--background: #f7fafc;   /* Light gray background */
--card-bg: #ffffff;      /* White cards */
--text: #1a202c;         /* Near black text */
--text-muted: #718096;   /* Gray secondary text */
--border: #e2e8f0;       /* Light borders */
--success: #38a169;      /* Green for positive */
--warning: #d69e2e;      /* Yellow for OT */
--accent: #805ad5;       /* Purple for detail */
```

**Earnings Category Colors**:
- Regular: #4299e1 (blue)
- Overtime: #ed8936 (orange)
- Detail: #9f7aea (purple)
- Other: #a0aec0 (gray)

## Typography

```css
--font-heading: 'Inter', -apple-system, sans-serif;
--font-body: 'Inter', -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', monospace;  /* For numbers */

/* Sizes */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
```

## Data Table Library

### Recommended: AG Grid (Community Edition)
**Pros**:
- Excellent performance with large datasets
- Built-in sorting, filtering, pagination
- Good mobile support
- Modern look
- Free for our use case

**Basic Setup**:
```html
<script src="https://cdn.jsdelivr.net/npm/ag-grid-community/dist/ag-grid-community.min.js"></script>
```

```javascript
const gridOptions = {
    columnDefs: [
        { field: 'name', sortable: true, filter: true },
        { field: 'department', sortable: true, filter: true },
        { field: 'title', sortable: true, filter: true },
        { field: 'regular', sortable: true, valueFormatter: currencyFormatter },
        { field: 'overtime', sortable: true, valueFormatter: currencyFormatter },
        { field: 'detail', sortable: true, valueFormatter: currencyFormatter },
        { field: 'total_gross', sortable: true, valueFormatter: currencyFormatter },
    ],
    defaultColDef: {
        resizable: true,
    },
    pagination: true,
    paginationPageSize: 50,
    rowSelection: 'single',
};
```

### Alternative: DataTables
If bundle size is concern:
```html
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
```

## Chart Library

### Chart.js
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

**Department Bar Chart**:
```javascript
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: departments.map(d => d.name),
        datasets: [{
            data: departments.map(d => d.total_earnings),
            backgroundColor: '#4299e1'
        }]
    },
    options: {
        indexAxis: 'y',  // Horizontal bars
        plugins: {
            legend: { display: false }
        }
    }
});
```

**Earnings Donut Chart**:
```javascript
new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Regular', 'Overtime', 'Detail', 'Other'],
        datasets: [{
            data: [63.9, 14.7, 10.0, 11.4],
            backgroundColor: ['#4299e1', '#ed8936', '#9f7aea', '#a0aec0']
        }]
    },
    options: {
        cutout: '60%',
        plugins: {
            legend: { position: 'bottom' }
        }
    }
});
```

## Responsive Behavior

### Desktop (> 1024px)
- Full layout as shown
- Table shows all columns
- Charts side by side

### Tablet (768px - 1024px)
- Charts stack vertically
- Table columns same

### Mobile (< 768px)
- Filters stack vertically
- Stats cards 2x2 grid
- Table scrolls horizontally
- Charts full width, stacked

## Performance Optimization

1. **Initial Load**: Load first 50 rows immediately
2. **Background Load**: Fetch all data for current filters (up to 5000 rows)
3. **Client-Side Search**: After full load, search is instant
4. **Debounce**: 300ms debounce on search input
5. **Lazy Charts**: Load charts after table renders

## File Structure

```
frontend/
├── index.html          # Single HTML file
├── css/
│   └── style.css       # All styles
└── js/
    └── app.js          # All JavaScript
```

## Dependencies (CDN)

```html
<!-- AG Grid -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-grid.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-theme-alpine.css">
<script src="https://cdn.jsdelivr.net/npm/ag-grid-community/dist/ag-grid-community.min.js"></script>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Optional: Number formatting -->
<script src="https://cdn.jsdelivr.net/npm/numeral@2.0.6/numeral.min.js"></script>
```
