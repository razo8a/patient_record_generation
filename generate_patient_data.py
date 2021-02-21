import sqlite3
import json
import os
import argparse


def split_rows(f):
    return f.split('|') 


def clean_newline(row):
    return row.replace('\n','') 


def create_table(table, headers):
    try:
        with sqlite3.connect('patient.db') as conn:
            conn.isolation_level = None
            cols = ",".join(headers) 
            conn.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(table, cols))
    except Exception as e:
        print('Error: ', type(e).__name__)
    else:
        print('Table {} created successfully'.format(table))


def insert_rows(table, rows):
    try:
        with sqlite3.connect('patient.db') as conn:
            conn.isolation_level = None
            row_count = conn.executemany("INSERT INTO " + table + " VALUES (" + "?,"*(len(rows[0])-1) + "?)", rows).rowcount
    except Exception as e:
        print('Error: ', type(e).__name__)
    else:
        print('Inserted successfully {} rows into table {}'.format(row_count, table))    


def run_query(q):
    try:
        with sqlite3.connect('patient.db') as conn:
            return conn.execute(q).fetchall()
    except Exception as e:
        print('Error: ', type(e).__name__)


def run_command(c):
    try:
        with sqlite3.connect('patient.db') as conn:
            conn.isolation_level = None
            conn.execute(c)
    except Exception as e:
        print('Error: ', type(e).__name__)    


def parse_files(tables):
    for table, file_name in tables.items():
        with open(file_name, mode='r') as file:
            header_row = file.readline()
            header_row_clean = clean_newline(header_row)
            headers = split_rows(header_row_clean)
            # adding PRIMARY KEY to patient_id in demo table 
            if table == 'demo':
                headers[0] = headers[0] + ' PRIMARY KEY'
            # addind FOREIGN KEY to patient_id in events table
            if table == 'events':
                headers.append('FOREIGN KEY (patient_id) REFERENCES demo (patient_id)')
            data = file.readlines()
            data_clean = [clean_newline(row) for row in data]
            data_rows = [(*split_rows(row),) for row in data_clean]
            create_table(table, headers)
            insert_rows(table, data_rows)


def generate_json(patient_id, patient_json):
    filename = patient_id + '.json'
    directory = './patient_json_files/'
    file_path = os.path.join(directory, filename)
    if not os.path.isdir(directory):
        os.mkdir(directory)
    with open(file_path, 'w') as f:
        json.dump(patient_json, f, indent=4)


# adding primary key to table demo
# run_command("ALTER TABLE demo ADD PRIMARY KEY (patient_id);")

def main():

    # parse all command line arguments
    parser = argparse.ArgumentParser(description='Patient data json files and analysis')
    parser.add_argument('-load', help='Confirm if data is being loaded', action='store_true')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--run_json', action='store_true')
    group.add_argument('--run_analysis', action='store_true')

    opts = parser.parse_args()

    # runs when script is executed with -load flag
    if opts.load:

        # creates tables from patient demographic and events files
        tables = {'demo':'demo.psv','events':'events.psv'}
        parse_files(tables)

        # creates a patient_events table for analysis
        patient_events_headers = ['patient_id', 'birth_date', 'gender', 'date', 'icd_version', 'icd_code']
        create_table('patient_events', patient_events_headers)

        run_command("""
            INSERT INTO patient_events SELECT 
            A.patient_id,
            A.birth_date,
            A.gender,
            B.date,
            B.icd_version,
            B.icd_code
            FROM demo A
            INNER JOIN events B
            ON A.patient_id = B.patient_id
            WHERE B.icd_code != ''
            AND B.icd_version != ''
            AND B.date != ''
            AND A.birth_date != ''
            AND A.gender != '';
        """)
        print('-*'*25)

    # runs to generate json files per patient with event information
    if opts.run_json:

        results = run_query("SELECT DISTINCT patient_id, birth_date, gender FROM patient_events;")

        for row in results:
            patient_id = row[0]
            patient_json = {
                'birth_date':row[1],
                'gender':row[2],
            }
            
            events_list = run_query("""
                SELECT date,
                CASE 
                    WHEN icd_version = '9' THEN 'http://hl7.org/fhir/sid/icd-9-cm'
                    WHEN icd_version = '10' THEN 'http://hl7.org/fhir/sid/icd-10'
                END AS icd_version, 
                icd_code 
                FROM patient_events 
                WHERE patient_id = '{}';""".format(patient_id))

            patient_json['event'] = []
            for event in events_list:
                patient_json['event'].append({'date':event[0], 'system':event[1], 'code':event[2]})

            generate_json(patient_id, patient_json)
    
    # runs to generate an analysis from patient data 
    if opts.run_analysis:

        # obtain the total amount of unique patients 
        valid_patients = run_query("SELECT COUNT(DISTINCT patient_id) total_patients FROM patient_events;")
        if valid_patients is not None:
            print('Total number of valid patients: ', valid_patients[0][0])
        
        # get the maximum/minimum/median length among patient timelines (number of days between the patient's first event and last) 
        patient_timeline = run_query("""
            WITH CTE1 AS (
                SELECT DISTINCT A.patient_id,
                B.max_date,
                C.min_date,
                JULIANDAY(B.max_date) - JULIANDAY(C.min_date) event_length
                FROM patient_events A
                INNER JOIN (SELECT patient_id, max(date(date)) max_date FROM patient_events GROUP BY patient_id) B
                ON A.patient_id = B.patient_id
                INNER JOIN (SELECT patient_id, min(date(date)) min_date FROM patient_events GROUP BY patient_id) C
                ON A.patient_id = C.patient_id
            )

            SELECT 
            CAST(MAX(event_length) AS INT) max_event_length,
            CAST(MIN(event_length) AS INT) min_event_length,
            CAST((SELECT AVG(event_length) FROM(
                SELECT event_length
                FROM CTE1
                ORDER BY event_length
                LIMIT 2 - (SELECT COUNT(*) FROM CTE1) % 2
                OFFSET (SELECT (COUNT(*) - 1) / 2 FROM CTE1)
            )) AS INT) median_length
            FROM CTE1;
        """)
        if patient_timeline is not None:
            print('The maximum event length: ', patient_timeline[0][0])
            print('The minimum event length: ', patient_timeline[0][1])
            print('The median event length: ', patient_timeline[0][2])

        # Obtain count of total males and females
        male_female_count = run_query("""
            SELECT 
            gender, 
            COUNT(*) total 
            FROM (SELECT DISTINCT patient_id, gender FROM patient_events) 
            GROUP BY gender
            ORDER BY 1;""")
        
        if male_female_count is not None:
            print('Total number of female patients: ', male_female_count[0])
            print('Total number of male patients: ', male_female_count[1])

        # Get the maximum/minimum/median age among all patients (calculated between birthdate and last registered event)
        patient_age = run_query("""
            WITH CTE1 AS (
                SELECT DISTINCT A.patient_id,
                B.max_event_date,
                A.birth_date,
                JULIANDAY(B.max_event_date) - JULIANDAY(A.birth_date) age
                FROM patient_events A
                INNER JOIN (SELECT patient_id, max(date(date)) max_event_date FROM patient_events GROUP BY patient_id) B
                ON A.patient_id = B.patient_id
            )

            SELECT 
            CAST(max(age) / 365 AS INT) max_age,
            CAST(min(age) / 365 AS INT) min_age,
            CAST((SELECT AVG(age) FROM(
                SELECT age
                FROM CTE1
                ORDER BY age
                LIMIT 2 - (SELECT COUNT(*) FROM CTE1) % 2
                OFFSET (SELECT (COUNT(*) - 1) / 2 FROM CTE1)
            )) / 365 AS INT) median_age
            FROM CTE1;
        """)
        if patient_age is not None:
            print('The maximum patient age: ', patient_age[0][0])
            print('The minimum patient age: ', patient_age[0][1])
            print('The median patient age: ', patient_age[0][2])


if __name__ == '__main__':
    main()
