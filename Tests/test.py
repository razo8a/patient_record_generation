import pandas as pd

# Data consistency and integrity check

demo = pd.read_csv('demo.psv', delimiter='|')
# Null and data type analysis
print(demo.info())
# Check if all elements in birth_date column have same format
print(demo[demo['birth_date'].str.contains(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',na=False) == False])
# Check unique patient_id count
print(demo['patient_id'].unique().size)

events = pd.read_csv('events.psv', delimiter='|')
# Null and data type analysis
print(events.info())
# Check if all elements in date column have same format
print(events[events['date'].str.contains(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',na=False) == False])
# Check all empty icd_code entries total unique patient_id count 
print(events.loc[events['icd_code'].isnull() == False,'patient_id'].unique().size)
# Check all non-empty icd_code entries total unique patient_id count 
print(events.loc[events['icd_code'].isnull() == False,'patient_id'].unique().size)
