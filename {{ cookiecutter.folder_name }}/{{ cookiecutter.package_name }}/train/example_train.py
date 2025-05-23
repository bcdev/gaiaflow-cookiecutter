# PLEASE DELETE ME AFTER YOU ARE DONE UNDERSTANDING!!

import os
import itertools
from typing import TYPE_CHECKING

import mlflow
import mlflow.tensorflow
import numpy as np
from dotenv import load_dotenv
os.environ["KERAS_BACKEND"] = "tensorflow"
import keras

from {{ cookiecutter.package_name }}.model_pipeline.example_model_pipeline import (
    ModelPipelineModel)
from {{ cookiecutter.package_name }}.utils.utils import (
    get_or_create_experiment
)
from {{ cookiecutter.package_name }}.models.example_model import get_model
from {{ cookiecutter.package_name }}.dataloader.example_data import load_preprocessed_data

if TYPE_CHECKING:
    from airflow.models import TaskInstance

load_dotenv()


class MnistTrainer:
    def __init__(self,
                 model: keras.Sequential,
                 train_data: np.ndarray,
                 test_data: np.ndarray,
                 hyperparams: dict[str, list],
                 trained_model_path: str,
                 s3_data_path: str
                 ):
        self.model = model
        self.train_data = train_data
        self.test_data = test_data
        self.hyperparams = hyperparams
        self.trained_model_path = trained_model_path
        self.s3_data_path = s3_data_path


    def train(self):
        X_train, y_train = self.train_data
        X_test, y_test = self.test_data

        y_train = keras.utils.to_categorical(y_train, 10)
        y_test = keras.utils.to_categorical(y_test, 10)

        mlflow.set_tracking_uri(os.getenv("J_MLFLOW_SERVER_URI"))
        experiment_id = get_or_create_experiment("MNIST_Hyperparameter_Search_autolog")
        mlflow.set_experiment(experiment_id=experiment_id)

        best_accuracy = 0
        best_model = None
        best_params = {}

        keys, values = zip(*self.hyperparams.items())
        param_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        mlflow.autolog()
        with mlflow.start_run(run_name="mnist-hyperparameter-tuning-parent"):
            for params in param_combinations:
                with mlflow.start_run(nested=True):
                    mlflow.log_param(key="data_source", value=self.s3_data_path)

                    optimizer = keras.optimizers.Adam(learning_rate=0.001)
                    self.model.compile(
                        optimizer=optimizer,
                        loss="categorical_crossentropy",
                        metrics=["accuracy"],
                    )
                    history = self.model.fit(
                        X_train,
                        y_train,
                        epochs=params["epochs"],
                        validation_data=(X_test, y_test),
                    )

                    val_acc = history.history["val_accuracy"][-1]

                    if val_acc > best_accuracy:
                        best_accuracy = val_acc
                        best_model = self.model
                        best_params = params

                if best_model is not None:
                    artifact_path = "mnist_model_final"

                    # Here we log our custom model that we created.
                    # It is important that we pass the code_paths argument which
                    # contains your package as mlflow needs to find the code that
                    # it needs to run.
                    # Please make sure that none of the __init__.py files are
                    # completely empty as this creates some issues with
                    # mlflow logging. You can literally just add a # to the
                    # __init__ file. This is needed because while serializing
                    # the files, empty files have 0 bytes of content and that
                    # creates issues with the urllib3 upload to S3 (this
                    # happens inside MLFlow)
                    # The following checks whether you are running this code
                    # from an Airflow worker or your local system to make sure
                    # we have the right path
                    if not os.getenv("AIRFLOW_HOME"):
                        code_paths = ["../../{{ cookiecutter.package_name }}"]
                    else:
                        code_paths = ["{{ cookiecutter.package_name }}"]
                    mlflow.pyfunc.log_model(
                        python_model=ModelPipelineModel(self.model),
                        artifact_path=artifact_path,
                        # Code paths are required basically to package your
                        # code along withe model if you have a custom model
                        # that for e.g. might need a preprocessing script.
                        # See here for more details:
                        # https://mlflow.org/docs/latest/model/dependencies.html#id12
                        code_paths=code_paths,
                        # sometimes when you deploy and run your model
                        # inference, you might get errors like Module Not
                        # found, for those cases, you can specify the
                        # libraries that your code needs. For e.g.,
                        # in preprocess script, I need boto3, so I need to
                        # specify it here.
                        # You can also specify conda env instead of pip if
                        # needed
                        # See here for more details:
                        # https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html#mlflow.pyfunc.log_model
                        extra_pip_requirements=["boto3"]
                    )

                    model_uri = mlflow.get_artifact_uri(artifact_path)

                    print(f"Best model accuracy: {best_accuracy:.4f}")
                    print("Best model params: ", best_params)
                    print("Model stored at ", model_uri)

        print("Training complete. Model logged in MLflow.")


def example_train(preprocessed_path, bucket_name):
    train_data, test_data, s3_data_path = load_preprocessed_data(preprocessed_path,
                                                    bucket_name)
    model = get_model()
    hyperparams = {"epochs": [1, 2]}
    trained_model_path = "mnist_model_final"
    trainer = MnistTrainer(model=model,
                           train_data=train_data,
                           test_data=test_data,
                           hyperparams=hyperparams,
                           trained_model_path=trained_model_path,
                           s3_data_path=s3_data_path)

    trainer.train()

if __name__ == "__main__":
    # If you want to run this locally, please run these commands first:
    # export MLFLOW_TRACKING_URI=http://localhost:5000
    # export MLFLOW_S3_ENDPOINT_URL="http://localhost:9000"
    example_train()