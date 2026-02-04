# CKAN Resource IDs

## Dataset ID
`418983dc-7cae-42bb-88e4-d56f5adcf869`

## Resource IDs by Year

| Year | Resource ID | Format | Direct Download URL |
|------|-------------|--------|---------------------|
| 2024 | `579a4be3-9ca7-4183-bc95-7d67ee715b6d` | CSV | https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/579a4be3-9ca7-4183-bc95-7d67ee715b6d/download/employee_earnings_report_2024.csv |
| 2023 | `6b3c5333-1dcb-4b3d-9cd7-6a03fb526da7` | XLSX | https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/6b3c5333-1dcb-4b3d-9cd7-6a03fb526da7/download/employee-earnings-report-2023.xlsx |
| 2022 | `63ac638b-36c4-487d-9453-1d83eb5090d2` | CSV | https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/63ac638b-36c4-487d-9453-1d83eb5090d2/download/finalconsolidatedcy22earnings_feb2023.xlsx-sheet1.csv |
| 2021 | `ec5aaf93-1509-4641-9310-28e62e028457` | CSV | https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/ec5aaf93-1509-4641-9310-28e62e028457/download/employee-earnings-report-2021.csv |
| 2020 | `e2e2c23a-6fc7-4456-8751-5321d8aa869b` | CSV | https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/e2e2c23a-6fc7-4456-8751-5321d8aa869b/download/city-of-boston-calendar-year-2020-earnings.csv |

## Download Commands

```bash
# Create data directory
mkdir -p data/raw

# Download all files
curl -o data/raw/earnings_2024.csv "https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/579a4be3-9ca7-4183-bc95-7d67ee715b6d/download/employee_earnings_report_2024.csv"

curl -o data/raw/earnings_2023.xlsx "https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/6b3c5333-1dcb-4b3d-9cd7-6a03fb526da7/download/employee-earnings-report-2023.xlsx"

curl -o data/raw/earnings_2022.csv "https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/63ac638b-36c4-487d-9453-1d83eb5090d2/download/finalconsolidatedcy22earnings_feb2023.xlsx-sheet1.csv"

curl -o data/raw/earnings_2021.csv "https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/ec5aaf93-1509-4641-9310-28e62e028457/download/employee-earnings-report-2021.csv"

curl -o data/raw/earnings_2020.csv "https://data.boston.gov/dataset/418983dc-7cae-42bb-88e4-d56f5adcf869/resource/e2e2c23a-6fc7-4456-8751-5321d8aa869b/download/city-of-boston-calendar-year-2020-earnings.csv"
```

## CKAN API (Not Used)

Note: Unlike building permits which use streaming CKAN datastore API, this dataset uses direct CSV downloads. The datastore API is not reliably available for these resources.

## Data Refresh

- **Frequency**: Annual (manual)
- **Timing**: New data published each February
- **Process**: Download new CSV, run load script, verify counts
