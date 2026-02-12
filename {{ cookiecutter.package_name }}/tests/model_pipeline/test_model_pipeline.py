# Hi, I am a test file. Please update me in the required places after you
# have updated your package.

from unittest.mock import MagicMock

from {{cookiecutter.package_name}}.model_pipeline.change_me_model_pipeline import \
    ModelPipelineModel


def test_model_pipeline():
    """Test end-to-end model pipeline execution."""

    # We mock the model here as we want to test the pipeline and not the
    # model itself.
    mock_model = MagicMock(predict=MagicMock(return_value="predictions"))
    test_input = "sample input"

    pipeline = ModelPipelineModel(mock_model)
    result = pipeline.predict(None, test_input)

    mock_model.predict.assert_called_once()
    assert result == "predictions"