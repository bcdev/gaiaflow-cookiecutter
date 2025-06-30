# Hi I am a Preprocessing Script Template
# Please update me in the required places.
# You can run me as is to see how everything works.
# Once you are comfortable, please delete all these comments including me.

from typing import Any

from {{ cookiecutter.package_name }}.dataloader.change_me_data import load_raw_data


def clean_data(data: Any):
    """
    Function to clean the dataset.

    Args:
        data: The raw dataset.

    Returns:
        The cleaned dataset.
    """
    print("Cleaning data...")
    # TODO: Implement data cleaning logic
    return data  # Modify this as needed


def feature_engineering(data: Any):
    """
    Function to create or modify features in the dataset.

    Args:
        data: The cleaned dataset.

    Returns:
        The dataset with new features.
    """
    print("Performing feature engineering...")
    # TODO: Implement feature engineering logic
    return data  # Modify this as needed


def save_data(data: Any, path: str):
    """
    Function to create or modify features in the dataset.

    Args:
        data: The cleaned dataset.

    Returns:
        The dataset with new features.
    """
    print("Saving data...")
    # TODO: Implement saving your data to S3 MinIO if you choose MinIO as
    #  your storage backend else save it locally in the data folder.
    print("Saving data successful.")


def preprocess(path: str):
    """
    General preprocessing pipeline. Includes loading, cleaning, and feature engineering.

    Make sure that your function can handle both single` and batch of data if
    you would also like to perform these preprocessing steps before the
    predictions.

    Args:
        path (str): The path to the data file.

    Returns:
        The preprocessed dataset.
    """
    data = load_raw_data(path)
    data = clean_data(data)
    data = feature_engineering(data)
    path = "path/to/store/your/preprocessed/file"
    save_data(data, path)

    print("Preprocessing complete!")
    return {"preprocessed_path": path, 'bucket_name': "my-bucket"}
