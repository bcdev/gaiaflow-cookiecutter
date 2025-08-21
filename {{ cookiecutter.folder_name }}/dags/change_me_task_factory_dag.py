# Hi, I am the python file that you need to update when you are ready to create
# the dags using the task factory. This step is usually done
# when you have your package ready in your `{{ cookiecutter.package_name }}` package.

# NOTE: Please delete all these comments once you have understood how to use me.

from datetime import datetime

from airflow import DAG
from airflow.utils.task_group import TaskGroup
from gaiaflow.core.create_task import create_task
from gaiaflow.core.operators import FromTask

# Define the mode here. It can either be `dev`, `dev_docker`, `prod` or
# `prod_local`.
MODE = "dev"

# Define default arguments
# `start_date` marks the beginning of the very first logical run period, not
# when the DAG will actually start executing
# The DAG won’t schedule at all if start_date is not provided.
# Scheduler needs start_date to compute when to run.
# For manual DAGs, you’d lose scheduling and catchup behavior.
default_args = {
    "owner": "change_your_name_here",
    "start_date": datetime(2025, 2, 1),
}

# Create the DAG
# Keep `catchup` as false if you would not like to backfill the runs if the
# start_date is in the past.
# To learn more about cron expressions, see here: https://crontab.guru/.
with DAG(
    "change_your_dag_name_here_create_task_dag",
    default_args=default_args,
    description="change your description here",
    schedule="0 0 * * *",
    catchup=False,
    tags=["create_task_dag", "{{ cookiecutter.package_name }}", MODE]
) as dag:

    # A task group logically/visually encapsulates a bunch of tasks in it. You don't HAVE to use
    # it, but of course you can.
    with TaskGroup(group_id="change_group_id",
                   tooltip="Change what appears in the tooltip") as trainer:
        preprocess = create_task(
            # Unique ID of the task. Feel free to change it.
            task_id="preprocess_data",
            # This argument expects the path to your function that you want
            # to execute.
            func_path="{{ cookiecutter.package_name }}:preprocess",
            # This argument expects that you provide all the keyword arguments
            # that your function as defined in `func_path` expects.
            # If your function depends on another function (from a different task), you should use
            # FromTask() as shown in the next task which depends on this one.
            # You can also provide `func_args` the same way.
            func_kwargs={
                "path": "dummmy_path"
            },

            # For dev_docker, prod_local and prod mode only
            # You must run the `gaiaflow dev dockerize --help`, and then run
            # that command. It will create a docker image to run your package
            # with all the dependencies included.
            # Please update the image name below:
            image="<your-image-name>",

            # To create secrets for prod_local mode, see `gaiaflow prod-local
            # help`
            # secrets=['<your-secret-name>'],

            # The following argument can be used to pass in environment variables that your
            # package might need. In the `dev` mode, you can use the .env file to pass your environment
            # variables.
            env_vars={
                 "SOME_ENV": "42"
            },

            # Needed for all modes
            # This decides which operator to use based on the environment.
            # Please keep in mind that when env="dev", the image field is ignored
            # as you are directly testing the package locally which is really
            # fast for testing and development.
            # The image field is only required when you want to run the DAG in
            # dev_docker, production (prod) or production-like (prod_local)
            # setting.
            mode=MODE,
            dag=dag,
        )

        train = create_task(
            task_id="train",
            func_path="{{ cookiecutter.package_name }}:train",
            func_kwargs={
                "preprocessed_path": FromTask(
                    task="change_group_id.preprocess_data", key="preprocessed_path"
                ),
                "bucket_name": FromTask(
                    task="change_group_id.preprocess_data", key="bucket_name"
                ),
            },

            # image="<your-image-name>",
            image="gaiaflow_test_pl:v17>",
            # To create secrets for prod_local mode, see gaiaflow
            # prod-local help
            # secrets=['<your-secret-name>'],
            env_vars={
                "SOME_ENV": "42"
            },

            mode=MODE,
            dag=dag,
        )

        # This bit operator shows the task dependencies.
        preprocess >> train

