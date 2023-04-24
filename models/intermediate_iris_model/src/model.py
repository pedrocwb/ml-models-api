import argparse
import logging
import os
from pathlib import Path
from typing import List

import joblib

from rpc_server import RabbitMQRPCServer

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class IrisModel(metaclass=Singleton):
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)

    def predict(self, input_data: List[List[int]]) -> List:
        prediction = self.model.predict(input_data)
        prediction = [int(v) for v in prediction]

        for i in range(int(1e5)):
            pass

        return list(prediction)


class IrisRPCServer(RabbitMQRPCServer):
    def __init__(self, model_path: str, queue: str):
        super().__init__(queue)
        self.model = IrisModel(model_path)

    def run_process(self, input_data):
        try:
            response = self.model.predict(input_data)
            return {"prediction": list(response)}
        except Exception as e:
            return {"prediction_error": e.args}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", help="name of the queue for the model server")
    args = parser.parse_args()

    model_path = f"{ROOT_DIR}/assets/iris_knn.joblib"
    server = IrisRPCServer(queue=args.queue, model_path=model_path)
    try:
        server.start()
    except KeyboardInterrupt:
        logging.info(" [x] Stopping RPC server")
        server.stop()
