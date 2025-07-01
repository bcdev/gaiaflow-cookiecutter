# Hi, I am a test file. Please update me in the required places after you
# have updated your package.

from {{cookiecutter.package_name}}.models.change_me_model import get_model


def test_model_creation():
    """Test model factory produces valid models."""
    model = get_model()

    assert model is None # Change this to not None once you define your model

    # Add your model specific assertions here.