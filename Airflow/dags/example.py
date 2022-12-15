import logging
from datetime import timedelta

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago


import pendulum
@dag(
    dag_id='dsp_example',
    description='DSP Example DAG',
    tags=['dsp'],
    schedule=timedelta(minutes=2),
    start_date=pendulum.today('UTC').add(days=-0,hours=-1)
)
def my_dag_example():
    @task
    def task_1() -> int:
        logging.info('Task one')
        print('OK')
        return 1

    @task
    def task_2(x: int) -> int:
        logging.info(f'{x = }')
        return x + 1

    # Task relationships
    x = task_1()
    y = task_2(x=x)
    print(y)


# Run dag
example_dag = my_dag_example()
