# Tutorials

## MLFlow

[Click here for MLFLow tutorial](assets/mlfow_introduction.ipynb)


## Task Factory

### Airflow DAG Creation with `task_factory`

Welcome! This guide walks you through setting up your DAGs using `task_factory`, a unified task generator that abstracts away the complexity of choosing the right Airflow operator depending on the deployment environment (`dev`, `prod_local`, or `prod`).

This template is primarily intended for Python-based projects and is designed to work seamlessly with Airflow's PythonOperator and KubernetesPodOperator.

---


### Purpose of `task_factory`

`task_factory` is a wrapper developed at BC that:

- Simplifies DAG and task creation
- Lets you switch between environments (dev, prod_local, prod)
- Supports:
  - `xcom` pulling
  - Secret injection
  - Environment variables
- Uses `PythonOperator` in `dev` mode
- Uses `KubernetesPodOperator` in `prod_local` and `prod`

Although you're encouraged to use `task_factory`, you're not restricted from using other Airflow operators—as long as you ensure they work in **both** `dev` and `prod`.


### File Structure Overview

This template assumes you're working in a Python package. 
The key file you'll need to update/create is the DAG file typically located at:

`dags/my_task_factory_dag.py`

### Imports and Setup

```bash
import os
import sys
from datetime import datetime

from airflow import DAG
from airflow.utils.task_group import TaskGroup

# Ensure this path line remains unchanged
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from task_factory import task_factory
```


### Define Your Execution Environment

- **`dev`**: Fast local development (runs tasks as local Python code)
- **`prod_local`**: Mimics production locally using Minikube
- **`prod`**: Production Kubernetes cluster

> You'll need to change the `ENVIRONMENT` variable depending on your current workflow stage.


### DAG Basics

You must define your DAG with a valid start_date, or the scheduler won’t 
trigger it.

```bash
default_args = {
    "owner": "change_your_name_here",
    "start_date": datetime(2025, 2, 1),
}
```

Create your DAG:

```bash
with DAG(
    "your_dag_name_here",
    default_args=default_args,
    description="change your description here",
    schedule_interval="0 0 * * *",
    catchup=False,
    tags=["task_factory_dag", "your_package_name", ENVIRONMENT]
) as dag:
```



### Example tasks created using task_factory


```bash
# A task group logically/visually encapsulates a bunch of tasks in it. You don't HAVE to use
# it, but of course you can.
with TaskGroup(group_id="change_group_id",
               tooltip="Change what appears in the tooltip") as trainer:
    preprocess = task_factory(
        
        # For all modes.
        # Unique ID of the task. Feel free to change it.
        task_id="preprocess_data",
        # This argument expects the path to your function that you want
        # to execute. It should be available in the  __init__.py of your package.
        func_path="your_package.preprocess",
        # This argument expects that you provide all the arguments that your
        # function as defined in `func_path` expects.
        # If your function depends on another function (from a different task), you should use
        # xcom_pull_tasks instead of func_kwargs as shown in the next task which depends on this one.
        func_kwargs={
            "path": "dummmy_path"
        },

        # For prod_local and prod mode only
        # You must run the `python minikube_manager.py --build-only`, it will then
        # create a docker image to run your package with all the dependencies included.
        # Please update the image name below:
        image="my-local-image/my-package:0.0.1",
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
        func_path="{{ cookiecutter.package_name }}.train",
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
```






### Final Steps

> Before releasing this DAG to prod:

- Replace all "change_me" or "dummy" placeholders.
- Delete all instructional comments once you’ve understood their purpose.
- Test your DAG end-to-end in dev.
- Validate it in prod_local.
- Ran tests as described [here](prod.md/#from-local-dags-to-production-ready-workflows)

Now you are [go for prod](prod.md/#go-for-production)