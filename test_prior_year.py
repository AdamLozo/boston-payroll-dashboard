import sys
sys.path.insert(0, 'C:\\Users\\adam\\OneDrive\\Claude\\Projects\\boston-payroll-dashboard')

from backend.queries import get_stats
import json

# Test for year 2023 (should have 2022 as prior year)
stats = get_stats(year=2023)
print(json.dumps(stats, indent=2, default=str))
