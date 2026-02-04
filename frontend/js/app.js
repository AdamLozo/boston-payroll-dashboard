// API Configuration
const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:8001'
    : '';

// Global state
let currentYear = 2024;
let currentDepartment = '';
let employeesData = [];
let grid = null;
let isFilteringFromChart = false; // Prevent circular filtering

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
    // Register datalabels plugin globally
    Chart.register(ChartDataLabels);

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
        if (!isFilteringFromChart) {
            currentDepartment = e.target.value;
            loadData();
        }
    });

    let searchTimeout;
    document.getElementById('search-input').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (grid) {
                grid.api.setGridOption('quickFilterText', e.target.value);
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
            grid.api.setGridOption('rowData', employeesData);
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
            field: 'total_gross',
            headerName: 'Total',
            width: 130,
            type: 'numericColumn',
            valueFormatter: params => formatCurrencyFull(params.value),
            cellStyle: { fontWeight: '700', color: '#1a365d' }
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

// Department bar chart with click handler
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
                    backgroundColor: top10.map(d =>
                        d.name === currentDepartment ? '#1a365d' : '#2b6cb0'
                    ),
                    fullNames: top10.map(d => d.name), // Store full names for filtering
                    employeeCounts: top10.map(d => d.employee_count),
                    avgSalaries: top10.map(d => d.avg_salary),
                    avgOvertimes: top10.map(d => d.avg_overtime)
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const fullName = window.deptChart.data.datasets[0].fullNames[index];

                        // Toggle filter
                        isFilteringFromChart = true;
                        if (currentDepartment === fullName) {
                            currentDepartment = '';
                        } else {
                            currentDepartment = fullName;
                        }

                        // Update dropdown to match
                        document.getElementById('department-filter').value = currentDepartment;
                        isFilteringFromChart = false;

                        // Reload data
                        loadData();
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: (context) => {
                                const index = context[0].dataIndex;
                                return window.deptChart.data.datasets[0].fullNames[index];
                            },
                            label: (context) => {
                                const index = context.dataIndex;
                                const dataset = window.deptChart.data.datasets[0];
                                return [
                                    `Employees: ${dataset.employeeCounts[index].toLocaleString()}`,
                                    `Avg Salary: ${formatCurrencyFull(dataset.avgSalaries[index])}`,
                                    `Avg Overtime: ${formatCurrencyFull(dataset.avgOvertimes[index])}`
                                ];
                            }
                        }
                    },
                    datalabels: {
                        anchor: 'end',
                        align: 'end',
                        formatter: (value) => formatCurrency(value),
                        color: '#1a202c',
                        font: {
                            weight: 'bold',
                            size: 11
                        }
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading department chart:', error);
    }
}

// Earnings composition bar chart
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
            type: 'bar',
            data: {
                labels: ['Regular', 'Overtime', 'Detail', 'Retro', 'Other', 'Injured', 'Quinn Ed'],
                datasets: [{
                    label: 'Percentage',
                    data: [
                        data.percentages.regular,
                        data.percentages.overtime,
                        data.percentages.detail,
                        data.percentages.retro,
                        data.percentages.other,
                        data.percentages.injured,
                        data.percentages.quinn_education
                    ],
                    totals: [
                        data.totals.regular,
                        data.totals.overtime,
                        data.totals.detail,
                        data.totals.retro,
                        data.totals.other,
                        data.totals.injured,
                        data.totals.quinn_education
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
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const index = context.dataIndex;
                                const total = window.earningsChart.data.datasets[0].totals[index];
                                return `Total: ${formatCurrency(total)}`;
                            }
                        }
                    },
                    datalabels: {
                        anchor: 'end',
                        align: 'end',
                        formatter: (value) => value.toFixed(1) + '%',
                        color: '#1a202c',
                        font: {
                            weight: 'bold',
                            size: 11
                        }
                    }
                },
                scales: {
                    y: {
                        display: false
                    },
                    x: {
                        ticks: {
                            font: {
                                size: 11
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
