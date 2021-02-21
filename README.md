## Info for Longitudinal Patient Data Interview Question

Files in the `data` folder are to be sent to the interviewee. They include a
copy of the `*_top.psv` tables as well as the interview question below. 

## Longitudinal Patient Data Interview Question

This problem is intended to evaluate thought process, common sense checks and
overall architecture. While the problem itself won't likely take very much 
time, and there are several valid ways to solve the problem, we're looking to 
see how you approach it and how well the code would adapt to changing needs 
over time. Please see the end of this README for restrictions on what tools
should be used.

Here are two tables, events.psv containing dates and medical events in an 
individual patient’s timeline, and demo.psv containing demographic information
about the patient. In this case medical events are represented as ICD codes, 
which is an industry standard coding system for representing diagnoses. Each 
entry in the events table therefore represents a patient receiving a single 
diagnosis on that date in either the ICD-9 or ICD-10 coding system.

The `events.psv` file has the following columns:
- `patient_id`: The ID for the patient
- `date`: the date of the event
- `icd_version`: the ICD code version (9 or 10)
- `icd_code`: the ICD code representing a medical event in the patient’s 
history

The `demo.psv` file has the following columns:
- `patient_id`: The ID for the patient
- `birth_date`: Patient’s birthday
- `gender`: “M” or “F”

Join these tables together to produce a series of JSONs, one per patient, 
representing that patient’s complete health record. The patient JSON you 
create should contain the demographic information for the patient and a list 
of events. Each event should have the code, the date when it happened (ISO 
format preferred) and a URL for the code system for the event. 

- The URL for ICD-9 codes is: http://hl7.org/fhir/sid/icd-9-cm
- The URL for ICD-10 codes is: http://hl7.org/fhir/sid/icd-10

Some patients may not have any events, in which case do not create a patient 
JSON. Some events may have an empty code, in which case, don’t create an entry
for that code in the “eventss” section. Some events may be assigned to a 
patient for which we have no demographic information, if so, don’t create a 
JSON for that patient. Only events that have a date, a code and a system are 
valid and should be included, and only patients that have both complete 
demographic information (both birthdate and gender) AND at least one event 
should be included.

The specific design/key names of the JSON isn’t set in stone, but an example 
is provided below:

```
{
    "birth_date": "1974-09-02",
    "gender": "F",
    "events": [
        {
            "date": "2016-03-01",
            "system": "http://hl7.org/fhir/sid/icd-10",
            "code": "Z01.00"
        },
        {
            "date": "2014-05-23",
            "system": "http://hl7.org/fhir/sid/icd-9-cm",
            "code": "367.0"
        }
    ]
}
```

A few statistics were computed on the valid patients:

- Total number of valid patients
- Maximum/Minimun/Median length among patient timelines in days 
(the number of days contained within an individual patient’s first event and a 
patient’s last event)
- Count of males and females
- Maximum/Minimum/Median age among patients as calculated between birthdate and 
last event in timeline

## Instructions to run the generate_patient_data.py

Please run the `generate_patient_data.py` in terminal as follows:

```
$ python3 generate_patient_data.py [-h] [-load] (--run_json | --run_analysis)
```

### Requiered arguments

- **--run_json**:  This option will generate all json files per patient and save them inside a folder
- **--run_analysis**: This option will generate all the stats regarding the generated event patient data

### Optional arguments

- **-load**: Use this flag in order to parse source data files and store them in a database
- **-h**, **--help**: Use this flag to show help message and exit

### Description

Algorithm will load `demo.psv` and `events.psv` files, parse them and load them into a local sqlite database. It will create two tables, one for each file. A primary key constraint was added to patient_id in demo table and foreign key added to patient_id in events table. The two tables are then joinned together to create a new table according to the following especifications:

- **INNER JOIN** in order to exclude patient_ids with no event data in the events table and no demographic data in the demo table. 
- **WHERE CLAUSE** in order to filter events with no icd_code 

JSON files are then generated per patient_id and saved into a `patient_json_files` directory created during execution.

### Usage

1. **First** run algorithm with *-load* flag in order to generate event patient data and store them in JSON files:

```
$ python3 generate_patient_data.py -load --run_json
```

2. **Second**, run algorithm again with *--run_analysis* option to generate event patient data stats:
```
$ python3 generate_patient_data.py --run_analysis
```

### Optional

In order to rerun algorithm to generate JSON files after loading data, you can run script as:
```
$ python3 generate_patient_data.py --run_json
```

In order to load data and show event patient data stats without the need to generate JSON files, you can run script as:
```
$ python3 generate_patient_data.py -load --run_analysis
```

