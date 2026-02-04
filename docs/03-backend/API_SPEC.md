# API Specification

## Base URL
- Development: `http://localhost:8000`
- Production: `https://bostonpayroll.adamlozo.com`

## Endpoints

### GET /api/employees

Paginated, filterable, searchable employee list. Designed for DataTables server-side processing.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | int | 2024 | Filter by year |
| `department` | string | null | Filter by department (exact match) |
| `search` | string | null | Search name, title, department |
| `sort_by` | string | total_gross | Column to sort by |
| `sort_order` | string | desc | asc or desc |
| `limit` | int | 100 | Records per page (max 500) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Demesmin,Stanley",
      "department_name": "Boston Police Department",
      "title": "Police Lieutenant (Det)",
      "regular": 161306.48,
      "retro": 105724.70,
      "other": 6906.86,
      "overtime": 223773.96,
      "injured": 12.52,
      "detail": 45597.23,
      "quinn_education": 32261.36,
      "total_gross": 575583.11,
      "postal": "02052",
      "year": 2024
    }
  ],
  "total": 23456,
  "filtered": 23456,
  "limit": 100,
  "offset": 0
}
```

---

### GET /api/stats

Summary statistics for dashboard header.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | int | 2024 | Filter by year |
| `department` | string | null | Filter by department |

**Response:**
```json
{
  "total_employees": 23456,
  "total_payroll": 1845678901.23,
  "avg_salary": 78654.32,
  "total_overtime": 234567890.12,
  "total_detail": 123456789.01,
  "max_earner": {
    "name": "Demesmin,Stanley",
    "total_gross": 575583.11
  },
  "year": 2024
}
```

---

### GET /api/departments

Department aggregations for charts.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | int | 2024 | Filter by year |
| `sort_by` | string | total | total, overtime, detail, count |
| `limit` | int | 20 | Number of departments |

**Response:**
```json
{
  "data": [
    {
      "department_name": "Boston Police Department",
      "employee_count": 3456,
      "total_payroll": 456789012.34,
      "total_overtime": 123456789.01,
      "total_detail": 98765432.10,
      "avg_salary": 132145.67
    }
  ],
  "year": 2024
}
```

---

### GET /api/earnings-breakdown

Earnings composition for pie/stacked bar chart.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | int | 2024 | Filter by year |
| `department` | string | null | Filter by department |

**Response:**
```json
{
  "regular": 1234567890.12,
  "retro": 123456789.01,
  "other": 98765432.10,
  "overtime": 234567890.12,
  "injured": 12345678.90,
  "detail": 123456789.01,
  "quinn_education": 45678901.23,
  "total": 1845678901.23,
  "year": 2024
}
```

---

### GET /api/years

Available years for dropdown.

**Response:**
```json
{
  "years": [2024, 2023, 2022, 2021, 2020]
}
```

---

### GET /api/department-list

Unique departments for dropdown filter.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | int | null | Filter by year (null = all years) |

**Response:**
```json
{
  "departments": [
    "Boston Centers for Youth & Families",
    "Boston Fire Department",
    "Boston Police Department",
    "Boston Public Schools",
    ...
  ]
}
```

---

### GET /api/health

Health check for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "record_count": 110234,
  "last_updated": "2024-02-28T12:00:00Z"
}
```

## Error Responses

```json
{
  "error": "Invalid parameter",
  "detail": "year must be between 2020 and 2024"
}
```

Status codes: 400 (bad request), 500 (server error)
