# Hi, I am Model Prediction Script Template.
# Please update me in the required places.

# import mlflow
from dotenv import load_dotenv


def predict(model_uri: str):
    load_dotenv()
    print("model URI: ", model_uri)
    # mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
    # model = mlflow.pyfunc.load_model(model_uri)
    print("Model loaded")
    # TODO: Create your data here or get it as an argument.
    # data = ...
    # result = model.predict(data)

    print("Prediction done!")