# Chart.js Specifications

## Library: Chart.js 4.x

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

## Chart 1: Department Breakdown (Horizontal Bar)

**Purpose**: Show total earnings by department, top 10-15

```javascript
async function renderDepartmentChart(year) {
    const response = await fetch(`/api/departments?year=${year}&limit=15&sort_by=total`);
    const { data } = await response.json();
    
    const ctx = document.getElementById('dept-chart').getContext('2d');
    
    // Destroy existing chart if exists
    if (window.deptChart) window.deptChart.destroy();
    
    window.deptChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => truncateLabel(d.department_name, 25)),
            datasets: [{
                label: 'Total Payroll',
                data: data.map(d => d.total_payroll),
                backgroundColor: '#2c5282',
                borderColor: '#1a365d',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',  // Horizontal bars
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => '$' + (ctx.raw / 1000000).toFixed(1) + 'M'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        callback: (value) => '$' + (value / 1000000).toFixed(0) + 'M'
                    }
                },
                y: {
                    ticks: { font: { size: 11 } }
                }
            }
        }
    });
}

function truncateLabel(label, maxLength) {
    return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
}
```

## Chart 2: Earnings Composition (Stacked Bar or Doughnut)

**Purpose**: Show breakdown of earnings types

### Option A: Stacked Bar (Recommended)

```javascript
async function renderCompositionChart(year, department = null) {
    let url = `/api/earnings-breakdown?year=${year}`;
    if (department) url += `&department=${encodeURIComponent(department)}`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    const ctx = document.getElementById('composition-chart').getContext('2d');
    
    if (window.compositionChart) window.compositionChart.destroy();
    
    window.compositionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Earnings Breakdown'],
            datasets: [
                {
                    label: 'Regular',
                    data: [data.regular],
                    backgroundColor: '#2c5282'
                },
                {
                    label: 'Overtime',
                    data: [data.overtime],
                    backgroundColor: '#ed8936'
                },
                {
                    label: 'Detail',
                    data: [data.detail],
                    backgroundColor: '#38a169'
                },
                {
                    label: 'Other',
                    data: [data.other + data.retro + data.injured + data.quinn_education],
                    backgroundColor: '#718096'
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ctx.dataset.label + ': $' + (ctx.raw / 1000000).toFixed(1) + 'M'
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        callback: (value) => '$' + (value / 1000000).toFixed(0) + 'M'
                    }
                },
                y: { stacked: true }
            }
        }
    });
}
```

### Option B: Doughnut

```javascript
window.compositionChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Regular', 'Overtime', 'Detail', 'Other'],
        datasets: [{
            data: [
                data.regular,
                data.overtime,
                data.detail,
                data.other + data.retro + data.injured + data.quinn_education
            ],
            backgroundColor: ['#2c5282', '#ed8936', '#38a169', '#718096']
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'right' },
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        const pct = ((ctx.raw / data.total) * 100).toFixed(1);
                        return `${ctx.label}: $${(ctx.raw / 1000000).toFixed(1)}M (${pct}%)`;
                    }
                }
            }
        }
    }
});
```

## Chart Containers (HTML)

```html
<div class="charts-section" id="charts-toggle">
    <div class="charts-header">
        <h2>Visualizations</h2>
        <button id="toggle-charts" class="btn-link">Hide</button>
    </div>
    <div class="charts-grid">
        <div class="chart-card">
            <h3>Top Departments by Total Payroll</h3>
            <div class="chart-container" style="height: 400px;">
                <canvas id="dept-chart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <h3>Earnings Composition</h3>
            <div class="chart-container" style="height: 250px;">
                <canvas id="composition-chart"></canvas>
            </div>
        </div>
    </div>
</div>
```

## Chart Styling (CSS)

```css
.charts-section {
    margin-top: 2rem;
    padding: 1.5rem;
    background: var(--surface);
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

@media (max-width: 992px) {
    .charts-grid {
        grid-template-columns: 1fr;
    }
}

.chart-card {
    padding: 1rem;
}

.chart-card h3 {
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text-muted);
}
```

## Update on Filter Change

```javascript
// Refresh charts when year or department changes
$('#year-filter, #dept-filter').on('change', function() {
    const year = $('#year-filter').val();
    const dept = $('#dept-filter').val();
    
    renderDepartmentChart(year);
    renderCompositionChart(year, dept);
});

// Initial load
$(document).ready(function() {
    renderDepartmentChart(2024);
    renderCompositionChart(2024);
});
```
