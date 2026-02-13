# PLEASE DELETE ME AFTER YOU ARE DONE UNDERSTANDING!!

import os

os.environ["KERAS_BACKEND"] = "tensorflow"
import keras


def get_model():
    return keras.Sequential(
        [
            keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(28, 28, 1)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Flatten(),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dense(10, activation="softmax"),
        ]
    )
