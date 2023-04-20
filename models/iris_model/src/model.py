from typing import List

import joblib


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
        return list(prediction)

