# Hi, I am Model Prediction Script Template.
# Please update me in the required places.

import mlflow
from dotenv import load_dotenv

def predict(model_uri: str):
    load_dotenv()
    print("model URI: ", model_uri)

    print("Model loaded")
    # TODO: Create your data here or get it as an argument.
    data = ...

    print("Prediction done!")