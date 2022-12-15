import os
import glob
from datetime import datetime
from datetime import timedelta
# import json
# from pathlib import Path
# from dotenv import load_dotenv
# import sendgrid
# from sendgrid.helpers.mail import (
#     Email, Mail, Personalization, Content
# )
# from airflow import AirflowException
from airflow.utils.dates import days_ago
from airflow.decorators import dag, task


DAGS_FOLDER = os.path.join("/c/Users/tingf/airflow", 'dags')
DATA_FOLDER = os.path.join(DAGS_FOLDER, 'data')

# print(DATA_FOLDER)
def get_newest_file(folder):
    files = glob.glob(os.path.join(folder, '*.csv'))
    # get the newest file
    newest_file = max(files, key=os.path.getctime)
    return newest_file

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

    @task(
        task_id='read_data'
    )
    def read_data():
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
        df["date"] = datetime.now().strftime("%Y-%m-%d")
        df.to_csv(os.path.join(DATA_FOLDER, 'cleaned_data', os.path.basename(newest_file)))

        return df

    @task(task_id='validate_data')
    def validate_data(df):
        """
        Validate the data using great expectations
        """

        import logging
        import great_expectations as ge
        from airflow import AirflowException

        logger = logging.getLogger("console")

        ge_df = ge.from_pandas(df)

        columns = ["SalePrice", "OverallQual", "GrLivArea",
                   "GarageArea", "TotalBsmtSF", "Street", "LotShape"]

        # OverallQual,GrLivArea,GarageArea,TotalBsmtSF,Street,LotShape
        # 2,120,200,110, Pave, Reg
        # 5,400,220,450, Pave, IR1
        # 3,280,490,300, Pave, Reg
        # 8,330,450,500, Pave, IR1
        # 9,600,730,830, Pave, IR2

        # Create an expectation suite

        # column="GrLivArea", min_value=100, max_value=1000, mostly=0.9,
        # column="GarageArea", min_value=100, max_value=1000, mostly=0.9,
        # column="TotalBsmtSF", min_value=100, max_value=1000, mostly=0.9,)
        # test1 using dict
        res = ge_df.expect_column_values_to_be_between(
            column="OverallQual", min_value=1, max_value=10, mostly=0.9)

        # test2 using list

        logger.info(f"validation result: {res}")

        if not res['success']:
            # send_email(f"validation failed:{newest_file}\n Time:{datetime.now()}\n {res['result']}") # to do
            # logger.info(f"validation failed:{df}\n Time:{datetime.now()}\n {res['result']}")
            # remove the file from new_data folder to failed data folder
            # os.remove(f"{newest_file}.csv")
            # df.to_csv(os.path.join(DATA_FOLDER, 'failed_data', os.path.basename(df)))
            raise AirflowException(f"Validation failed\n Time:{datetime.now()}\n {res['result']}")

        else:
            return res


    @task(
        task_id = 'make_newest_prediction',
        # multiple_outputs=True
    )
    def make_newest_prediction(df):
        import logging

        logger = logging.getLogger("console")

        # Get the newest file
        # newest_file = get_newest_file(os.path.join(DATA_FOLDER, 'cleaned_data'))

        logger.info(f"newest file: {df}")

        # pred = make_request(newest_file)
        pred = None
        return pred

    df         = read_data()
    validation = validate_data(df)
    pred       = make_newest_prediction(df)
    print(pred, validation)

dag = make_prediction()


# def make_request(newest_file):
#     logger = logging.getLogger("console")
#     response = requests.post(
#         "http://localhost:8000",
#         files={'file': open(newest_file, 'rb')}
#     )
#     # raise AirflowException("Error")
#     if response.status_code != 200:
#         raise AirflowException(f"{response.status_code} - {response.text}")
#     # logger infos
#     logger.info(f"response:{response.status_code} - {response.text}")
#     logger.info(f"response: {response.json()}")

# def send_email(content):
#     pass # to do make request to the prediction api



        # df = pd.read_csv(
        #     newest_file,
        #     parse_dates=['date'],
        #     index_col='date'
        # )

        # # Validate the data
        # df = validate_data(df)

        # # Save the data
        # df.to_csv(os.path.join(DATA_FOLDER, 'cleaned_data', 'cleaned_data.csv'))

        # return df


 # ge_df = ge.from_pandas(df)

        # columns = ["SalePrice", "OverallQual", "GrLivArea",
        #            "GarageArea", "TotalBsmtSF", "Street", "LotShape"]
        # OverallQual,GrLivArea,GarageArea,TotalBsmtSF,Street,LotShape
        # 2,120,200,110, Pave, Reg
        # 5,400,220,450, Pave, IR1
        # 3,280,490,300, Pave, Reg
        # 8,330,450,500, Pave, IR1
        # 9,600,730,830, Pave, IR2
        # res = ge_df.expect_column_values_to_be_between(
        #     column="OverallQual", min_value=1, max_value=10, mostly=0.9,
        #     column="GrLivArea", min_value=100, max_value=1000, mostly=0.9,
        #     column="GarageArea", min_value=100, max_value=1000, mostly=0.9,
        #     column="TotalBsmtSF", min_value=100, max_value=1000, mostly=0.9,)
        # logger.info(f"validation result: {res}")
        # res =ge_df.validate(expectation_suite=os.path.join(DAGS_FOLDER,'suites', 'expectation_suite.json'))

        # rasie exception if validation fails



        # logger.info(f"validation result: {res}")

        # Validate the data using the expectation suite

        # res = ge_df.validate(expectation_suite=os.path.join(DAGS_FOLDER, 'suites', 'expectation_suite.json'))

        # rasie exception if validation fails
        # if not res['success']:
        #     # send_email(f"validation failed:{newest_file}\n Time:{datetime.now()}\n {res['result']}") # to do
        #     logger.info(f"validation failed:{newest_file}\n Time:{datetime.now()}\n {res['result']}")
        #     # remove the file from new_data folder to failed data folder
        #     os.remove(f"{newest_file}.csv")
        #     df.to_csv(os.path.join(DATA_FOLDER, 'failed_data', os.path.basename(newest_file)))
        #     raise AirflowException(f"validation failed:{newest_file}\n Time:{datetime.now()}\n {res['result']}")


        # logger.info(f"validation result: {res}")