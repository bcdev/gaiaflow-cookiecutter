# Hi, I am the python file that you need to update when you are ready to create
# the dags using the task factory. This step is usually done
# when you have your code ready in your {{ cookiecutter.package_name }} package.

# NOTE: Please delete all these comments once you have understood how to use

from datetime import datetime
from airflow import DAG

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from task_factory import task_factory

# Define the environment here. It can either be `dev` or `prod`.
# Currently, the task factory support PythonOperator for dev mode and
# KubernetesPodOperator for prod mode. Usually, most of the use cases should
# be handled by these. If you need something else, you can either use those
# Operators directly from the imports but you would need to take care to make
# sure that they work in both dev and prod environments. If not, you can
# create an issue at https://github.com/bcdev/gaiaflow/issues
ENVIRONMENT = "dev"

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
    "change_your_dag_name_here_task_factory_dag",
    default_args=default_args,
    description="change your description here",
    schedule_interval="0 0 * * *",
    catchup=False,
    tags=["task_factory_dag", "{{ cookiecutter.package_name }}"]
) as dag:

    preprocess_data = task_factory(
        task_id="preprocess_data",
        # TODO: Update this with template name after ECR is created.
        # Please change the version number here to the one that was build
        # manually or will be built by the CI.
        # The docker image name is basically your project name. Please only
        # use this name to create images for your project.
        image="syogesh9/change_me_image:v1",
        # This argument expects the full path to your function that you want
        # to execute.
        func_path="tac.change_me_preprocess",
        # This argument expects tat you provide all the arguments that your
        # function as defined in `func_path` expects.
        func_kwargs={
            "path": "/tmp/iris_output.csv"
        },
        # This decides which operator to use based on the environment.
        # Please keep in mind that when env="dev", the image field is ignored
        # as you are directly testing the package locally which is really
        # fast for testing and development.
        # The image field is only required when you want to run the DAG in
        # production setting.
        env=ENVIRONMENT,
        # do_xcom_push is already enabled by default so that you do not have
        # to send that argument along with every task. If you would like to
        # disable it, uncomment the line below:
        # xcom_push = False

    )

    train = task_factory(
        task_id="train",
        image="syogesh9/change_me_image:v1",
        func_path="tac.example_train",
        env=ENVIRONMENT
    )

    preprocess_data >> train


# TODO:
#  Update ti.xcom code with simple return dict statements.
#  Update the cookiecutter so that it allows using Airflow standalone (without
#  MLOps) for projects requiring only Airflow.
#  Make ECR work. How to add credentials?
#  Make sure task factory works out of the box when new projects are created.
#  Add tests for Airflow dags.
#  Update the documentation stating that we should only return simple objects from the
#  main function that airflow needs to execute.
#  Update documentation providing best practices while working with Docker (
#  cleanup images on registry, local etc.)
#  S3 credentials access?
#  Add sensor based DAGs