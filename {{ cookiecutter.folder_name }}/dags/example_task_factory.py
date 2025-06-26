import os
import sys
from datetime import datetime

from airflow import DAG
from airflow.utils.task_group import TaskGroup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from task_factory import task_factory

ENVIRONMENT = "dev" # can be one of ("dev", "prod_local", "prod")

# TODO (User Action Required):
# This DAG is intended to run in a `prod_local` environment, which emulates the
# production setup.
#
# To configure your environment properly, please follow these steps:
#
# 1. Run `./prod_local_setup.sh`
#    - This script will provision a Minikube cluster on your local machine.
#    - The cluster is required to run DAG tasks using the KubernetesPodOperator,
#    as in production.
#
# 2. Obtain the correct Minikube gateway address:
#    - Execute the `docker_network_gateway()` function from the mlops package
#    to retrieve the Minikube gateway IP.
#    - This IP is essential for connecting your DAG to local MLOps services
#    during testing.
#    - The gateway is typically `192.168.49.1`, but this may vary by system.
#
# Note: These steps are only necessary for running in the `prod_local` environment.
MINIKUBE_GATEWAY = "<YOUR_MINIKUBE_GATEWAY_IP>"

with DAG(
    dag_id="task_factory_dag_example",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["task_factory", "{{ cookiecutter.package_name }}", ENVIRONMENT]
) as dag:

    with TaskGroup(group_id="Trainer",
                   tooltip="Preprocesses and train Mnist Model") as trainer:
        preprocess_data = task_factory(
            # For all modes
            task_id="preprocess_data",
            func_path="{ cookiecutter.package_name }}.example_preprocess",
            func_kwargs={"dummy_arg": "hello world"},

            # For prod_local and prod mode only
            # When you run the ./prod_local_setup.sh as shown above, it will also
            # create a docker image from your package with your environment.yml.
            # Please put the image name below
            image="<your-image-name>",
            secrets=["my-minio-creds"],
            env_vars={
                "MLFLOW_TRACKING_URI": f"http://{MINIKUBE_GATEWAY}:5000",
                "MLFLOW_S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
            },

            # For all modes
            env=ENVIRONMENT,
        )

        train = task_factory(
            task_id="train",
            func_path="{{ cookiecutter.package_name }}.example_train",
            # Pull outputs from preprocess_data as inputs
            xcom_pull_tasks={
                "preprocessed_path": {
                    "task": "Trainer.preprocess_data",
                    "key": "return_value",
                },
                "bucket_name": {
                    "task": "Trainer.preprocess_data",
                    "key": "return_value"
                },
            },

            image="<your-image-name>",
            secrets=["my-minio-creds"],
            env_vars={
                "MLFLOW_TRACKING_URI": f"http://{MINIKUBE_GATEWAY}:5000",
                "MLFLOW_S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
            },

            env=ENVIRONMENT,
        )

        preprocess_data >> train

    with TaskGroup(group_id="Predictor",
                   tooltip="Predict from Mnist Model") as predictor:
        predict = task_factory(
            task_id="predict",
            func_path="frijun.example_predict",
            # Pull model_uri output from the train task
            xcom_pull_tasks={
                "model_uri": {
                    "task": "Trainer.train",
                    "key": "return_value",
                },
            },

            secrets=["my-minio-creds"],
            env_vars={
                "MLFLOW_TRACKING_URI": f"http://{MINIKUBE_GATEWAY}:5000",
                "MLFLOW_S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
            },

            env=ENVIRONMENT,
        )

    trainer >> predictor