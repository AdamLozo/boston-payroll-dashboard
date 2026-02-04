# Sample Data

## Top Earners (2024)

```csv
NAME,DEPARTMENT_NAME,TITLE,REGULAR,RETRO,OTHER,OVERTIME,INJURED,DETAIL,QUINN_EDUCATION,TOTAL GROSS,POSTAL
"Demesmin,Stanley",Boston Police Department,Police Lieutenant (Det),"161,306.48","105,724.70","6,906.86","223,773.96",12.52,"45,597.23","32,261.36","575,583.11",02052
"Sordillo,Paul J",Facilities Management,Building Services Fleet Mgr,"108,815.78","20,055.71","413,783.39","24,772.61",,,,"567,427.49",02127
"Smith,Sean P",Boston Police Department,Police Lieutenant,"155,265.97","96,850.51","21,740.86","148,505.22",,"97,045.79","38,816.51","558,224.86",02186
"Connolly,Timothy",Boston Police Department,Police Captain/DDC,"178,073.23","99,063.23","27,649.74","193,677.07",126.81,"7,651.56","44,518.46","550,760.10",02186
"Danilecki,John H",Boston Police Department,Police Captain,"177,743.21","87,989.27","27,598.50","136,562.06",130.09,"70,060.84","44,435.86","544,519.83",02559
```

## Parsing Notes

### Currency Cleanup
```python
def parse_currency(value):
    """Convert '161,306.48' to 161306.48"""
    if not value or value.strip() == '':
        return 0.0
    return float(value.replace(',', ''))
```

### Name Parsing (Optional)
```python
def parse_name(name):
    """Split 'Last,First M' into components"""
    parts = name.split(',')
    last_name = parts[0].strip() if parts else ''
    first_name = parts[1].strip() if len(parts) > 1 else ''
    return last_name, first_name
```

## Test Cases

### High Overtime
- Stanley Demesmin: $223,773.96 overtime
- Rick E Johnson: $202,514.27 overtime

### High Detail Pay
- Ismael Lopes Almeida: $180,113.95 detail
- Timothy M. Kervin: $180,075.11 detail

### High Quinn Education
- Timothy Connolly: $44,518.46 Quinn
- John H Danilecki: $44,435.86 Quinn

### Non-Police High Earner
- Robert J Calobrisi (Fire): $495,495.96 (mostly "Other")
- Paul J Sordillo (Facilities): $567,427.49 (mostly "Other")

## Expected Query Results

### Top 10 by Department (2024)
```
Boston Police Department: ~$450M total
Boston Fire Department: ~$180M total
Boston Public Schools: ~$350M total
...
```

### Overtime Concentration
Expect ~70-80% of overtime in BPD and BFD
