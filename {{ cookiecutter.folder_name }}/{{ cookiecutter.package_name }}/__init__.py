# Package init files are used to bring exports from nested packages up to the
# top level, making them directly accessible from the outermost package layer.

# Also, since we use ruff as the linter and these exports are not used
# anywhere, it throws error when you check for linting. To avoid that,
# we are using the #noqa flag which tell the Ruff compiler to ignore these
# export errors.

from .version import version as __version__
from .train.change_me_train import train  # noqa
from .preprocess.change_me_preprocess import preprocess  # noqa
from .postprocess.change_me_postprocess import postprocess  # noqa
from .predict.change_me_predict import predict  # noqa
{% if cookiecutter.show_examples == "yes" %}
from .train.example_train import example_train  # noqa
from .preprocess.example_preprocess import example_preprocess  # noqa
from .postprocess.example_postprocess import example_postprocess  # noqa
from .predict.example_predict import example_predict  # noqa
{% endif %}

__all__ = [
    "__version__",
    "train",
    "preprocess",
    "postprocess",
    "predict"
]

{% if cookiecutter.show_examples == "yes" %}
__all__ += [
    "example_train",
    "example_preprocess",
    "example_postprocess",
    "example_predict",
]
{% endif %}

