from airflow import DAG
from datetime import datetime

from task_factory import task_factory

ENVIRONMENT = "dev"

with DAG(
    dag_id="task_factory_dag_example",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["task_factory", "{{ cookiecutter.package_name }}"]
) as dag:

    preprocess_data = task_factory(
        task_id="preprocess_data",
        # This is a dummy Docker image (but a real one). It contains a
        # package called preprocessing which contains the function process
        # and it expects 3 inputs as arguments as shown below.
        # TODO: Change this to use the package from this repo instead in dev
        #  mode.
        image="syogesh9/test-runner:v1",
        func_path="tac.example_preprocess",
        func_kwargs={
            "data": "iris",
            "transform": "scale_and_rotate",
            "path": "/tmp/iris_output.csv"
        },
        env=ENVIRONMENT
    )

    train = task_factory(
        task_id="train",
        image="syogesh9/test-runner:v1",
        func_path="tac.example_train",
        func_kwargs={
            "data": "iris",
            "transform": "scale_and_rotate",
            "path": "/tmp/iris_output.csv"
        },
        env=ENVIRONMENT
    )

    preprocess_data >> train