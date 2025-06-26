# Hi, I am Model Training Script Template.
# Please update me in the required places.
# You can run me as is to see how everything works.

import os
import mlflow
from dotenv import load_dotenv

def predict(model_uri: str):
    load_dotenv()
    print("model URI: ", model_uri)
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

    model = mlflow.pyfunc.load_model(model_uri)
    print("Model loaded")
    # TODO: Create your data here or get it as an argument.
    data = ...

    print("Prediction::", model.predict(data))