# Hi, I am a test file. Please update me in the required places after you
# have updated your package.

from unittest.mock import patch

from {{cookiecutter.package_name}}.preprocess.change_me_preprocess import (
    clean_data, feature_engineering, preprocess)


def test_clean_data():
    raw_data = "raw_data"  # Create sample raw data
    expected_data = "raw_data"  # Currently it is set to the same value as
    # raw_data because the current implementation just returns the original
    # input

    cleaned_data = clean_data(raw_data)

    assert cleaned_data is not None, "Cleaned data should not be None"
    assert cleaned_data == expected_data

    # Add your specific assertions here


def test_feature_engineering():
    cleaned_data = "cleaned_data"  # Should match clean_data's output

    engineered_data = feature_engineering(cleaned_data)

    assert engineered_data is not None

    # Add your specific assertions here


# Integration test
@patch("{{ cookiecutter.package_name }}.preprocess.change_me_preprocess.load_raw_data")
@patch("{{ cookiecutter.package_name }}.preprocess.change_me_preprocess.clean_data")
@patch("{{ cookiecutter.package_name }}.preprocess.change_me_preprocess.feature_engineering")
@patch("{{ cookiecutter.package_name }}.preprocess.change_me_preprocess.save_data")
def test_preprocess_pipeline(mock_save, mock_feat, mock_clean, mock_load):
    mock_load.return_value = "raw"
    mock_clean.return_value = "cleaned"
    mock_feat.return_value = "engineered"

    result = preprocess("dummy_path")

    assert result is not None
    mock_load.assert_called_once_with("dummy_path")
    mock_clean.assert_called_once_with("raw")
    mock_feat.assert_called_once_with("cleaned")
    mock_save.assert_called_once()