# Hi, I am the python file that you need to update when you are ready to create
# the dags. This step is usually done
# when you have your code ready in your {{ cookiecutter.package_name }} package.

# NOTE: Please delete all these comments once you have understood how to use

from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

from {{ cookiecutter.package_name }} import preprocess, train

# Define default arguments
# Please change the start date as today (the day you will run this dag for the
# first time) and keep it static.
default_args = {
    "owner": "change_your_name_here",
    "start_date": datetime(2025, 2, 1),
}

# Create the DAG
# Keep `catchup` as false if you would not like to backfill the runs if the
# start_date is in the past.
# To learn more about cron expressions, see here: https://crontab.guru/.
with DAG(
    "change_your_dag_name_here_py_dag",
    default_args=default_args,
    description="change your description here",
    schedule_interval="0 0 * * *",
    catchup=False,
    tags=["python_dag", "{{ cookiecutter.package_name }}"]
) as dag:

    # Define the bash task. If you would like to run bash scripts, use this
    # operator.
    # You can invoke the scripts that you have written in the scripts folder by using:
    # bash_command="${AIRFLOW_HOME}/scripts/your_script"
    change_task_1 = BashOperator(task_id="bash_demo", bash_command="echo 1")

    # Create task group
    with TaskGroup(group_id="change_task_group_23", tooltip="change your task group tooltip") as tg:

        # Define preprocess task. If you would like to run python scripts,
        # use this operator.
        # Please update the python_callable key here to point to your file in
        # your `{{ cookiecutter.package_name }}` package. It is currently set
        # to `preprocess` as an example which is imported above.
        # You can pass parameters as follows to your python callable, if required.
        # op_kwargs={"your_param": "your_value"},
        change_task_2 = PythonOperator(
            task_id="preprocess_task",
            python_callable=preprocess,  # Replace with your actual function
            # op_kwargs={"your_param": "your_value"}
        )

        # Define train task
        # If you would like to run python scripts, use this operator.
        # Please update the python_callable key here to point to your file in
        # your `{{ cookiecutter.package_name }}` package. It is currently set
        # to `train` as an example which is imported above.
        change_task_3 = PythonOperator(
            task_id="train_task",
            python_callable=train  # Replace with your actual function
        )

        # Set dependencies within the task group
        change_task_2 >> change_task_3

    # Set main DAG dependencies
    change_task_1 >> tg
