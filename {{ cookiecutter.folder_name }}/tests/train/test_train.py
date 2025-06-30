# Hi, I am a test file. Please update me in the required places after you
# have updated your package.

from unittest.mock import MagicMock, patch

import mlflow

from {{ cookiecutter.package_name }}.train.change_me_train import Trainer


def test_trainer_initialization():
    model = MagicMock()

    train_data = ("X_train", "y_train")
    test_data = ("X_test", "y_test")
    hyperparams = {'learning_rate': 0.01}
    model_path = "/tmp/model.pkl"

    trainer = Trainer(model, train_data, test_data, hyperparams, model_path)

    assert trainer.model == model
    assert trainer.train_data == train_data
    assert trainer.test_data == test_data
    assert trainer.hyperparams == hyperparams
    assert trainer.trained_model_path == model_path

@patch('{{ cookiecutter.package_name }}.train.change_me_train.mlflow.pyfunc.log_model')
def test_training_process(mock_log_model):
    model = MagicMock()
    model.fit = MagicMock()
    model.predict = MagicMock(return_value=[0, 1, 0])
    model.score = MagicMock(return_value=0.95)

    train_data = ("X_train", "y_train")
    test_data = ("X_test", "y_test")

    trainer = Trainer(
        model=model,
        train_data=train_data,
        test_data=test_data,
        hyperparams={'epochs': 10},
        trained_model_path="/tmp/model.pkl"
    )

    trainer.train()

    # Enable these assertions once you have them in your code
    # model.fit.assert_called_once_with(("X_train", "y_train"))
    #
    # mock_log_model.assert_called_once()
    # _, kwargs = mock_log_model.call_args
    #
    # assert isinstance(kwargs['python_model'], mlflow.pyfunc.PythonModel)
    # assert 'code_paths' in kwargs
    # assert 'extra_pip_requirements' in kwargs

    # Add specific assertions for your training such as predict assertions,
    # mlflow logging assertions etc.