# PLEASE DELETE ME AFTER YOU ARE DONE UNDERSTANDING!!

import os

import fsspec
import numpy as np
from datetime import datetime

from dotenv import load_dotenv

from {{ cookiecutter.package_name }}.dataloader.example_data_without_minio import load_raw_data


load_dotenv()


def feature_engineering(X: np.ndarray, is_single_input: bool = False):
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
):
    fs = fsspec.filesystem("file")
    fs.makedirs(path, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    save_path = f"{path}/mnist_processed_{timestamp}.npz"
    np.savez_compressed(
        save_path, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )

    print(f"Preprocessed data stored to MinIO: {save_path}")
    return save_path


def preprocess():
    # For training data
    (X_train, y_train), (X_test, y_test) = load_raw_data()

    # Process training data (already in batch form)
    X_train_processed = feature_engineering(X_train, is_single_input=False)
    X_test_processed = feature_engineering(X_test, is_single_input=False)

    # This checks whether you are running this code from an Airflow worker or
    # your local system to make sure we have the right path
    if not os.getenv("AIRFLOW_HOME"):
        path = "../../data/preprocessing/"
    else:
        path = "data/preprocessing/"

    stored_path = save_data(X_train_processed, y_train, X_test_processed, y_test, path)
    print("Preprocessing complete!")
    # Returning a dict would make it available via xcom (
    # cross-communications between tasks) to be picked up by the downstream
    # tasks
    return {"preprocessed_path": stored_path}


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
    preprocess()
