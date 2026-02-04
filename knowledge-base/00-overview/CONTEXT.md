# Project Overview - Boston Payroll Dashboard

## Vision
A transparent, searchable public dashboard for Boston city employee compensation data. Users can explore who earns what, analyze overtime patterns, and understand how taxpayer money is spent on city salaries.

## Primary Use Cases

### 1. Explore Top Earners by Department
**User Story**: As a Boston resident, I want to see which employees earn the most in each department so I can understand compensation patterns.

**Features Required**:
- Searchable data table with all employees
- Sort by any earnings column (Regular, Overtime, Detail, Total)
- Filter by department
- Filter by year

### 2. Analyze Overtime and Detail Pay Patterns
**User Story**: As a journalist/researcher, I want to analyze overtime and detail pay across departments to identify trends or anomalies.

**Features Required**:
- Earnings breakdown visualization (Regular vs OT vs Detail)
- Department-level aggregations
- Year-over-year comparison capability

## Constraints

### Technical
- **Database**: Shared Render PostgreSQL (existing infrastructure)
- **No Maps**: Only ZIP code data available (no lat/long)
- **Annual Data**: Updated once per year (not real-time)
- **5 Years**: 2020-2024 data only

### Design
- **Data Table Focused**: Different from map-centric building permits dashboard
- **Fast Search**: Client-side filtering for instant results
- **Mobile Friendly**: Responsive design

### Operational
- **Manual Refresh**: No automated sync (annual manual update)
- **Shared DB**: Must prefix tables to avoid conflicts

## Data Source

**Analyze Boston**: Employee Earnings Report
- URL: https://data.boston.gov/dataset/employee-earnings-report
- Format: 14 separate CSV files (one per year, 2011-2024)
- We use: 2020-2024 only (5 files)
- Update Frequency: Annual
- License: Open Data Commons PDDL

### Resource IDs (CSV Downloads)
| Year | Resource ID |
|------|-------------|
| 2024 | `579a4be3-9ca7-4183-bc95-7d67ee715b6d` |
| 2023 | `6b3c5333-1dcb-4b3d-9cd7-6a03fb526da7` |
| 2022 | `63ac638b-36c4-487d-9453-1d83eb5090d2` |
| 2021 | `ec5aaf93-1509-4641-9310-28e62e028457` |
| 2020 | `e2e2c23a-6fc7-4456-8751-5321d8aa869b` |

### Data Fields
| Field | Type | Description |
|-------|------|-------------|
| NAME | text | Employee full name |
| DEPARTMENT_NAME | text | City department |
| TITLE | text | Job title |
| REGULAR | numeric | Base salary earnings |
| RETRO | numeric | Retroactive pay |
| OTHER | numeric | Other compensation |
| OVERTIME | numeric | Overtime pay |
| INJURED | numeric | Injured-on-duty pay |
| DETAIL | numeric | Detail pay (police/fire) |
| QUINN_EDUCATION | numeric | Quinn Bill education incentive |
| TOTAL GROSS | numeric | Total gross earnings |
| POSTAL | text | ZIP code |

## Success Metrics

1. **Performance**: Table loads in < 1 second
2. **Search**: Instant filtering (< 100ms)
3. **Data Accuracy**: 100% match with source CSVs
4. **Availability**: 99.9% uptime

## Out of Scope

- Historical data before 2020
- Automated annual updates
- Map visualizations
- Individual employee detail pages
- Benefits/pension data (not in dataset)
- Comparison with other cities

## Related Projects

- **Boston Building Permits**: Map-focused, real-time API, bostonpermits.adamlozo.com
- **Boston Restaurants**: Map-focused, bostonrestaurants.adamlozo.com

This project establishes a new pattern: **data table focused analytics dashboard**.
