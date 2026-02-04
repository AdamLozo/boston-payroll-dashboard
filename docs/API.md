# Boston Payroll API Documentation

Base URL (development): `http://localhost:8000`
Production: `https://bostonpayroll.adamlozo.com` *(coming soon)*

## Authentication

No authentication required (public data).

## Endpoints

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "total_records": 118931,
  "years_available": [2024, 2023, 2022, 2021, 2020]
}
```

---

### GET /api/employees

Get employee list with filters.

**Query Parameters:**
- `year` (int, default: 2024): Filter by year (2020-2024)
- `department` (string, optional): Exact department name
- `search` (string, optional): Search name or title (case-insensitive)
- `sort_by` (string, default: "total_gross"): Column to sort by
- `sort_order` (string, default: "desc"): "asc" or "desc"
- `limit` (int, default: 50, max: 5000): Records per page
- `offset` (int, default: 0): Pagination offset

**Example:**
```bash
curl "http://localhost:8000/api/employees?year=2024&search=police&limit=10"
```

**Response:**
```json
{
  "data": [
    {
      "id": 169376,
      "year": 2024,
      "name": "Demesmin,Stanley",
      "department": "Boston Police Department",
      "title": "Police Lieutenant (Det)",
      "regular": "161306.48",
      "retro": "105724.70",
      "other": "6906.86",
      "overtime": "223773.96",
      "injured": "12.52",
      "detail": "45597.23",
      "quinn_education": "32261.36",
      "total_gross": "575583.11",
      "zip_code": "02052"
    }
  ],
  "total": 25525,
  "limit": 10,
  "offset": 0,
  "year": 2024
}
```

---

### GET /api/departments

Get department aggregations.

**Query Parameters:**
- `year` (int, default: 2024): Filter by year

**Example:**
```bash
curl "http://localhost:8000/api/departments?year=2024"
```

**Response:**
```json
{
  "departments": [
    {
      "name": "Boston Police Department",
      "employee_count": 3490,
      "total_earnings": "577778101.97",
      "avg_earnings": "165552.46",
      "total_overtime": "103205022.04",
      "total_detail": "49972385.71"
    }
  ],
  "year": 2024
}
```

---

### GET /api/stats

Get summary statistics.

**Query Parameters:**
- `year` (int, default: 2024): Filter by year
- `department` (string, optional): Filter by department

**Example:**
```bash
curl "http://localhost:8000/api/stats?year=2024"
```

**Response:**
```json
{
  "year": 2024,
  "total_employees": 25525,
  "total_payroll": "2418844224.96",
  "avg_salary": "94763.73",
  "median_salary": "84026.13",
  "total_overtime": "176611676.68",
  "total_detail": "61936172.73",
  "top_department": "Boston Police Department",
  "top_department_total": "577778101.97"
}
```

---

### GET /api/earnings-breakdown

Get earnings composition.

**Query Parameters:**
- `year` (int, default: 2024): Filter by year
- `department` (string, optional): Filter by department

**Example:**
```bash
curl "http://localhost:8000/api/earnings-breakdown?year=2024"
```

**Response:**
```json
{
  "year": 2024,
  "breakdown": {
    "regular": "1911118183.08",
    "overtime": "176611676.68",
    "detail": "61936172.73",
    "retro": "113889720.07",
    "other": "76913562.89",
    "injured": "46425533.77",
    "quinn_education": "31949770.38"
  },
  "percentages": {
    "regular": 79.0,
    "overtime": 7.3,
    "detail": 2.6,
    "retro": 4.7,
    "other": 3.2,
    "injured": 1.9,
    "quinn_education": 1.3
  }
}
```

---

### GET /api/years

Get available years.

**Example:**
```bash
curl "http://localhost:8000/api/years"
```

**Response:**
```json
{
  "years": [2024, 2023, 2022, 2021, 2020],
  "default": 2024
}
```

---

### GET /api/export

Export filtered data as CSV.

**Query Parameters:** Same as `/api/employees` (without pagination)

**Example:**
```bash
curl "http://localhost:8000/api/export?year=2024&department=Boston+Police+Department" -o payroll.csv
```

**Response:** CSV file download

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Database error

**Error response format:**
```json
{
  "detail": "Error message"
}
```

---

## Performance

Target response times:
- `/api/health`: < 50ms
- `/api/employees`: < 200ms (up to 5000 records)
- `/api/departments`: < 100ms
- `/api/stats`: < 100ms
- `/api/earnings-breakdown`: < 100ms

---

## Example Queries

### Search for employees named "Smith"
```bash
curl "http://localhost:8000/api/employees?search=smith&year=2024&limit=10"
```

### Get police department employees
```bash
curl "http://localhost:8000/api/employees?department=Boston+Police+Department&year=2024"
```

### Get stats for fire department
```bash
curl "http://localhost:8000/api/stats?department=Boston+Fire+Department&year=2024"
```

### Compare departments across years
```bash
for year in 2020 2021 2022 2023 2024; do
  echo "Year $year:"
  curl -s "http://localhost:8000/api/stats?year=$year" | grep total_payroll
done
```

---

## CORS

CORS is enabled for all origins in development. Production will restrict to specific domains.

---

## Rate Limiting

No rate limiting in place currently. May be added in production if needed.
