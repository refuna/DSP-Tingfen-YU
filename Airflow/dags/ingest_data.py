import logging
from datetime import datetime
from datetime import timedelta

import pandas as pd
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago

# Import pendulumc

import pendulum

import os

# Constants:
airflow_home_folder = os.environ["AIRFLOW_HOME"]
input_file_path = airflow_home_folder + "/input_data/power_plants.csv"
output_folder_path = airflow_home_folder + f'/output_data/{datetime.now().strftime("%Y-%M-%d_%H-%M-%S")}.csv'

# print('OK')
@dag(
    dag_id='ingest_data',
    description='Ingest data from a file to another DAG',
    tags=['dsp', 'data_ingestion'],
    schedule=timedelta(minutes=2),
    # start_date=days_ago(n=0, hour=1)
    start_date = pendulum.today('UTC').add(days=-0,hours=-1)
)
def ingest_data():
    print('OK')
    print(input_file_path)
    @task
    def get_data_to_ingest_from_local_file() -> pd.DataFrame:
        nb_rows = 5
        print('Tentative de lecture du fichier')
        logging.info(input_file_path)
        print(input_file_path)
        input_data_df = pd.read_csv(input_file_path)
        print(f'Extract {nb_rows} from the file {input_file_path}')
        data_to_ingest_df = input_data_df.sample(n=nb_rows)
        return data_to_ingest_df

    @task
    def save_data(data_to_ingest_df: pd.DataFrame) -> None:
        print(f'Save data to {output_folder_path}')
        logging.info(f'Ingesting data in {output_folder_path}')
        data_to_ingest_df.to_csv(output_folder_path, index=False)

    # Task relationships
    data_to_ingest = get_data_to_ingest_from_local_file()
    save_data(data_to_ingest)


ingest_data_dag = ingest_data()
