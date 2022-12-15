import os
import glob
from datetime import datetime
from datetime import timedelta
# import json
from pathlib import Path
# from dotenv import load_dotenv
# import sendgrid
# from sendgrid.helpers.mail import (
#     Email, Mail, Personalization, Content
# )
# from airflow import AirflowException
from airflow.utils.dates import days_ago
from airflow.decorators import dag, task
from airflow import AirflowException
# add the path to the houseprices package

from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
print("path *************** ")
print(path)
sys.path.insert(0, path)
print(os.path)

from houseprices.inference import make_predictions



DAGS_FOLDER = os.path.join("/c/Users/tingf/airflow", 'dags')
DATA_FOLDER = os.path.join(DAGS_FOLDER, 'data')
VALIDATE_JSON_FOLDER = os.path.join(DAGS_FOLDER, 'suites', 'validation_suite.json')

# print(DATA_FOLDER)
def get_newest_file(folder):
    files = glob.glob(os.path.join(folder, '*.csv'))
    # get the newest file
    newest_file = max(files, key=os.path.getctime)
    return newest_file


def send_request(file):
    import requests
    import logging
    logger = logging.getLogger("console")

    print(file)
    files = {'csv_file':open(file,'rb')}
    response = requests.post(url = f"http://127.0.0.1:8000" + '/multi-predictions', files=files) # post the file to the API is impossible

    # raise AirflowException("Error")
    if response.status_code != 200:
        print(f"response:{response.status_code} - {response.text}")
        raise AirflowException(f"{response.status_code} - {response.text}")
    # logger infos
    logger.info(f"response:{response.status_code} - {response.text}")
    logger.info(f"response: {response.json()}")
    print(f"response:{response.status_code} - {response.text}")
    print(f"response: {response.json()}")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    # 'start_date': datetime(2015, 6, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

@dag(
    dag_id='prediction',
    description='make predictions for new data',
    tags=['dsp', 'preidction'],
    schedule=timedelta(minutes=5),
    # start_date=days_ago(n=0, hour=1)
    start_date = days_ago(1),
    default_args=default_args)

def make_prediction():

    @task(task_id='read_data')
    def read_newest_data():
        """
        Read the data from the new_data folder
        """
        import logging
        import pandas as pd

        logger = logging.getLogger("console")

        newest_file = get_newest_file(os.path.join(DATA_FOLDER, 'new_data'))
        logger.info(f"newest file: {newest_file}")

        df = pd.read_csv(newest_file)

        # put today date in the date column
        # df["date"] = datetime.now().strftime("%Y-%m-%d")
        # df.to_csv(os.path.join(DATA_FOLDER, 'cleaned_data', os.path.basename(newest_file)))

        return df

    @task(task_id='validate_data')
    def validate_data(df):
        """
        Validate the data using great expectations
        """

        import logging
        import great_expectations as ge
        import json

        logger = logging.getLogger("console")
        ge_df = ge.from_pandas(df)
        # Create an expectation suite
        ge_df.expect_column_values_to_be_between(
            column='OverallQual', min_value=0, max_value=10, mostly=0.9)
        ge_df.expect_column_values_to_be_between(
            column='GrLivArea', min_value=0, max_value=1000, mostly=0.9)
        ge_df.expect_column_values_to_be_between(
            column='GarageArea', min_value=0, max_value=10000, mostly=0.9)
        ge_df.expect_column_values_to_be_between(
            column='TotalBsmtSF', min_value=0, max_value=10000, mostly=0.9)
        ge_df.expect_column_values_to_be_in_set(column='Street', value_set=df['Street'].unique())
        ge_df.expect_column_values_to_be_in_set(column='LotShape', value_set=df['LotShape'].unique())


        config = ge_df.get_expectations_config()  # return object type
        #ge_df.save_expectations_config(os.path.join(DAGS_FOLDER, 'suites', 'validation_suite.json'))


        # check info of result
        # logging.info("S************************")
        # logging.info(os.path)
        # logging.info(type(config))
        # logging.info(config)
        # logging.info("E************************")

        # In Python Json Format, the null is not allowed !!!
        null = None

        with open(os.path.join(DAGS_FOLDER, 'suites', 'validation_suite.json'), 'w') as outfile:
           outfile.write(str(config))
        #  save the config to a json file
        config_file = os.path.join(DAGS_FOLDER, 'suites', 'validation_suite.json')
        logger.info(config_file)


        res = ge_df.validate(
            expectation_suite=os.path.join(
                DAGS_FOLDER, 'suites', 'validation_suite.json')
        )
        # res = ge_df.validate(expectations_config=config, catch_exceptions=True) --> not working


        logger.info(f"validation result: {res}")
        newest_file = get_newest_file(os.path.join(DATA_FOLDER, 'new_data'))

        if not res['success']:
            os.rename(newest_file, os.path.join(DATA_FOLDER, 'failed_data', os.path.basename(newest_file)))
            # send_email(f"validation failed:{newest_file}\n Time:{datetime.now()}\n {res['result']}") # to do
            # logger.info(f"validation failed:{df}\n Time:{datetime.now()}\n {res['result']}")
            raise AirflowException(f"Validation failed\n Time:{datetime.now()}\n {res['result']}")
        else:
            os.rename(newest_file, os.path.join(DATA_FOLDER, 'cleaned_data', os.path.basename(newest_file)))
            return res

    @task(task_id = 'make_newest_prediction')
        # multiple_outputs=True
    def make_newest_prediction():
        import logging
        import pandas as pd

        logger = logging.getLogger("console")
        # send_request(newest_file) # python does not support send request within the two ports using same IP address
        # get the newest file in the cleaned_data folder
        newest_file = get_newest_file(os.path.join(DATA_FOLDER, 'cleaned_data'))
        # logger.info(f"newest file: {newest_file}")
        df = pd.read_csv(newest_file)
        logger.info(f"newest file: {df}")
        prediction = make_predictions(df)
        logger.info(f"prediction: {prediction}")
        return prediction


    # @task(task_id = 'make_newest_prediction')
    #     # multiple_outputs=True
    # def make_newest_prediction(df):
    #     import logging

    #     logger = logging.getLogger("console")
    #     # send_request(newest_file) # python does not support send request within the two ports using same IP address
    #     logger.info(f"newest file: {df}")
    #     prediction = make_predictions(df)
    #     logger.info(f"prediction: {prediction}")
    #     return prediction


    df         = read_newest_data()
    validation = validate_data(df)
    pred       = make_newest_prediction(validation)
    # print(pred, validation)
    print(pred)

dag = make_prediction()

# def send_email(content):
#     pass #




