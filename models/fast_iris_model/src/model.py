import argparse
import logging
import os
from pathlib import Path
from typing import List

import joblib

from rpc_server import RabbitMQRPCServer

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent


class Singleton(type):
    """
    Singleton metaclass to ensure that only one instance of a class exists at a time.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class IrisModel(metaclass=Singleton):
    """
    Class that loads and uses a KNN model to predict the species of Iris flowers.
    """

    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)

    def predict(self, input_data: List[List[int]]) -> List:
        """
        Makes predictions on the input data using the loaded KNN model.

        Parameters:
            input_data (List[List[int]]): A list of lists containing the input data to predict on.

        Returns:
            A list of integers representing the predicted species of Iris flowers.
        """

        prediction = self.model.predict(input_data)
        prediction = [int(v) for v in prediction]

        return list(prediction)


class IrisRPCServer(RabbitMQRPCServer):
    """
    Class that runs an RPC server to serve the IrisModel object predictions.
    """

    def __init__(self, model_path: str, queue: str):
        super().__init__(queue)
        self.model = IrisModel(model_path)

    def run_process(self, input_data):
        """
        Runs the IrisModel object's predict method on the input data.

        Parameters:
            input_data (List[List[int]]): A list of lists containing the input data to predict on.

        Returns:
            A dictionary containing the prediction or prediction error message.
        """
        try:
            response = self.model.predict(input_data)
            return {"prediction": list(response)}
        except Exception as e:
            return {"prediction_error": e.args}


if __name__ == "__main__":
    """
    Parses command line arguments to specify the name of the queue for the model server,
    creates an instance of the IrisRPCServer class using the specified queue name and the
    path to the model file, and starts the server.

    Args:
        --queue: A string that specifies the name of the queue for the model server.

    Returns:
        None
    """

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--queue", help="name of the queue for the model server")
    # args = parser.parse_args()

    model_path = f"{ROOT_DIR}/assets/iris_knn.joblib"
    server = IrisRPCServer(queue="fast_iris_model_queue", model_path=model_path)
    try:
        server.start()
    except KeyboardInterrupt:
        logging.info(" [x] Stopping RPC server")
        server.stop()
