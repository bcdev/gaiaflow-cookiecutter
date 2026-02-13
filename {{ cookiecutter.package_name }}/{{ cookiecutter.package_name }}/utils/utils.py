import json
from pprint import pprint

import boto3
import mlflow


def get_or_create_experiment(experiment_name: str):
    """
    Retrieve the ID of an existing MLflow experiment or create a new one if it doesn't exist.

    This function checks if an experiment with the given name exists within MLflow.
    If it does, the function returns its ID. If not, it creates a new experiment
    with the provided name and returns its ID.

    Taken from mlflow.org

    Parameters:
    - experiment_name (str): Name of the MLflow experiment.

    Returns:
    - str: ID of the existing or newly created MLflow experiment.
    """
    if experiment := mlflow.get_experiment_by_name(experiment_name):
        return experiment.experiment_id
    else:
        return mlflow.create_experiment(experiment_name)


def get_s3_client(endpoint_url: str, access_key: str, secret_key: str) -> boto3.client:
    """
    Create a boto3 S3 client configured for MinIO
    """
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        verify=False,  # For local MinIO. Set to True for production
    )


def get_latest_data_path(
    s3_client: boto3.client, bucket_name: str, base_folder: str = "preprocessing"
) -> tuple[str, str]:
    """
    Find the latest timestamp folder and NPZ file in the specified bucket/folder
    Returns tuple of (full_path, filename)
    """
    response = s3_client.list_objects_v2(
        Bucket=bucket_name, Prefix=f"{base_folder}/", Delimiter="/"
    )

    timestamps = []
    for prefix in response.get("CommonPrefixes", []):
        folder_name = prefix["Prefix"].strip("/")
        try:
            timestamp = folder_name.replace(f"{base_folder}/", "")
            timestamps.append(timestamp)
        except ValueError:
            continue

    if not timestamps:
        raise ValueError("No timestamp folders found")

    latest_timestamp = sorted(timestamps)[-1]
    latest_folder = f"{base_folder}/{latest_timestamp}"

    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=latest_folder)

    npz_files = [
        obj["Key"]
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".npz")
    ]

    if not npz_files:
        raise ValueError(f"No NPZ files found in {latest_folder}")

    latest_file = npz_files[0]
    return latest_file, latest_file.split("/")[-1]


def show_datasets_info(run_id: str):
    """
    Display readable information about all datasets used in an MLflow run
    """
    run = mlflow.get_run(run_id)
    datasets = run.inputs.dataset_inputs

    print(f"Number of datasets used: {len(datasets)}\n")
    if "data_source" in run.data.params:
        print(f"Data Source: {run.data.params['data_source']}")
    for dataset_input in datasets:
        dataset = dataset_input.dataset
        tags = dataset_input.tags

        info = {
            "Role": tags[0].value,
            "Digest": dataset.digest,
            "Name": dataset.name,
            "Profile": json.loads(dataset.profile),
            "Schema": json.loads(dataset.schema),
            "Source": json.loads(dataset.source),
        }

        print(f"Dataset (Role: {info['Role']}):")
        pprint(info, indent=2, width=100)
        print("\n" + "=" * 80 + "\n")
