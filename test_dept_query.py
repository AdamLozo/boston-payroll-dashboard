import sys
sys.path.insert(0, 'C:\\Users\\adam\\OneDrive\\Claude\\Projects\\boston-payroll-dashboard')

from backend.queries import get_departments
import json

# Test departments query
depts = get_departments(year=2024)
print(json.dumps(depts[:2], indent=2, default=str))
