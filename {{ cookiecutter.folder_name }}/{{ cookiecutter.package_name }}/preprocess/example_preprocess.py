# PLEASE DELETE ME AFTER YOU ARE DONE UNDERSTANDING!!

import os

import numpy as np
from datetime import datetime

from botocore.exceptions import ClientError
from dotenv import load_dotenv


from {{ cookiecutter.package_name }}.utils.utils import get_s3_client
from {{ cookiecutter.package_name }}.dataloader.example_data import (
    load_raw_data)

load_dotenv()

s3 = get_s3_client(
    endpoint_url=os.getenv("MLFLOW_S3_ENDPOINT_URL"),
    access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def feature_engineering(X: np.ndarray, is_single_input:bool=False):
    """
    Preprocess input data - works for both single samples and batches

    Args:
        X: Input data - can be single image or batch of images
        is_single_input: Boolean indicating if input is a single sample

    Returns:
        Preprocessed data
    """
    # Add batch dimension if single input
    if is_single_input:
        X = np.expand_dims(X, axis=0)

    # Convert to float32 and normalize
    X = X.astype("float32") / 255.0

    # Add channel dimension if not present
    if len(X.shape) == 3:
        X = np.expand_dims(X, axis=-1)

    return X


def save_data(
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        path: str,
        timestamp: str
):
    np.savez_compressed(
        path, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )

    bucket_name = "mnist-data"
    object_path = f"preprocessing/{timestamp}/mnist_processed.npz"

    try:
        s3.head_bucket(Bucket=bucket_name)
    except (NameError, ClientError):
        print(f"Bucket: {bucket_name} does not exist, creating one now!")
        s3.create_bucket(Bucket=bucket_name)

    s3.upload_file(path, bucket_name, object_path)

    os.remove(path)
    print(f"Preprocessed data stored to MinIO: {object_path}")
    return object_path, bucket_name


def example_preprocess():
    # For training data
    (X_train, y_train), (X_test, y_test) = load_raw_data()

    # Process training data (already in batch form)
    X_train_processed = feature_engineering(X_train, is_single_input=False)
    X_test_processed = feature_engineering(X_test, is_single_input=False)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = f"/tmp/mnist_processed_{timestamp}.npz"

    stored_path, bucket_name = save_data(X_train_processed, y_train, X_test_processed,
                           y_test, path,
              timestamp)
    print("Preprocessing complete!")
    # Returning a dict would make it available via xcom (
    # cross-communications between tasks) to be picked up by the downstream
    # tasks
    return {"preprocessed_path": stored_path, "bucket_name": bucket_name}


def preprocess_single_sample(sample: np.ndarray):
    """
    Preprocess a single input sample

    Args:
        sample: Single input image of shape (28, 28)

    Returns:
        Preprocessed sample of shape (1, 28, 28, 1)
    """
    return feature_engineering(sample, is_single_input=True)


def preprocess_batch_samples(samples: np.ndarray):
    """
    Preprocess a batch of input samples

    Args:
        samples: Batch of input images of shape (batch_size, 28, 28)

    Returns:
        Preprocessed batch of shape (batch_size, 28, 28, 1)
    """
    return feature_engineering(samples, is_single_input=False)


if __name__ == "__main__":
    example_preprocess()
