# Phase 3: Frontend UI Implementation Plan

> **For Claude:** This plan builds a data table-focused dashboard with vanilla JS.

## Overview
Build responsive frontend UI for Boston Payroll Dashboard with searchable data table, department analytics, and earnings breakdown charts.

## Prerequisites
- [x] Phase 2 complete (API running)
- [x] API endpoints tested and working
- [ ] Frontend directory structure created

## Tasks

### Task 1: Create Basic HTML Structure
**Files:** `frontend/index.html`

**Implementation:**

Create `frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Boston Employee Earnings Dashboard</title>

    <!-- AG Grid -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/styles/ag-grid.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/styles/ag-theme-alpine.css">

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <!-- Custom CSS -->
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <h1>Boston Employee Earnings</h1>
            <p>Explore city employee compensation 2020-2024</p>
        </header>

        <!-- Filters -->
        <div class="filters">
            <select id="year-filter" class="filter-select">
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
                <option value="2021">2021</option>
                <option value="2020">2020</option>
            </select>

            <select id="department-filter" class="filter-select">
                <option value="">All Departments</option>
            </select>

            <input type="text" id="search-input" class="search-input" placeholder="🔍 Search name or title...">

            <button id="export-btn" class="export-btn">Export CSV</button>
        </div>

        <!-- Stats Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="stat-employees">-</div>
                <div class="stat-label">Employees</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-payroll">-</div>
                <div class="stat-label">Total Payroll</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-average">-</div>
                <div class="stat-label">Average Salary</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-overtime">-</div>
                <div class="stat-label">Total Overtime</div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="table-container">
            <div id="employees-grid" class="ag-theme-alpine" style="height: 600px; width: 100%;"></div>
        </div>

        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Top Departments by Total Earnings</h3>
                <canvas id="dept-chart"></canvas>
            </div>
            <div class="chart-card">
                <h3>Earnings Composition</h3>
                <canvas id="earnings-chart"></canvas>
            </div>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p>Data source: <a href="https://data.boston.gov" target="_blank">Analyze Boston</a></p>
            <p>Last updated: 2024</p>
        </footer>
    </div>

    <!-- AG Grid -->
    <script src="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/dist/ag-grid-community.min.js"></script>

    <!-- Custom JS -->
    <script src="js/app.js"></script>
</body>
</html>
```

**Expected Outcome:**
- Clean HTML structure
- All UI elements in place
- CDN libraries loaded

---

### Task 2: Create CSS Styling
**Files:** `frontend/css/style.css`

**Implementation:**

Create `frontend/css/style.css`:
```css
:root {
    --primary: #1a365d;
    --secondary: #2b6cb0;
    --background: #f7fafc;
    --card-bg: #ffffff;
    --text: #1a202c;
    --text-muted: #718096;
    --border: #e2e8f0;
    --success: #38a169;
    --warning: #ed8936;
    --accent: #805ad5;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background-color: var(--background);
    color: var(--text);
    line-height: 1.6;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

/* Header */
.header {
    text-align: center;
    margin-bottom: 30px;
    padding: 40px 20px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    border-radius: 8px;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 8px;
    font-weight: 700;
}

.header p {
    font-size: 1.1rem;
    opacity: 0.9;
}

/* Filters */
.filters {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}

.filter-select, .search-input {
    padding: 10px 16px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 0.95rem;
    background: var(--card-bg);
}

.filter-select {
    min-width: 150px;
}

.search-input {
    flex: 1;
    min-width: 250px;
}

.export-btn {
    padding: 10px 20px;
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    transition: background 0.2s;
}

.export-btn:hover {
    background: var(--secondary);
}

/* Stats Cards */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.stat-card {
    background: var(--card-bg);
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    text-align: center;
}

.stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 4px;
}

.stat-label {
    font-size: 0.875rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Table */
.table-container {
    background: var(--card-bg);
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    padding: 16px;
    margin-bottom: 24px;
}

/* Charts */
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
    margin-bottom: 40px;
}

.chart-card {
    background: var(--card-bg);
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    padding: 24px;
}

.chart-card h3 {
    margin-bottom: 16px;
    font-size: 1.1rem;
    color: var(--primary);
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px 20px;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    margin-top: 40px;
}

.footer a {
    color: var(--secondary);
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .header h1 {
        font-size: 1.75rem;
    }

    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .charts-grid {
        grid-template-columns: 1fr;
    }

    .filters {
        flex-direction: column;
    }

    .filter-select, .search-input {
        width: 100%;
    }
}
```

**Expected Outcome:**
- Professional blue color scheme
- Responsive layout
- Clean, modern design

---

### Task 3: Create JavaScript Application
**Files:** `frontend/js/app.js`

**Implementation:**

Create `frontend/js/app.js`:
```javascript
// API Configuration
const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:8001'
    : '';

// Global state
let currentYear = 2024;
let currentDepartment = '';
let employeesData = [];
let grid = null;

// Format currency
function formatCurrency(value) {
    if (value >= 1000000) {
        return '$' + (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
        return '$' + (value / 1000).toFixed(0) + 'K';
    }
    return '$' + value.toLocaleString();
}

function formatCurrencyFull(value) {
    return '$' + Number(value).toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadDepartments();
    setupEventListeners();
    await loadData();
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('year-filter').addEventListener('change', (e) => {
        currentYear = parseInt(e.target.value);
        loadData();
    });

    document.getElementById('department-filter').addEventListener('change', (e) => {
        currentDepartment = e.target.value;
        loadData();
    });

    let searchTimeout;
    document.getElementById('search-input').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (grid) {
                grid.api.setQuickFilter(e.target.value);
            }
        }, 300);
    });

    document.getElementById('export-btn').addEventListener('click', exportCSV);
}

// Load departments for dropdown
async function loadDepartments() {
    try {
        const response = await fetch(`${API_BASE}/api/departments?year=${currentYear}`);
        const data = await response.json();

        const select = document.getElementById('department-filter');
        select.innerHTML = '<option value="">All Departments</option>';

        data.departments
            .sort((a, b) => a.name.localeCompare(b.name))
            .forEach(dept => {
                const option = document.createElement('option');
                option.value = dept.name;
                option.textContent = dept.name;
                select.appendChild(option);
            });
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

// Load all data
async function loadData() {
    await Promise.all([
        loadEmployees(),
        loadStats(),
        loadCharts()
    ]);
}

// Load employees data
async function loadEmployees() {
    try {
        let url = `${API_BASE}/api/employees?year=${currentYear}&limit=5000`;
        if (currentDepartment) {
            url += `&department=${encodeURIComponent(currentDepartment)}`;
        }

        const response = await fetch(url);
        const data = await response.json();
        employeesData = data.data;

        if (!grid) {
            initializeGrid();
        } else {
            grid.api.setRowData(employeesData);
        }
    } catch (error) {
        console.error('Error loading employees:', error);
    }
}

// Initialize AG Grid
function initializeGrid() {
    const columnDefs = [
        {
            field: 'name',
            headerName: 'Name',
            width: 200,
            pinned: 'left',
            cellStyle: { fontWeight: '600' }
        },
        {
            field: 'department',
            headerName: 'Department',
            width: 180
        },
        {
            field: 'title',
            headerName: 'Title',
            width: 180
        },
        {
            field: 'regular',
            headerName: 'Regular',
            width: 120,
            type: 'numericColumn',
            valueFormatter: params => formatCurrencyFull(params.value)
        },
        {
            field: 'overtime',
            headerName: 'Overtime',
            width: 120,
            type: 'numericColumn',
            valueFormatter: params => formatCurrencyFull(params.value)
        },
        {
            field: 'detail',
            headerName: 'Detail',
            width: 110,
            type: 'numericColumn',
            valueFormatter: params => formatCurrencyFull(params.value)
        },
        {
            field: 'other',
            headerName: 'Other',
            width: 110,
            type: 'numericColumn',
            valueFormatter: params => formatCurrencyFull(params.value)
        },
        {
            field: 'total_gross',
            headerName: 'Total',
            width: 130,
            type: 'numericColumn',
            valueFormatter: params => formatCurrencyFull(params.value),
            cellStyle: { fontWeight: '700', color: '#1a365d' }
        }
    ];

    const gridOptions = {
        columnDefs: columnDefs,
        rowData: employeesData,
        defaultColDef: {
            sortable: true,
            filter: true,
            resizable: true
        },
        pagination: true,
        paginationPageSize: 50,
        domLayout: 'normal'
    };

    const gridDiv = document.getElementById('employees-grid');
    grid = agGrid.createGrid(gridDiv, gridOptions);
}

// Load stats
async function loadStats() {
    try {
        let url = `${API_BASE}/api/stats?year=${currentYear}`;
        if (currentDepartment) {
            url += `&department=${encodeURIComponent(currentDepartment)}`;
        }

        const response = await fetch(url);
        const stats = await response.json();

        document.getElementById('stat-employees').textContent =
            stats.total_employees.toLocaleString();
        document.getElementById('stat-payroll').textContent =
            formatCurrency(stats.total_payroll);
        document.getElementById('stat-average').textContent =
            formatCurrencyFull(stats.avg_salary);
        document.getElementById('stat-overtime').textContent =
            formatCurrency(stats.total_overtime);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load and render charts
async function loadCharts() {
    await Promise.all([
        loadDepartmentChart(),
        loadEarningsChart()
    ]);
}

// Department bar chart
async function loadDepartmentChart() {
    try {
        const response = await fetch(`${API_BASE}/api/departments?year=${currentYear}`);
        const data = await response.json();

        const top10 = data.departments.slice(0, 10);

        const ctx = document.getElementById('dept-chart').getContext('2d');

        // Destroy existing chart if it exists
        if (window.deptChart) {
            window.deptChart.destroy();
        }

        window.deptChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: top10.map(d => d.name.length > 25 ? d.name.substring(0, 25) + '...' : d.name),
                datasets: [{
                    label: 'Total Earnings',
                    data: top10.map(d => d.total_earnings),
                    backgroundColor: '#2b6cb0'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => formatCurrency(context.raw)
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            callback: value => formatCurrency(value)
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading department chart:', error);
    }
}

// Earnings composition donut chart
async function loadEarningsChart() {
    try {
        let url = `${API_BASE}/api/earnings-breakdown?year=${currentYear}`;
        if (currentDepartment) {
            url += `&department=${encodeURIComponent(currentDepartment)}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        const ctx = document.getElementById('earnings-chart').getContext('2d');

        // Destroy existing chart if it exists
        if (window.earningsChart) {
            window.earningsChart.destroy();
        }

        window.earningsChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Regular', 'Overtime', 'Detail', 'Retro', 'Other', 'Injured', 'Quinn Ed'],
                datasets: [{
                    data: [
                        data.percentages.regular,
                        data.percentages.overtime,
                        data.percentages.detail,
                        data.percentages.retro,
                        data.percentages.other,
                        data.percentages.injured,
                        data.percentages.quinn_education
                    ],
                    backgroundColor: [
                        '#4299e1',
                        '#ed8936',
                        '#9f7aea',
                        '#48bb78',
                        '#a0aec0',
                        '#f56565',
                        '#38b2ac'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                return `${label}: ${value.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading earnings chart:', error);
    }
}

// Export CSV
async function exportCSV() {
    try {
        let url = `${API_BASE}/api/export?year=${currentYear}`;
        if (currentDepartment) {
            url += `&department=${encodeURIComponent(currentDepartment)}`;
        }

        window.location.href = url;
    } catch (error) {
        console.error('Error exporting CSV:', error);
        alert('Error exporting data');
    }
}
```

**Test Command:**
```bash
# Start backend API (if not running)
cd ~/OneDrive/Claude/Projects/boston-payroll-dashboard
python -c "from backend.main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001)" &

# Open frontend in browser
open frontend/index.html  # or use a local server
```

**Expected Outcome:**
- Interactive data table with sorting
- Live search functionality
- Department and earnings charts
- Stats cards with current data
- CSV export working

---

## Completion Criteria

- [ ] HTML structure complete
- [ ] CSS styling applied and responsive
- [ ] JavaScript app connects to API
- [ ] Data table loads and displays data
- [ ] Filters work (year, department, search)
- [ ] Stats cards show correct data
- [ ] Charts render correctly
- [ ] CSV export works
- [ ] Mobile responsive

## Notes

- Frontend uses CDN for all libraries (no build step)
- Vanilla JavaScript (no frameworks)
- Works with Phase 2 API on port 8001
- Ready for Render deployment

