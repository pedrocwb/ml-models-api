import abc
import joblib


class BaseModel:
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)

    @abc.abstractmethod
    def predict(self, input_data: str):
        raise NotImplementedError
