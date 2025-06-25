import os
import sys
from datetime import datetime

from airflow import DAG
from airflow.utils.task_group import TaskGroup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from task_factory import task_factory

ENVIRONMENT = "dev" # can be one of ("dev", "prod_local", "prod")

# TODO by the user:
#  NOTE: The following is only used when in `prod_local` environment
#  Please run ./prod_local_setup.sh. This will setup a minikube cluster on
#  your machine to run the tasks of this DAG as KubernetesPodOperator which
#  is how it runs in the production Airflow.
#  Please run the function docker_network_gateway() to get
#  the correct Gateway address of the Minikube cluster. It is required if you
#  want to test your DAG in prod_local environment with your local MLOps
#  services running. It is usually  "192.168.49.1".
MINIKUBE_GATEWAY = "<MINIKUBE_GATEWAY_IP>"

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
            task_id="preprocess_data",
            # When you run the ./prod_local_setup.sh as shown above, it will also
            # create a docker image from your package with your environment.yml.
            # Please put the image name below
            image="<your-image-name>",
            func_path="{ cookiecutter.package_name }}.example_preprocess",
            func_kwargs={"dummy_arg": "hello world"},
            secrets=["my-minio-creds"],
            env_vars={
                "S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
                "MLFLOW_SERVER_URI": f"http://{MINIKUBE_GATEWAY}:5000",
                "MLFLOW_S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
            },
            env=ENVIRONMENT,
        )

        train = task_factory(
            task_id="train",
            image="<your-image-name>",
            func_path="{{ cookiecutter.package_name }}.example_train",
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
            secrets=["my-minio-creds"],
            env_vars={
                "S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
                "MLFLOW_SERVER_URI": f"http://{MINIKUBE_GATEWAY}:5000",
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
            xcom_pull_tasks={
                "model_uri": {
                    "task": "Trainer.train",
                    "key": "return_value",
                },
            },
            secrets=["my-minio-creds"],
            env_vars={
                "S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
                "MLFLOW_SERVER_URI": f"http://{MINIKUBE_GATEWAY}:5000",
                "MLFLOW_S3_ENDPOINT_URL": f"http://{MINIKUBE_GATEWAY}:9000",
            },
            env=ENVIRONMENT,
        )

    trainer >> predictor