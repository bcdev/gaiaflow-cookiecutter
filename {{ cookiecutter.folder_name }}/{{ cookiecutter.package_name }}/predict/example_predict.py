import os
import mlflow
import numpy as np
from dotenv import load_dotenv

def example_predict(model_uri: str):
    load_dotenv()
    mlflow.set_tracking_uri(os.getenv("MLFLOW_SERVER_URI"))

    model = mlflow.pyfunc.load_model(model_uri)
    print("Model loaded")
    raw_image = np.random.randint(0, 256, (28, 28), dtype=np.uint8)
    preprocessed = raw_image.reshape(28, 28, 1)

    print("Prediction::", model.predict(preprocessed))