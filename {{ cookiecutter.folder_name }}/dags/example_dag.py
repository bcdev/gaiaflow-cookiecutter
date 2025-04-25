from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

from {{ cookiecutter.package_name }} import example_preprocess, example_train

default_args = {
    "owner": "add_your_name_here",
    "start_date": datetime(2025, 2, 1),
    "depends_on_past": False,
}

with DAG(
    "add_your_dag_name_here_py_dag",
    default_args=default_args,
    description="add your description here",
    schedule_interval="0 0 * * *",
    catchup=False,
    tags=["python_dag", "{{ cookiecutter.package_name }}"]
) as dag:

    bash_demo = BashOperator(
        task_id="bash_demo",
        bash_command="${AIRFLOW_HOME}/scripts/example_script"
    )

    with TaskGroup(group_id="ml", tooltip="this is a ml task group") as ml_group:

        preprocess_task = PythonOperator(
            task_id="preprocess_task",
            python_callable=example_preprocess,
        )

        train_task = PythonOperator(
            task_id="train_task",
            python_callable=example_train
        )

        preprocess_task >> train_task

    bash_demo >> ml_group
