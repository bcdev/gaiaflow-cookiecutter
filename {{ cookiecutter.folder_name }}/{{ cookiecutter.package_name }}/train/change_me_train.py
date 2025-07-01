# Hi, I am Model Training Script Template.
# Please update me in the required places.
# You can run me as is to see how everything works.
# There are some instructions below that tell you how to use mlflow
# in-conjunction with your code to track your experiments.
# Once you are comfortable, please delete all these comments including me.

from typing import Any

# from {{ cookiecutter.package_name }}.model_pipeline.change_me_model_pipeline import ModelPipelineModel
from {{cookiecutter.package_name}}.dataloader.change_me_data import \
    load_preprocessed_data
from {{cookiecutter.package_name}}.models.change_me_model import get_model

# import mlflow



class Trainer:
    def __init__(self,
                 model: Any,
                 train_data: Any,
                 test_data: Any,
                 hyperparams: Any,
                 trained_model_path: Any
                 ):
        self.model = model
        self.train_data = train_data
        self.test_data = test_data
        self.hyperparams = hyperparams
        self.trained_model_path = trained_model_path

    def train(self):
        """
        Function to train a machine learning model.
        Returns:
            The trained machine learning model.
        """
        print("Training model...")
        # TODO: Implement model training logic with mlflow logging (use
        #  autologging)
        # self.model.fit(self.train_data)
        print("Evaluating model...")
        # TODO: Implement model evaluation logic
        print("Saving model...")
        # TODO: Save model # save model to self.trained_model_path
        # artifact_path = "..."
        # example custom model saving
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

        # code_paths = ["{{ cookiecutter.package_name }}"]
        # mlflow.pyfunc.log_model(
        #     python_model=ModelPipelineModel(self.model),
        #     artifact_path=artifact_path,
        #     # Code paths are required basically to package your
        #     # code along withe model if you have a custom model
        #     # that for e.g. might need a preprocessing script.
        #     # See here for more details:
        #     # https://mlflow.org/docs/latest/model/dependencies.html#id12
        #     code_paths=code_paths,
        #     # sometimes when you deploy and run your model
        #     # inference, you might get errors like Module Not
        #     # found, for those cases, you can specify the
        #     # libraries that your code needs. For e.g.,
        #     # in preprocess script, if you need boto3, you need to
        #     # specify it here.
        #     # You can also specify conda env instead of pip if
        #     # needed.
        #     # This is just an example, if you do not need boto3, feel free to
        #     # remove it.
        #     # See here for more details:
        #     # https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html#mlflow.pyfunc.log_model
        #     extra_pip_requirements=["boto3"]
        # )
        print("Model training and evaluation complete!")
        return "path-to-best-model"


def train(preprocessed_path: str, bucket_name: str):
    # Modify this path to point to the preprocessed data file
    train_data, test_data = load_preprocessed_data(preprocessed_path, bucket_name)
    model = get_model()
    hyperparams = {}
    trained_model_path = "path/to/save/your/model"
    trainer = Trainer(model, train_data, test_data, hyperparams,
                      trained_model_path)
    trainer.train()
    model_uri = trainer.train()
    return {"model_uri": model_uri}
