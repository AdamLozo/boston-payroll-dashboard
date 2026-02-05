import sys
sys.path.insert(0, 'C:\\Users\\adam\\OneDrive\\Claude\\Projects\\boston-payroll-dashboard')

from backend.queries import get_departments
import json

# Test departments query with rounding
depts = get_departments(year=2024)
print("avg_earnings:", depts[0]['avg_earnings'])
print("avg_overtime:", depts[0]['avg_overtime'])
print("Type:", type(depts[0]['avg_earnings']))
