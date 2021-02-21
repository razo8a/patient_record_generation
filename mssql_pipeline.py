import airflow
from airflow import models
from airflow.contrib.operators import gcs_to_bq, mssql_to_gcs

args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(2)
}

with models.DAG(dag_id='mssql_pipeline', default_args=args, schedule_interval=None) as dag:
    export_mssql = mssql_to_gcs.MsSqlToGoogleCloudStorageOperator(
    task_id='export_mssql',
    sql='SELECT * FROM AdventureWorksDW2016.dbo.DimCustomer;',
    bucket='mae_tables',
    filename='gs://mae_tables/dept.csv',
    schema_filename='dept_schema.json',
    mssql_conn_id='mssql_default',
    google_cloud_storage_conn_id='google_cloud_default'
)