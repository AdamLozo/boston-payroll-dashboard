// API Configuration
const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:8001'
    : 'https://boston-payroll-api.onrender.com';

// Global state
let currentYear = 2024;
let currentDepartment = '';
let currentEarningsType = '';
let employeesData = [];
let grid = null;
let isFilteringFromChart = false; // Prevent circular filtering

// Earnings type mapping for display and API
const earningsTypeMap = {
    'Regular': 'regular',
    'Overtime': 'overtime',
    'Detail': 'detail',
    'Retro': 'retro',
    'Other': 'other',
    'Injured': 'injured',
    'Quinn Ed': 'quinn_education'
};

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
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

// Update page titles based on filter
function updateTitles() {
    const deptTitle = document.querySelector('.chart-card:first-child h3');
    const earningsTitle = document.querySelector('.chart-card:last-child h3');

    // Build earnings title with active filters
    let earningsTitleText = '';
    if (currentDepartment && currentEarningsType) {
        earningsTitleText = `${currentDepartment} - Earnings Composition (${currentYear})`;
    } else if (currentDepartment) {
        earningsTitleText = `${currentDepartment} - Earnings Composition (${currentYear})`;
    } else if (currentEarningsType) {
        const displayName = Object.keys(earningsTypeMap).find(key => earningsTypeMap[key] === currentEarningsType) || currentEarningsType;
        earningsTitleText = `Earnings Composition - ${displayName} Selected (${currentYear})`;
    } else {
        earningsTitleText = `Earnings Composition (${currentYear})`;
    }

    deptTitle.textContent = `Top Departments by Total Earnings (${currentYear})`;
    earningsTitle.textContent = earningsTitleText;
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
            if (grid && grid.api) {
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
    updateTitles();
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
        if (currentEarningsType) {
            url += `&earnings_type=${encodeURIComponent(currentEarningsType)}`;
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
            field: 'retro',
            headerName: 'Retro',
            width: 110,
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
            field: 'injured',
            headerName: 'Injured',
            width: 110,
            type: 'numericColumn',
            valueFormatter: params => formatCurrencyFull(params.value)
        },
        {
            field: 'quinn_education',
            headerName: 'Quinn/Ed',
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
        domLayout: 'normal',
        onGridReady: (params) => {
            grid = params;
        }
    };

    const gridDiv = document.getElementById('employees-grid');
    agGrid.createGrid(gridDiv, gridOptions);
}

// Format variance display
function formatVariance(current, prior, isPositiveGood = false) {
    if (!prior || prior === 0) {
        return '';
    }

    const diff = current - prior;
    const pctChange = ((diff / prior) * 100).toFixed(1);
    const arrow = diff > 0 ? '▲' : '▼';
    const className = diff > 0 ? 'positive' : 'negative';

    let diffStr;
    if (Math.abs(current) >= 1000000) {
        diffStr = formatCurrency(Math.abs(diff));
    } else if (Math.abs(current) >= 1000) {
        diffStr = Math.abs(diff).toLocaleString('en-US', {maximumFractionDigits: 0});
    } else {
        diffStr = Math.abs(diff).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }

    return { text: `${arrow} ${diffStr} (${Math.abs(pctChange)}%)`, className };
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
            formatCurrencyFull(stats.total_payroll);
        document.getElementById('stat-average').textContent =
            formatCurrencyFull(stats.avg_salary);
        document.getElementById('stat-overtime').textContent =
            formatCurrency(stats.total_overtime);

        // Update variance indicators
        const employeesVar = formatVariance(stats.total_employees, stats.prior_year_employees);
        const payrollVar = formatVariance(stats.total_payroll, stats.prior_year_payroll);
        const avgVar = formatVariance(stats.avg_salary, stats.prior_year_avg_salary);
        const overtimeVar = formatVariance(stats.total_overtime, stats.prior_year_overtime);

        updateVarianceElement('stat-employees-variance', employeesVar);
        updateVarianceElement('stat-payroll-variance', payrollVar);
        updateVarianceElement('stat-average-variance', avgVar);
        updateVarianceElement('stat-overtime-variance', overtimeVar);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateVarianceElement(elementId, variance) {
    const element = document.getElementById(elementId);
    if (variance) {
        element.textContent = variance.text;
        element.className = 'stat-variance ' + variance.className;
    } else {
        element.textContent = '';
        element.className = 'stat-variance';
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
                    avgSalaries: top10.map(d => Math.round(d.avg_earnings)),
                    avgOvertimes: top10.map(d => Math.round(d.avg_overtime))
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
                                const avgSalary = dataset.avgSalaries[index] || 0;
                                const avgOvertime = dataset.avgOvertimes[index] || 0;
                                return [
                                    `Employees: ${dataset.employeeCounts[index].toLocaleString()}`,
                                    `Avg Salary: ${formatCurrencyFull(avgSalary)}`,
                                    `Avg Overtime: ${formatCurrencyFull(avgOvertime)}`
                                ];
                            }
                        }
                    },
                    datalabels: {
                        display: true,
                        anchor: 'end',
                        align: (context) => {
                            const value = context.dataset.data[context.dataIndex];
                            const max = Math.max(...context.dataset.data);
                            // If bar is long enough, put label inside
                            return value / max > 0.3 ? 'start' : 'end';
                        },
                        offset: (context) => {
                            const value = context.dataset.data[context.dataIndex];
                            const max = Math.max(...context.dataset.data);
                            // Offset for labels inside bars to prevent clipping
                            return value / max > 0.3 ? 10 : 4;
                        },
                        formatter: (value) => formatCurrency(value),
                        color: (context) => {
                            const value = context.dataset.data[context.dataIndex];
                            const max = Math.max(...context.dataset.data);
                            // White text for labels inside bars
                            return value / max > 0.3 ? '#ffffff' : '#1a202c';
                        },
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

        const earningsLabels = ['Regular', 'Overtime', 'Detail', 'Retro', 'Other', 'Injured', 'Quinn Ed'];
        const earningsKeys = ['regular', 'overtime', 'detail', 'retro', 'other', 'injured', 'quinn_education'];
        const baseColors = ['#4299e1', '#ed8936', '#9f7aea', '#48bb78', '#a0aec0', '#f56565', '#38b2ac'];
        const selectedColors = ['#1a365d', '#c05621', '#6b46c1', '#276749', '#4a5568', '#c53030', '#234e52'];

        window.earningsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: earningsLabels,
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
                        data.breakdown.regular,
                        data.breakdown.overtime,
                        data.breakdown.detail,
                        data.breakdown.retro,
                        data.breakdown.other,
                        data.breakdown.injured,
                        data.breakdown.quinn_education
                    ],
                    earningsKeys: earningsKeys,
                    backgroundColor: earningsKeys.map((key, i) =>
                        key === currentEarningsType ? selectedColors[i] : baseColors[i]
                    )
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const earningsKey = earningsKeys[index];

                        // Toggle filter
                        if (currentEarningsType === earningsKey) {
                            currentEarningsType = '';
                        } else {
                            currentEarningsType = earningsKey;
                        }

                        // Reload data (charts will update colors, employees will filter)
                        loadData();
                    }
                },
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
                            },
                            afterLabel: () => {
                                return 'Click to filter employees';
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
        if (currentEarningsType) {
            url += `&earnings_type=${encodeURIComponent(currentEarningsType)}`;
        }

        window.location.href = url;
    } catch (error) {
        console.error('Error exporting CSV:', error);
        alert('Error exporting data');
    }
}
