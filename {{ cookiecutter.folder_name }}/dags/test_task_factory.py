from airflow import DAG
from datetime import datetime
from task_factory import task_factory

with DAG(
    dag_id="task_factory_dag_example",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    task = task_factory(
        task_id="process_data",
        # This is a dummy Docker image (but a real one). It contains a
        # package called preprocessing which contains the function process
        # and it expects 3 inputs as arguments as shown below.
        # TODO: Change this to use the package from this repo instead in dev
        #  mode.
        image="syogesh9/test-runner:v1",
        func_path="actual_package.preprocessing.process",
        func_kwargs={
            "data": "iris",
            "transform": "scale_and_rotate",
            "path": "/tmp/iris_output.csv"
        },
        env="prod"
    )