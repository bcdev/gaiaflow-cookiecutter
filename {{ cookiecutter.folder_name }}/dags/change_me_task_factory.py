# Hi, I am the python file that you need to update when you are ready to create
# the dags using the task factory. This step is usually done
# when you have your package ready in your please_work package.

# NOTE: Please delete all these comments once you have understood how to use me.

import os
import sys
from datetime import datetime

from airflow import DAG
from airflow.utils.task_group import TaskGroup

# Please do not remove the following line.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from task_factory import task_factory

# We use `task_factory`, a wrapper developed at BC on top of Airflow operators, to
# make it easy for users to create DAGs and switch between different environments.
# Currently, only PythonOperator (for dev) and KubernetesPodOperator (KPO) (for prod_local/prod)
# are supported. These operators should cover most cases. You are of course allowed to
# use any other operators as you see fit, but we recommend using task_factory.
# If you need some support for some other operator, you can create an issue at
# https://github.com/bcdev/gaiaflow/issues

# Define the environment here. It can either be `dev`, `prod` or `prod_local`.
ENVIRONMENT = "prod_local"

# TODO (User Action Required):
# Please look for change me's below and update them as needed.

# This DAG can also be run in a `prod_local` environment, which emulates the
# production setup when you are ready to test your DAGs in that env.
# Until then, you can keep working in the `dev` environment which is faster for testing and development.
# Once you are happy with the `dev` environment results, you can
# test your dags in the `prod_local` env.
# Finally, once you are ready to deploy these dags to production airflow, change
# the environment as `prod` and follow these steps TODO: <ADD LINK TO PROD>.
# Please see more here for running DAGs in production.

# Note: This following step below are only necessary for running in the `prod_local` environment.
# To configure your environment properly, please follow these steps:
#
# 1. Run `python minikube_manager.py --start`
#    - This script will provision a Minikube cluster on your local machine.
#    - The cluster is required to run DAG tasks using the KubernetesPodOperator,
#    as in production.
#
# 2. Obtain the correct Minikube gateway address:
#    For Linux users:
#    - Execute the `docker_network_gateway()` function from the mlops package
#    to retrieve the Minikube gateway IP.
#    - This IP is essential for connecting your DAG to local MLOps services
#    during testing.
#    - The gateway is typically `192.168.49.1` in linux, but this may vary by system.
#
#    For Windows users:
#    - The gateway is "host.docker.internal".
#
# 3. Make sure you update `ENVIRONMENT='prod_local'`
# 4. Run `python minikube_manager.py --build-only` to create your docker image that is
# accessible by the Minikube cluster.
MINIKUBE_GATEWAY = "host.docker.internal"


# Define default arguments
# Please change the start date as today (the day you will run this dag for the
# first time) and keep it static.
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
    "change_your_dag_name_here_task_factory_dag",
    default_args=default_args,
    description="change your description here",
    schedule_interval="0 0 * * *",
    catchup=False,
    tags=["task_factory_dag", "please_work"]
) as dag:

    # A task group logically/visually encapsulates a bunch of tasks in it. You don't HAVE to use
    # it, but of course you can.
    with TaskGroup(group_id="change_group_id",
                   tooltip="Change what appears in the tooltip") as trainer:
        preprocess = task_factory(
            # Unique ID of the task. Feel free to change it.
            task_id="preprocess_data",
            # This argument expects the path to your function that you want
            # to execute. It should be available in the  __init__.py of your package.
            func_path="please_work.preprocess",
            # This argument expects that you provide all the arguments that your
            # function as defined in `func_path` expects.
            # If your function depends on another function (from a different task), you should use
            # xcom_pull_tasks instead of func_kwargs as shown in the next task which depends on this one.
            func_kwargs={
                "path": "dummmy_path"
            },

            # # For prod_local and prod mode only
            # You must run the `python minikube_manager.py --build-only`, it will then
            # create a docker image to run your package with all the dependencies included.
            # Please update the image name below:
            # TODO: Talk with Tejas to align on image naming.
            image="my-local-image/my-package:0.0.1",

            # TODO: Discuss with Tejas about a process for creating secrets
            secrets=["my-minio-creds"],

            # The following argument can be used to pass in environment variables that your
            # package might need. In the `dev` mode, you can use the .env file to pass your environment
            # variables.
            env_vars={
                "MLFLOW_TRACKING_URI": f"http://{MINIKUBE_GATEWAY}:5000",
                "MLFLOW_S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
            },

            # Needed for all modes
            # This decides which operator to use based on the environment.
            # Please keep in mind that when env="dev", the image field is ignored
            # as you are directly testing the package locally which is really
            # fast for testing and development.
            # The image field is only required when you want to run the DAG in
            # production (prod) or production-like (prod-like) setting.
            env=ENVIRONMENT,
        )

        train = task_factory(
            task_id="train",
            func_path="please_work.train",
            xcom_pull_tasks={
                "preprocessed_path": {
                    "task": "change_group_id.preprocess_data",
                    "key": "return_value",
                },
                "bucket_name": {
                    "task": "change_group_id.preprocess_data",
                    "key": "return_value"
                },
            },

            image="my-local-image/my-package:0.0.1",
            secrets=["my-minio-creds"],
            env_vars={
                "MLFLOW_TRACKING_URI": f"http://{MINIKUBE_GATEWAY}:5000",
                "MLFLOW_S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
            },

            env=ENVIRONMENT,
        )

        # This bit operator shows the task dependencies.
        preprocess >> train

    with TaskGroup(group_id="change_me_group_id_2",
                   tooltip="Change what appears in the tooltip 2") as predictor:
        predict = task_factory(
            task_id="predict",
            func_path="please_work.predict",
            # Pull model_uri output from the train task
            xcom_pull_tasks={
                "model_uri": {
                    "task": "change_group_id.train",
                    "key": "return_value",
                },
            },
            image="my-local-image/my-package:0.0.1",
            secrets=["my-minio-creds"],
            env_vars={
                "MLFLOW_TRACKING_URI": f"http://{MINIKUBE_GATEWAY}:5000",
                "MLFLOW_S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
            },

            env=ENVIRONMENT,
        )

    trainer >> predictor


# TODO:
#  [DONE] Update ti.xcom code with simple return dict statements.
#  [NOT NEEDED] Update the cookiecutter so that it allows using Airflow standalone (without
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
#  [DONE] Add version.py in package
#  [DONE] Improve change_me_train.py and other files.
#  Make sure dag_factory works in prod env
#  Make CI unittest using conda instead
#  Update CI to use ECR credentials.
#  Run ruff, isort.
#  Update documentation also including, restarting airflow service after env update. now possible using --restart
#  after starting prod, restart airflow containers.
#  on windows, run pytest --ignore=logs and before that run set AIRFLOW_CONFIG=%cd%\airflow_test.cfg