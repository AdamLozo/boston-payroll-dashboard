# DataTable Specification

## Library Choice: DataTables.js

**Why DataTables** (over AG Grid):
- Simpler setup, no React required
- Sufficient for ~100K records with server-side processing
- Better documentation for vanilla JS
- Free, MIT license
- Lighter weight

**When to use AG Grid instead**:
- Need inline editing
- Complex cell renderers
- Tree data / grouping
- >500K records

## CDN Includes

```html
<!-- CSS -->
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
<link rel="stylesheet" href="https://cdn.datatables.net/responsive/2.5.0/css/responsive.dataTables.min.css">

<!-- JS -->
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/responsive/2.5.0/js/dataTables.responsive.min.js"></script>
```

## Table Configuration

```javascript
const table = $('#earnings-table').DataTable({
    // Server-side processing
    processing: true,
    serverSide: true,
    ajax: {
        url: '/api/employees',
        type: 'GET',
        data: function(d) {
            // Transform DataTables params to our API format
            return {
                limit: d.length,
                offset: d.start,
                sort_by: d.columns[d.order[0].column].data,
                sort_order: d.order[0].dir,
                search: d.search.value,
                year: $('#year-filter').val(),
                department: $('#dept-filter').val()
            };
        },
        dataSrc: function(json) {
            // Transform API response to DataTables format
            json.recordsTotal = json.total;
            json.recordsFiltered = json.filtered;
            return json.data;
        }
    },
    
    // Columns
    columns: [
        { 
            data: 'name',
            title: 'Name',
            className: 'name-col'
        },
        { 
            data: 'department_name',
            title: 'Department',
            className: 'dept-col'
        },
        { 
            data: 'title',
            title: 'Title',
            className: 'title-col'
        },
        { 
            data: 'regular',
            title: 'Regular',
            render: formatCurrency,
            className: 'currency-col dt-right'
        },
        { 
            data: 'overtime',
            title: 'Overtime',
            render: formatCurrency,
            className: 'currency-col dt-right'
        },
        { 
            data: 'detail',
            title: 'Detail',
            render: formatCurrency,
            className: 'currency-col dt-right'
        },
        { 
            data: 'total_gross',
            title: 'Total',
            render: formatCurrency,
            className: 'total-col dt-right'
        }
    ],
    
    // Options
    pageLength: 100,
    lengthMenu: [[50, 100, 250, 500], [50, 100, 250, 500]],
    order: [[6, 'desc']],  // Default sort by Total descending
    
    // Appearance
    responsive: true,
    scrollX: true,
    
    // Language
    language: {
        processing: '<div class="spinner">Loading...</div>',
        emptyTable: 'No matching records found',
        info: 'Showing _START_ to _END_ of _TOTAL_ employees',
        infoFiltered: '(filtered from _MAX_ total)'
    },
    
    // Performance
    deferRender: true,
    stateSave: true,  // Remember user's sort/filter
    
    // Callbacks
    drawCallback: function(settings) {
        // Update stats after table draw
        updateStats();
    }
});
```

## Currency Formatter

```javascript
function formatCurrency(value, type, row) {
    if (value === null || value === undefined) return '$0';
    
    // For display
    if (type === 'display') {
        return '$' + parseFloat(value).toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    }
    
    // For sorting/filtering
    return parseFloat(value);
}
```

## Filter Integration

```javascript
// Year filter
$('#year-filter').on('change', function() {
    table.ajax.reload();
    updateDepartmentDropdown($(this).val());
});

// Department filter
$('#dept-filter').on('change', function() {
    table.ajax.reload();
});

// Search (debounced)
let searchTimeout;
$('#search-input').on('keyup', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        table.search($(this).val()).draw();
    }, 300);
});
```

## Responsive Column Priority

```javascript
columns: [
    { data: 'name', responsivePriority: 1 },           // Always show
    { data: 'department_name', responsivePriority: 3 },
    { data: 'title', responsivePriority: 4 },          // Hide first on mobile
    { data: 'regular', responsivePriority: 5 },        // Hide second
    { data: 'overtime', responsivePriority: 5 },
    { data: 'detail', responsivePriority: 5 },
    { data: 'total_gross', responsivePriority: 2 }     // Always show
]
```

## Row Detail Expansion (Optional)

```javascript
// Click row to expand details
$('#earnings-table tbody').on('click', 'tr', function() {
    const data = table.row(this).data();
    
    if (table.row(this).child.isShown()) {
        table.row(this).child.hide();
        $(this).removeClass('shown');
    } else {
        table.row(this).child(formatRowDetail(data)).show();
        $(this).addClass('shown');
    }
});

function formatRowDetail(data) {
    return `
        <div class="row-detail">
            <div class="detail-grid">
                <div><strong>Regular:</strong> ${formatCurrency(data.regular, 'display')}</div>
                <div><strong>Retro:</strong> ${formatCurrency(data.retro, 'display')}</div>
                <div><strong>Other:</strong> ${formatCurrency(data.other, 'display')}</div>
                <div><strong>Overtime:</strong> ${formatCurrency(data.overtime, 'display')}</div>
                <div><strong>Injured:</strong> ${formatCurrency(data.injured, 'display')}</div>
                <div><strong>Detail:</strong> ${formatCurrency(data.detail, 'display')}</div>
                <div><strong>Quinn Ed:</strong> ${formatCurrency(data.quinn_education, 'display')}</div>
                <div><strong>ZIP:</strong> ${data.postal || 'N/A'}</div>
            </div>
        </div>
    `;
}
```

## Export Buttons (Optional Future Enhancement)

```html
<link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css">
<script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
```

```javascript
// Add to DataTable options
dom: 'Bfrtip',
buttons: ['csv', 'excel']
```
