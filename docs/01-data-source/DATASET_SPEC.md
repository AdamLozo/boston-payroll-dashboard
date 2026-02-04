# Dataset Specification

## Source
**Dataset**: Employee Earnings Report  
**Provider**: City of Boston - Office of Human Resources  
**URL**: https://data.boston.gov/dataset/employee-earnings-report  
**License**: Open Data Commons Public Domain Dedication and License (PDDL)  
**Update Frequency**: Annual (published each February for prior calendar year)

## Column Definitions

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `NAME` | string | Employee name | Format: "Last,First" or "Last,First M" |
| `DEPARTMENT_NAME` | string | City department | ~50 unique departments |
| `TITLE` | string | Job title | ~1,500+ unique titles |
| `REGULAR` | decimal | Regular pay | Base salary earnings |
| `RETRO` | decimal | Retroactive pay | Back pay from contract negotiations |
| `OTHER` | decimal | Other earnings | Stipends, bonuses, misc |
| `OVERTIME` | decimal | Overtime pay | Time-and-a-half earnings |
| `INJURED` | decimal | Injured pay | Workers comp while out |
| `DETAIL` | decimal | Detail pay | Police/fire paid details |
| `QUINN_EDUCATION` | decimal | Quinn Bill incentive | Education bonus (police) |
| `TOTAL GROSS` | decimal | Total earnings | Sum of all columns |
| `POSTAL` | string | ZIP code | Employee's postal code |

## Data Quirks

1. **Currency formatting**: Values have commas (e.g., "161,306.48") - must parse
2. **Empty values**: Some columns are empty (not null, just empty string)
3. **Name variations**: Some names have middle initials, some don't
4. **Department changes**: Department names may change slightly year-to-year
5. **2023 file**: XLSX format (others are CSV) - need to handle
6. **Quinn Bill**: Only applies to police, blank for other departments

## Data Volume (Estimated)

| Year | Approx Records |
|------|---------------|
| 2024 | ~23,000 |
| 2023 | ~22,500 |
| 2022 | ~22,000 |
| 2021 | ~21,500 |
| 2020 | ~21,000 |
| **Total** | **~110,000** |

## Top Departments (by employee count)

1. Boston Public Schools
2. Boston Police Department
3. Boston Fire Department
4. Public Works Department
5. Boston Centers for Youth & Families

## Sample Query Use Cases

1. "Show me all Police Lieutenants making over $300K"
2. "Which department has the highest average overtime?"
3. "Top 100 earners in 2024"
4. "Compare BPD overtime 2020 vs 2024"
