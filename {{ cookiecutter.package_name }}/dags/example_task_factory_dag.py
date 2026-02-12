from datetime import datetime

from airflow import DAG
from airflow.utils.task_group import TaskGroup
from gaiaflow.core.create_task import create_task
from gaiaflow.core.operators import FromTask



MODE = "dev" # can be one of ("dev", "dev_docker", "prod_local", "prod")


default_args = {
    "owner": "example_dag_owner",
    "start_date": datetime(2025, 2, 1),
}


with DAG(
    dag_id="create_task_dag_example",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    description="Example Dag",
    catchup=False,
    tags=["create_task", "{{ cookiecutter.package_name }}", MODE]
) as dag:

    with TaskGroup(group_id="Trainer",
                   tooltip="Preprocesses and train Mnist Model") as trainer:
        preprocess_data = create_task(
            task_id="preprocess_data",
            func_path="{{ cookiecutter.package_name }}:example_preprocess",
            func_kwargs={"dummy_arg": "hello world"},

            image="<your-image-name>", # not needed for dev mode
            secrets=["my-minio-creds"],  # not needed for dev mode
            env_vars={
                "SOME_ENV": "42"
            },
            mode=MODE,
            dag=dag,
        )

        train = create_task(
            task_id="train",
            func_path="{{ cookiecutter.package_name }}:example_train",
            func_kwargs={
                "preprocessed_path": FromTask(
                    task="Trainer.preprocess_data", key="preprocessed_path"
                ),
                "bucket_name": FromTask(
                    task="Trainer.preprocess_data", key="bucket_name"
                ),
            },

            image="<your-image-name>", # not needed for dev mode
            secrets=["my-minio-creds"], # not needed for dev mode
            env_vars={
                "SOME_ENV": "42"
            },
            mode=MODE,
            dag=dag,
        )

        preprocess_data >> train
