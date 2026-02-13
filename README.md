# GaiaFlow: MLOps Project Template

[![Unittest Gaiaflow](https://github.com/bcdev/gaiaflow/actions/workflows/unittest.yml/badge.svg)](https://github.com/bcdev/gaiaflow/actions/workflows/unittest.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://bcdev.github.io/gaiaflow/)
![Static Badge](https://img.shields.io/badge/Airflow-3.0-8A2BE2?logo=apacheairflow)
![Static Badge](https://img.shields.io/badge/MLFlow-darkblue?logo=mlflow)
![Static Badge](https://img.shields.io/badge/MinIO-red?logo=minio)
![Static Badge](https://img.shields.io/badge/Jupyter-grey?logo=jupyter)
![Static Badge](https://img.shields.io/badge/Minikube-lightblue?logo=kubernetes)

![Gaiaflow](assets/gaiaflow.png)


<sub>(Image created using ChatGPT)</sub>

The word `GaiaFlow` is a combination of `Gaia` (the Greek goddess of Earth, symbolizing our planet) 
and `Flow` (representing seamless workflows in MLOps). It is an MLOps 
framework tailored for efficient Earth Observation projects. GaiaFlow is built 
to provide you with a framework for the entire pipeline of remote sensing applications, from data 
ingestion to machine learning modeling to deploying them.

It is a comprehensive template for machine learning projects
providing a MLOps framework with tools like `Airflow`, `MLFlow`, 
`JupyterLab`, `Minio` and `Minikube` to allow the user to create ML projects, 
experiments, model deployments and more in an standardized way. The documentation
is available [here](https://bcdev.github.io/gaiaflow/)


The architecture below describes what we want to achieve as our MLOps framework.
This is taken from the [Google Cloud Architecture Centre](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning#mlops_level_2_cicd_pipeline_automation)

[//]: # (Currently what we support is the shown as green ticks.)

[//]: # ()
[//]: # (![Current Local MLOps Architecture]&#40;assets/mlops_arch.png&#41;)

**Please note**: 
This framework has only been tested on Linux Ubuntu and Windows 11 using WSL2 and it works 
as expected.
As we have not tested it yet on MacOS and directly on Windows, we are not sure if it works in there.

# Table of Contents
- [Overview](#overview)
- [Project Structure from this template.](#project-structure-from-this-template)
- [ML Pipeline Overview](#ml-pipeline-overview)
  * [0. Cookiecutter](#0-cookiecutter)
  * [1. Apache Airflow](#1-apache-airflow)
    + [Airflow UI](#airflow-ui)
  * [2. MLflow](#2-mlflow)
    + [MLFlow UI](#mlflow-ui)
  * [3. JupyterLab](#3-jupyterlab)
  * [4. MinIO](#4-minio)
- [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
    + [Docker and Docker compose plugin Installation](#docker-and-docker-compose-plugin-installation)
  * [Installation](#installation)
- [Troubleshooting](#troubleshooting)
- [Acknowledgments](#acknowledgments)

## Overview

This template provides a standardized project structure for ML initiatives at 
BC.

A python package [Gaiaflow](https://pypi.org/project/gaiaflow/) has also been developed for integrating essential MLOps tools:
- **Apache Airflow**: For orchestrating ML pipelines and workflows
- **MLflow**: For experiment tracking and model registry
- **JupyterLab**: For interactive development and experimentation
- **MinIO**: For local object storage for ML artifacts
- **Minikube**: For local lightweight Kubernetes cluster

## Project Structure from this template

You will get the following project when you use this template to get started with
your ML project.

```
├── .github/             # GitHub Actions workflows (you are provided with a starter CI)
├── dags/                # Airflow DAG definitions 
│                          (you can either define dags using a config-file (dag-factory)
│                           or use Python scripts.)
├── notebooks/           # JupyterLab notebooks
├── your_package/         (If you chose pixi as env manager, this will be suffixed by `src/`         
│   │                     (For new projects, it would be good to follow this standardized folder structure.
│   │                      You are of course allowed to add anything you like to it.)
│   ├── dataloader/      # Your Data loading scripts
│   ├── train/           # Your Model training scripts
│   ├── preprocess/      # Your Feature engineering/preprocessing scripts
│   ├── postprocess/     # Your Postprocessing model output scripts
│   ├── model/           # Your Model defintion
│   ├── model_pipeline/  # Your Model Pipeline to be used for inference
│   └── utils/           # Utility functions
├── tests/               # Unit and integration tests
├── data/                # If you have data locally, move it here and use it so that airflow has access to it.
├── README.md            # Its a readme. Feel to change it!
├── CHANGES.md           # You put your changelog for every version here.
├── pyproject.toml       # Config file containing your package's build information and its metadata
├── .env                 # Your environment variables that docker compose and python scripts can use (already added to .gitignore)
├── .gitignore           # Files to ignore when pushing to git.
└── environment.yml      # Libraries required for local mlops and your project (if pixi is used, this will not be present)
```

## Getting Started

Please make sure that you install the following from the links provided as they
have been tried and tested.

If you face any issues, please let us know.

---
### Prerequisites

- [Mamba](https://github.com/conda-forge/miniforge) – Please make sure you install **Python 3.12**, as this repository has been tested with that version.  
 or 
- [Pixi](https://pixi.prefix.dev/latest/installation/) (We recommend using this)
---


#### Verify Installations

Inside your terminal (Linux or WSL2), check:

    mamba         # should print Mamba help page
    or
    pixi          # should print pixi help page

---


Once the pre-requisites are done, you can go ahead with the project creation:

1. Create a separate environment for cookiecutter
```bash
  mamba create -n cc cookiecutter ruamel.yaml 
  mamba activate cc
```

2. Generate the project from template:
```bash
  cookiecutter https://github.com/bcdev/gaiaflow-cookiecutter
```

When prompted for input, enter the details requested. If you dont provide any 
input for a given choice, the first choice from the list is taken as the default.

3. (Optional) - If you wish to use Gaiaflow dockerized MLOps services 
(Airflow, MLFlow, Minio) please follow the steps
[here](https://github.com/bcdev/gaiaflow). Once gaiaflow is installed, 
please read the [user guide](https://bcdev.github.io/gaiaflow/dev_guide/).

> NOTE: The python package currently only works with the conda version of this template, 
pixi version will be released soon.

---

## Acknowledgments

- [Cookiecutter](https://github.com/cookiecutter/cookiecutter)
