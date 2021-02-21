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

