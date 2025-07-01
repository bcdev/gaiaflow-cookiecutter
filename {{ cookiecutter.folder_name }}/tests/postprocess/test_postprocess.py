# Hi, I am a test file. Please update me in the required places after you
# have updated your package.

from {{cookiecutter.package_name}} import postprocess


def test_postprocess():
    raw_predictions = ...  # Sample model output

    processed = postprocess(raw_predictions)

    assert processed is not None

    # Add your specific assertions here