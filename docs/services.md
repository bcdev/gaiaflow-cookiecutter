# Gaiaflow Services

This documentation is designed to provide an in-depth understanding of the services and components used in your system, namely:

- **Apache Airflow** – Workflow orchestration and DAG management.

- **MLflow** – Machine learning experiment tracking and model lifecycle management.

- **MinIO** – High-performance S3-compatible object storage.

- **Custom `Task Factory`** – A unified interface for defining tasks in multiple environments.


## Architecture Overview

The Gaiaflow environment includes the following core services:


| Service         | Description                                                                                |
|-----------------|--------------------------------------------------------------------------------------------| 
| GaiaflowManager | Spins up mlops services for local development                                              |
| MinikubeManager | Spins up local kuberenetes cluster for testing your dags before pushing them to production | 



### GaiaflowManager

| Service | Description                                | Default Port(s)          |
| ------- | ------------------------------------------ | ------------------------ |
| Airflow | DAG orchestration & scheduling platform    | 8080 (Web UI)            |
| MLflow  | ML lifecycle management (tracking, models) | 5000 (UI & API)          |
| MinIO   | Object storage compatible with AWS S3      | 9000 (S3 API), 9001 (UI) |


### MinikubeManager


| Service  | Description                  |       |
|----------|------------------------------| ----------------------- |
| Minikube | Local lightweight Kubernetes |            |


NOTE: These ports work on localhost only when you have started the 
Gaiaflow services using the `GaiaflowManager`

## Apache Airflow

### What is Apache Airflow?
**Apache Airflow** is an open-source platform to programmatically author, schedule, 
and monitor workflows as **DAGs** (Directed Acyclic Graphs). It allows us to 
build scalable, production-grade pipelines with 
clear dependency management, scheduling, retries, and monitoring.

Airflow workflows are defined entirely in Python, allowing dynamic generation 
and tight integration with the Python ecosystem.


### Key Concepts in Airflow

#### DAG (Directed Acyclic Graph)
A DAG is a collection of tasks organized in a structure that reflects their 
execution order. DAGs do not allow for loops, ensuring deterministic scheduling 
and execution.

#### Task
A Task represents a single unit of work within a DAG. Each task is an instance
of an **Operator**.

#### Operator
Operators define the type of work to be done. They are templates that 
encapsulate logic.

Common Operators:

- **PythonOperator**: Executes a Python function.

- **BashOperator**: Executes bash commands.

- **KubernetesPodOperator**: Executes code inside a Kubernetes pod.

- **DummyOperator**: No operation — used for DAG design.

For ease of use of Airflow, we have created a wrapper `task_factory` that 
allows the user to create these tasks without worrying about which operator to
use. Read more [here](#task-factory)

#### Scheduler
The scheduler is responsible for triggering DAG runs based on a schedule. 
It evaluates DAGs, resolves dependencies, and queues tasks for execution.

#### XCom (Cross-Communication)
A lightweight mechanism for passing small data between tasks. Data is stored 
in Airflow’s metadata DB and fetched using Jinja templates or Python.

## MLflow

### What is MLflow?
MLflow is an open-source platform designed to manage the end-to-end machine 
learning lifecycle, including:

- Experiment tracking

- Reproducible runs

- Model packaging

- Deployment

It supports multiple backends and integrates well with popular ML frameworks 
like TensorFlow, PyTorch, Scikit-learn, and more.

### Core Components

#### Tracking
Allows logging of metrics, parameters, artifacts, and models for every 
experiment.

#### Models
MLflow models are saved in a standard format that supports deployment to 
various serving platform.

#### Model Registry
Central hub for managing ML models where one can register and version models.

## MinIO
### What is MinIO?
MinIO is a high-performance, Kubernetes-native object storage system. 
It is fully compatible with the Amazon S3 API, making it ideal for:

- ML/AI artifact storage
- Local development iterations using a portion of the data
- Cloud-native application development

## Task Factory
### Purpose
`task_factory` is a unified task generator that abstracts away the complexity 
of choosing the right Airflow operator depending on the deployment environment 
(dev, prod_local, or prod). Its goal is to:

- Simplify task definitions
- Enable environment switching (`dev`, `prod`, `prod_local`)
- Unify local Python-based execution and Kubernetes-based execution
- Support **XCom pulling**, **secret injection**, and **environment variables**


### Parameters
| Parameter         | Type   | Description                                             |
| ----------------- | ------ |---------------------------------------------------------|
| `task_id`         | `str`  | Unique task identifier in all modes                     |
| `func_path`       | `str`  | Module path to the function (e.g., `my.module:func`)   in all modes  |
| `func_kwargs`     | `dict` | Function arguments   in all modes                                    |
| `image`           | `str`  | Docker image to use in `prod`/`prod_local` mode         |
| `env`             | `str`  | One of `dev`, `prod`, `prod_local`                      |
| `xcom_push`       | `bool` | Whether to push result to XCom  in all modes                         |
| `xcom_pull_tasks` | `dict` | Tasks and keys to pull from XCom  in all modes                       |
| `secrets`         | `list` | Kubernetes secret names in `prod`/`prod_local` mode     |
| `env_vars`        | `dict` | Extra environment variables in `prod`/`prod_local` mode |

### Behavior by Environment:

#### `dev` mode:

- Local development mode.
- Uses PythonOperator.
- Fastest for iteration.
- Only `task_id`, `func_path`, `func_kwargs`, and `env` are used.
- `image`, `secrets`, `env_vars` are ignored.

#### `prod_local` mode:

- Simulates production on your machine using `Minikube` + `KubernetesPodOperator`.
  
- Requires:
   - `image`: Docker image (built locally from your project).
   - `secrets`: For injecting secure credentials (e.g., to connect to MinIO or databases).
   - `env_vars`: Environment-specific config (e.g., MLFLOW and S3 URIs).
   - You must run `MinikubeManager` beforehand

#### `prod` mode:
- Uses `KubernetesPodOperator`
- Production environment in your actual Kubernetes cluster.
- Same requirements as `prod_local`, but deployed to remote infra.

### Use cases for environments:

| Environment  | Use Case                                                                                   |
| ------------ |--------------------------------------------------------------------------------------------|
| `dev`        | Local testing with `PythonOperator` (no Docker or Kubernetes needed)                       |
| `prod_local` | Testing production-like behavior on your machine via Minikube with `KubernetesPodOperator` |
| `prod`       | Fully production environment on Kubernetes  with `KubernetesPodOperator`                    |


### Supported Operators:

| Operator                | Used In              | Purpose                                                          |
| ----------------------- | -------------------- |------------------------------------------------------------------|
| `PythonOperator`        | `dev`                | Runs functions directly in the scheduler                         |
| `KubernetesPodOperator` | `prod_local`, `prod` | Runs tasks in isolated Docker containers via Kubernetes/Minikube |


### secrets
- Used only in `prod_local` and `prod` modes.
- Reference to Kubernetes secrets.
- Passed to `KubernetesPodOperator` to inject secure credentials (e.g., MinIO 
  access keys).
- Defined in your Kubernetes environment (Minikube or production cluster).
- Injected as environment variables using `env_from`. 

### env_vars
- Used only in `prod_local` and `prod` modes.
- Dictionary of environment variables needed at runtime.
- Used to connect to services like:
   - MLflow Tracking Server (`MLFLOW_TRACKING_URI`)
   - MinIO or S3-compatible storage (`MLFLOW_S3_ENDPOINT_URL`)
- In prod_local, these point to your local Minikube (e.g., `192.168.49.1`).
- In prod, they point to production service URLs.

### XCom Support (For all modes)

You can pass results between tasks using `xcom_pull_tasks`, regardless of mode.
It is used to pull data from the output (return_value) of a previous task using 
Airflow’s XCom (Cross-Communication) mechanism.

**NOTE**:
- In `dev`, values are pulled directly from Airflow’s XCom system.
- In `prod`/`prod_local`, values are injected into the pod as environment 
variables using templated Jinja strings and parsed at runtime by your 
application.


#### Structure:

```bash
xcom_pull_tasks={
    "argument_name": {
        "task": "<task_group.task_id>" | "<task_id>",  # Fully qualified task name. include task group if any
        "key": "return_value",  # Optional, defaults to return_value
    },
}
```

- The keys in the dictionary become arguments passed to your function.
- The value is a reference to another task's output (via XCom).
- It works in all modes (dev, prod_local, prod), because task_factory handles 
 the internals.

Example:

```bash
xcom_pull_tasks={
    "preprocessed_path": {
        "task": "Trainer.preprocess_data",
        "key": "return_value"
    }
}
```
This pulls the result of `preprocess_data` from the `Trainer` task group and 
passes it to the function that is invoked in the task.
